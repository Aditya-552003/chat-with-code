"""Pydantic request and response schemas for the API."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


# ────────────────────────────────────────────
# Enums
# ────────────────────────────────────────────
class IndexingStatus(str, Enum):
    QUEUED = "queued"
    LOADING = "loading"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# ────────────────────────────────────────────
# Repository
# ────────────────────────────────────────────
class RepositoryLoadRequest(BaseModel):
    repository_url: str = Field(..., description="GitHub repository URL", max_length=500)
    branch: Optional[str] = Field(None, description="Branch name (defaults to repo default branch)")

    @field_validator("repository_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip().rstrip("/")
        if not v.startswith("https://github.com/"):
            raise ValueError("URL must start with https://github.com/")
        return v


class RepositoryInfo(BaseModel):
    repository_id: str
    owner: str
    repo: str
    branch: str
    github_url: str
    status: IndexingStatus
    total_files: int = 0
    indexed_chunks: int = 0
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class IndexingJob(BaseModel):
    job_id: str
    repository_id: str
    status: IndexingStatus
    progress_message: str = ""
    total_files: int = 0
    indexed_chunks: int = 0
    error_message: Optional[str] = None


# ────────────────────────────────────────────
# Chat
# ────────────────────────────────────────────
class SourceReference(BaseModel):
    file_path: str
    language: Optional[str] = None
    snippet: str = ""
    start_line: Optional[int] = None
    end_line: Optional[int] = None
    github_url: str = ""
    relevance_score: Optional[float] = None


class ChatRequest(BaseModel):
    repository_id: str = Field(..., description="Repository session ID")
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message: str = Field(..., description="User question", min_length=1, max_length=5000)


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    sources: list[SourceReference] = []
    retrieval_time_ms: Optional[float] = None
    generation_time_ms: Optional[float] = None


class ChatStreamEvent(BaseModel):
    event: str  # "chunk", "sources", "done", "error"
    data: str = ""
    sources: list[SourceReference] = []


# ────────────────────────────────────────────
# Conversation
# ────────────────────────────────────────────
class ConversationMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    sources: list[SourceReference] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Conversation(BaseModel):
    conversation_id: str
    repository_id: str
    messages: list[ConversationMessage] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ConversationExport(BaseModel):
    markdown: str


# ────────────────────────────────────────────
# Health
# ────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = ""
    gemini_configured: bool = False
    github_configured: bool = False
