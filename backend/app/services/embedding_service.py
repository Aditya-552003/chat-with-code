"""Embedding service — singleton HuggingFace embedding model."""

from __future__ import annotations

from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from app.config import get_settings
from app.core.logging import logger

_embed_model: HuggingFaceEmbedding | None = None


def get_embedding_model() -> HuggingFaceEmbedding:
    """
    Get or create the singleton embedding model.

    Reuses the same model across requests to avoid reloading weights.
    This preserves the BAAI/bge-small-en model from the original code.
    """
    global _embed_model
    if _embed_model is None:
        settings = get_settings()
        logger.info(f"Loading embedding model: {settings.embedding_model}")
        _embed_model = HuggingFaceEmbedding(model_name=settings.embedding_model)
        logger.info("Embedding model loaded successfully")
    return _embed_model
