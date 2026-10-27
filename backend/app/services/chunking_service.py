"""Code chunking service with metadata preservation."""

from __future__ import annotations

import os
from typing import Any

from llama_index.core.schema import Document

from app.services.github_service import build_github_file_url
from app.core.logging import logger


# Language detection by extension
_EXT_TO_LANG: dict[str, str] = {
    ".py": "python", ".pyi": "python",
    ".js": "javascript", ".jsx": "javascript", ".mjs": "javascript", ".cjs": "javascript",
    ".ts": "typescript", ".tsx": "typescript",
    ".java": "java", ".kt": "kotlin",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".hpp": "cpp", ".cc": "cpp",
    ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php",
    ".swift": "swift", ".sh": "bash", ".bash": "bash",
    ".sql": "sql", ".html": "html", ".css": "css", ".scss": "scss",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml",
    ".toml": "toml", ".md": "markdown", ".rst": "restructuredtext",
    ".xml": "xml", ".gradle": "groovy", ".vue": "vue", ".svelte": "svelte",
}


def _detect_language(file_path: str) -> str:
    """Detect programming language from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return _EXT_TO_LANG.get(ext, "text")


def _count_lines(text: str) -> int:
    """Count lines in text."""
    return text.count("\n") + (1 if text and not text.endswith("\n") else 0)


def chunk_documents(
    documents: list[Any],
    owner: str,
    repo: str,
    branch: str,
    repository_id: str,
    chunk_size: int = 1500,
    chunk_overlap: int = 200,
) -> list[Document]:
    """
    Chunk loaded documents with metadata.

    Uses a simple line-based splitting strategy that tries to respect
    natural code boundaries (blank lines, function/class definitions).
    Each chunk retains file path, language, and GitHub URL metadata.
    """
    chunks: list[Document] = []

    for doc in documents:
        file_path = doc.metadata.get("file_path", "unknown")
        language = _detect_language(file_path)
        text = doc.text

        if not text.strip():
            continue

        # For small files, keep as single chunk
        if len(text) <= chunk_size:
            github_url = build_github_file_url(owner, repo, branch, file_path, 1, _count_lines(text))
            chunk_doc = Document(
                text=text,
                metadata={
                    "repository_id": repository_id,
                    "owner": owner,
                    "repo": repo,
                    "branch": branch,
                    "file_path": file_path,
                    "language": language,
                    "start_line": 1,
                    "end_line": _count_lines(text),
                    "github_url": github_url,
                    "chunk_index": 0,
                },
            )
            chunks.append(chunk_doc)
            continue

        # Split larger files by lines with overlap
        lines = text.split("\n")
        total_lines = len(lines)
        # Target lines per chunk (approximate)
        avg_line_length = max(len(text) / max(total_lines, 1), 1)
        lines_per_chunk = max(int(chunk_size / avg_line_length), 20)
        overlap_lines = max(int(chunk_overlap / avg_line_length), 3)

        start = 0
        chunk_index = 0
        while start < total_lines:
            end = min(start + lines_per_chunk, total_lines)

            # Try to break at a natural boundary (blank line or def/class)
            if end < total_lines:
                best_break = end
                for i in range(end, max(end - 15, start), -1):
                    line = lines[i].strip() if i < total_lines else ""
                    if line == "" or line.startswith("def ") or line.startswith("class ") or \
                       line.startswith("function ") or line.startswith("export ") or \
                       line.startswith("public ") or line.startswith("fn ") or \
                       line.startswith("func "):
                        best_break = i
                        break
                end = best_break

            chunk_text = "\n".join(lines[start:end])
            if chunk_text.strip():
                s_line = start + 1
                e_line = end
                github_url = build_github_file_url(owner, repo, branch, file_path, s_line, e_line)

                chunk_doc = Document(
                    text=chunk_text,
                    metadata={
                        "repository_id": repository_id,
                        "owner": owner,
                        "repo": repo,
                        "branch": branch,
                        "file_path": file_path,
                        "language": language,
                        "start_line": s_line,
                        "end_line": e_line,
                        "github_url": github_url,
                        "chunk_index": chunk_index,
                    },
                )
                chunks.append(chunk_doc)
                chunk_index += 1

            start = end - overlap_lines if end < total_lines else total_lines

    logger.info(f"Chunked {len(documents)} documents into {len(chunks)} chunks")
    return chunks
