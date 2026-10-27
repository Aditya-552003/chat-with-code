"""Chat endpoints with standard and SSE streaming support."""

from __future__ import annotations

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    MessageRole,
    SourceReference,
)
from app.core.errors import AppError, app_error_to_http
from app.core.logging import logger
from app.services import conversation_service, llm_service
from app.services.indexing_service import get_index

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message and get a complete response with sources.

    Uses the RAG pipeline to retrieve relevant code and generate an answer.
    """
    # Verify index exists
    if get_index(request.repository_id) is None:
        raise HTTPException(
            status_code=409,
            detail=f"Repository '{request.repository_id}' is not indexed. Please load it first.",
        )

    # Get or create conversation
    conv = conversation_service.get_or_create_conversation(
        request.conversation_id, request.repository_id
    )

    # Store user message
    conversation_service.add_message(
        request.conversation_id, MessageRole.USER, request.message
    )

    # Get conversation history for context
    history = conversation_service.get_history_for_context(
        request.conversation_id, max_messages=10
    )
    # Exclude the just-added user message from history context
    history = history[:-1] if history else []

    try:
        answer, sources, retrieval_ms, generation_ms = llm_service.query_repository(
            repository_id=request.repository_id,
            question=request.message,
            conversation_history=history if history else None,
        )
    except AppError as e:
        raise app_error_to_http(e)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate response.")

    # Store assistant message
    conversation_service.add_message(
        request.conversation_id, MessageRole.ASSISTANT, answer, sources
    )

    return ChatResponse(
        conversation_id=request.conversation_id,
        message=answer,
        sources=sources,
        retrieval_time_ms=retrieval_ms,
        generation_time_ms=generation_ms,
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """
    Stream a chat response using Server-Sent Events.

    Events:
    - event: chunk — partial response text
    - event: sources — source citations JSON
    - event: done — stream complete
    - event: error — error occurred
    """
    # Verify index exists
    if get_index(request.repository_id) is None:
        raise HTTPException(
            status_code=409,
            detail=f"Repository '{request.repository_id}' is not indexed.",
        )

    # Get or create conversation
    conversation_service.get_or_create_conversation(
        request.conversation_id, request.repository_id
    )

    # Store user message
    conversation_service.add_message(
        request.conversation_id, MessageRole.USER, request.message
    )

    # Get history
    history = conversation_service.get_history_for_context(
        request.conversation_id, max_messages=10
    )
    history = history[:-1] if history else []

    def generate():
        full_response = ""
        all_sources: list[SourceReference] = []

        try:
            for chunk_text, sources in llm_service.query_repository_stream(
                repository_id=request.repository_id,
                question=request.message,
                conversation_history=history if history else None,
            ):
                if chunk_text:
                    full_response += chunk_text
                    yield f"event: chunk\ndata: {json.dumps({'text': chunk_text})}\n\n"

                if sources is not None:
                    all_sources = sources
                    sources_data = [s.model_dump() for s in sources]
                    yield f"event: sources\ndata: {json.dumps({'sources': sources_data})}\n\n"

            # Store assistant message
            conversation_service.add_message(
                request.conversation_id, MessageRole.ASSISTANT, full_response, all_sources
            )

            yield f"event: done\ndata: {json.dumps({'message': 'complete'})}\n\n"

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)[:300]})}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
