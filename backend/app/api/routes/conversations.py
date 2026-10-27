"""Conversation management endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.api.schemas import Conversation, ConversationExport
from app.services import conversation_service

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str) -> Conversation:
    """Get a conversation with all messages."""
    conv = conversation_service.get_conversation(conversation_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.delete("/{conversation_id}")
async def clear_conversation(conversation_id: str) -> dict:
    """Clear all messages in a conversation."""
    success = conversation_service.clear_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "cleared", "conversation_id": conversation_id}


@router.delete("/{conversation_id}/delete")
async def delete_conversation(conversation_id: str) -> dict:
    """Delete a conversation entirely."""
    success = conversation_service.delete_conversation(conversation_id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "deleted", "conversation_id": conversation_id}


@router.get("/{conversation_id}/export", response_model=ConversationExport)
async def export_conversation(conversation_id: str) -> ConversationExport:
    """Export a conversation as Markdown."""
    export = conversation_service.export_conversation(conversation_id)
    if not export:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return export


@router.get("", response_model=list[Conversation])
async def list_conversations(repository_id: str | None = None) -> list[Conversation]:
    """List conversations, optionally filtered by repository."""
    return conversation_service.list_conversations(repository_id)
