"""Indexing service — manages FAISS vector indexes per repository."""

from __future__ import annotations

import threading
from typing import Any

from llama_index.core import Settings as LlamaSettings, VectorStoreIndex

from app.services.embedding_service import get_embedding_model
from app.core.logging import logger

# Thread-safe index store: repository_id -> VectorStoreIndex
_indexes: dict[str, VectorStoreIndex] = {}
_index_lock = threading.Lock()

# Metadata store: repository_id -> metadata dict
_index_metadata: dict[str, dict] = {}


def build_index(repository_id: str, chunks: list[Any]) -> VectorStoreIndex:
    """
    Build a VectorStoreIndex from chunked documents.

    Preserves the VectorStoreIndex.from_documents approach from the original code,
    but uses the singleton embedding model and stores by repository_id.
    """
    embed_model = get_embedding_model()

    # Set the embedding model for this indexing operation
    LlamaSettings.embed_model = embed_model

    logger.info(f"Building vector index for {repository_id} with {len(chunks)} chunks")
    index = VectorStoreIndex.from_documents(chunks)
    logger.info(f"Index built for {repository_id}")

    with _index_lock:
        _indexes[repository_id] = index

    return index


def get_index(repository_id: str) -> VectorStoreIndex | None:
    """Get a previously built index for a repository."""
    with _index_lock:
        return _indexes.get(repository_id)


def remove_index(repository_id: str) -> None:
    """Remove an index from the store."""
    with _index_lock:
        _indexes.pop(repository_id, None)
        _index_metadata.pop(repository_id, None)


def store_index_metadata(repository_id: str, metadata: dict) -> None:
    """Store metadata about an index."""
    with _index_lock:
        _index_metadata[repository_id] = metadata


def get_index_metadata(repository_id: str) -> dict | None:
    """Get metadata about an index."""
    with _index_lock:
        return _index_metadata.get(repository_id)


def list_indexes() -> list[str]:
    """List all indexed repository IDs."""
    with _index_lock:
        return list(_indexes.keys())
