"""Application configuration loaded from environment variables."""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # --- API Keys ---
    gemini_api_key: str = Field(default="", description="Google Gemini API key")
    github_token: str = Field(default="", description="GitHub personal access token (optional for public repos)")

    # --- Model Configuration ---
    gemini_model: str = Field(default="gemini-2.5-flash", description="Gemini model name")
    embedding_model: str = Field(default="gemini-embedding-001", description="Gemini embedding model")
    embedding_dimensions: int = Field(default=3072, description="Embedding vector dimensions for Gemini")

    # --- Retrieval ---
    retrieval_top_k: int = Field(default=8, description="Number of chunks to retrieve")
    max_context_chunks: int = Field(default=6, description="Max chunks sent to LLM context")

    # --- LLM Generation ---
    temperature: float = Field(default=0.1, description="LLM temperature")
    max_response_tokens: int = Field(default=4096, description="Maximum response tokens")

    # --- Repository ---
    max_file_size_bytes: int = Field(default=500_000, description="Max file size in bytes to index")
    max_files_per_repo: int = Field(default=500, description="Max files to index per repository")
    vector_store_path: str = Field(default="./vector_stores", description="Path for persisted vector indexes")
    concurrent_github_requests: int = Field(default=5, description="Concurrent GitHub API requests")

    # --- Server ---
    frontend_origin: str = Field(default="http://localhost:5173", description="Allowed frontend origin for CORS")
    log_level: str = Field(default="INFO", description="Logging level")
    port: int = Field(default=8000, description="Server port")
    app_version: str = Field(default="2.0.0", description="Application version")

    # --- Conversation ---
    max_history_messages: int = Field(default=10, description="Max previous messages included in context")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
