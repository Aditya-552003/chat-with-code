"""Embedding service — singleton Gemini embedding model."""

from __future__ import annotations

from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

from app.config import get_settings
from app.core.logging import logger

_embed_model: GoogleGenAIEmbedding | None = None


def get_embedding_model() -> GoogleGenAIEmbedding:
    """
    Get or create the singleton embedding model.

    Reuses the same model across requests to avoid reloading weights.
    Uses Google Gemini embedding API for ultra-low memory footprint (~50MB vs 800MB).
    """
    global _embed_model
    if _embed_model is None:
        settings = get_settings()
        logger.info(f"Initializing Gemini embedding model: {settings.embedding_model}")
        _embed_model = GoogleGenAIEmbedding(
            model_name=settings.embedding_model,
            api_key=settings.gemini_api_key or None,
        )
        logger.info("Gemini embedding model initialized successfully")
    return _embed_model
