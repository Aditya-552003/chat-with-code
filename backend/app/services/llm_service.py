"""LLM service for query execution with source attribution."""

from __future__ import annotations

import time
from typing import Any, Generator

from llama_index.core import Settings as LlamaSettings, PromptTemplate
from llama_index.llms.google_genai import GoogleGenAI

from app.api.schemas import SourceReference
from app.config import get_settings
from app.services.embedding_service import get_embedding_model
from app.services.indexing_service import get_index
from app.core.errors import GeminiAPIError, IndexNotReadyError
from app.core.logging import logger


# Singleton LLM instance
_llm: GoogleGenAI | None = None


def _get_llm() -> GoogleGenAI:
    """Get or create the singleton Gemini LLM."""
    global _llm
    if _llm is None:
        settings = get_settings()
        logger.info(f"Initializing Gemini LLM: {settings.gemini_model}")
        _llm = GoogleGenAI(
            model=settings.gemini_model,
            temperature=settings.temperature,
        )
    return _llm


# System prompt template for code Q&A
_QA_PROMPT = PromptTemplate(
    "You are an expert code analysis assistant. You help developers understand codebases "
    "by providing accurate, detailed answers based on the repository source code.\n\n"
    "INSTRUCTIONS:\n"
    "- Answer the question using ONLY the provided source code context.\n"
    "- When referencing code, mention the file path.\n"
    "- If the context is insufficient, clearly state what information is missing.\n"
    "- Do NOT fabricate file names, function names, or code that isn't in the context.\n"
    "- Use code examples from the actual source when helpful.\n"
    "- Be precise about what the code does vs. what you're assuming.\n"
    "- Format your response with Markdown for readability.\n\n"
    "REPOSITORY CONTEXT:\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n\n"
    "QUESTION: {query_str}\n\n"
    "ANSWER:"
)


def _extract_sources(source_nodes: list[Any]) -> list[SourceReference]:
    """Extract source citations from retrieval nodes."""
    sources: list[SourceReference] = []
    seen_paths: set[str] = set()

    for node in source_nodes:
        metadata = node.metadata if hasattr(node, "metadata") else {}
        # Handle NodeWithScore wrapper
        if hasattr(node, "node"):
            metadata = node.node.metadata if hasattr(node.node, "metadata") else {}

        file_path = metadata.get("file_path", "")
        if not file_path:
            continue

        # Deduplicate by file_path + chunk range
        chunk_key = f"{file_path}:{metadata.get('start_line', '')}:{metadata.get('end_line', '')}"
        if chunk_key in seen_paths:
            continue
        seen_paths.add(chunk_key)

        # Extract snippet (first ~10 lines of the chunk)
        text = ""
        if hasattr(node, "node") and hasattr(node.node, "text"):
            text = node.node.text
        elif hasattr(node, "text"):
            text = node.text

        snippet_lines = text.split("\n")[:10]
        snippet = "\n".join(snippet_lines)
        if len(snippet_lines) < text.count("\n"):
            snippet += "\n..."

        score = None
        if hasattr(node, "score"):
            score = round(float(node.score), 4) if node.score is not None else None

        sources.append(SourceReference(
            file_path=file_path,
            language=metadata.get("language"),
            snippet=snippet,
            start_line=metadata.get("start_line"),
            end_line=metadata.get("end_line"),
            github_url=metadata.get("github_url", ""),
            relevance_score=score,
        ))

    return sources


def query_repository(
    repository_id: str,
    question: str,
    conversation_history: list[dict] | None = None,
) -> tuple[str, list[SourceReference], float, float]:
    """
    Query the repository index with a question.

    Returns (answer_text, sources, retrieval_ms, generation_ms).
    Preserves and improves the RAG pipeline from the original main.py.
    """
    settings = get_settings()

    index = get_index(repository_id)
    if index is None:
        raise IndexNotReadyError(repository_id)

    llm = _get_llm()
    embed_model = get_embedding_model()

    # Set models for this query
    LlamaSettings.llm = llm
    LlamaSettings.embed_model = embed_model

    # Build query engine (preserving similarity_top_k from original)
    query_engine = index.as_query_engine(
        similarity_top_k=settings.retrieval_top_k,
        streaming=False,
    )

    # Update prompt template
    query_engine.update_prompts({
        "response_synthesizer:text_qa_template": _QA_PROMPT,
    })

    # Build context-enriched query if conversation history exists
    enriched_query = question
    if conversation_history:
        # Include last few messages for context
        recent = conversation_history[-settings.max_history_messages:]
        history_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:500]}"
            for m in recent
        )
        enriched_query = f"Previous conversation:\n{history_text}\n\nCurrent question: {question}"

    try:
        # Retrieval phase
        t0 = time.time()
        response = query_engine.query(enriched_query)
        t1 = time.time()

        # Extract sources from response
        source_nodes = response.source_nodes if hasattr(response, "source_nodes") else []
        sources = _extract_sources(source_nodes)

        retrieval_ms = round((t1 - t0) * 1000, 1)
        generation_ms = 0.0  # LlamaIndex combines retrieval and generation

        answer = str(response)

        return answer, sources, retrieval_ms, generation_ms

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Query error for {repository_id}: {error_msg}")
        if "quota" in error_msg.lower() or "rate" in error_msg.lower():
            raise GeminiAPIError("API rate limit or quota exceeded. Please try again later.")
        if "api key" in error_msg.lower() or "authentication" in error_msg.lower():
            raise GeminiAPIError("Invalid or missing Gemini API key.")
        raise GeminiAPIError(f"Failed to generate response: {error_msg[:200]}")


def query_repository_stream(
    repository_id: str,
    question: str,
    conversation_history: list[dict] | None = None,
) -> Generator[tuple[str, list[SourceReference] | None], None, None]:
    """
    Stream a query response from the repository index.

    Yields (chunk_text, sources_or_None) tuples.
    Sources are yielded once after the final chunk.
    """
    settings = get_settings()

    index = get_index(repository_id)
    if index is None:
        raise IndexNotReadyError(repository_id)

    llm = _get_llm()
    embed_model = get_embedding_model()

    LlamaSettings.llm = llm
    LlamaSettings.embed_model = embed_model

    query_engine = index.as_query_engine(
        similarity_top_k=settings.retrieval_top_k,
        streaming=True,
    )

    query_engine.update_prompts({
        "response_synthesizer:text_qa_template": _QA_PROMPT,
    })

    # Build enriched query
    enriched_query = question
    if conversation_history:
        recent = conversation_history[-settings.max_history_messages:]
        history_text = "\n".join(
            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content'][:500]}"
            for m in recent
        )
        enriched_query = f"Previous conversation:\n{history_text}\n\nCurrent question: {question}"

    try:
        response = query_engine.query(enriched_query)

        # Extract sources first
        source_nodes = response.source_nodes if hasattr(response, "source_nodes") else []
        sources = _extract_sources(source_nodes)

        # Stream response text
        if hasattr(response, "response_gen"):
            for chunk in response.response_gen:
                yield chunk, None
        else:
            # Fallback for non-streaming response
            yield str(response), None

        # Yield sources at the end
        yield "", sources

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Stream query error for {repository_id}: {error_msg}")
        raise GeminiAPIError(f"Failed to generate response: {error_msg[:200]}")
