"""In-memory conversation management service."""

from __future__ import annotations

import threading
import uuid
from datetime import datetime

from app.api.schemas import (
    Conversation,
    ConversationExport,
    ConversationMessage,
    MessageRole,
    SourceReference,
)
from app.core.logging import logger

# Thread-safe conversation store
_conversations: dict[str, Conversation] = {}
_conv_lock = threading.Lock()


def create_conversation(repository_id: str, conversation_id: str | None = None) -> Conversation:
    """Create a new conversation for a repository."""
    conv_id = conversation_id or str(uuid.uuid4())
    conv = Conversation(
        conversation_id=conv_id,
        repository_id=repository_id,
    )
    with _conv_lock:
        _conversations[conv_id] = conv
    logger.debug(f"Created conversation {conv_id} for repo {repository_id}")
    return conv


def get_conversation(conversation_id: str) -> Conversation | None:
    """Get a conversation by ID."""
    with _conv_lock:
        return _conversations.get(conversation_id)


def get_or_create_conversation(conversation_id: str, repository_id: str) -> Conversation:
    """Get existing conversation or create a new one."""
    conv = get_conversation(conversation_id)
    if conv is None:
        conv = create_conversation(repository_id, conversation_id)
    return conv


def add_message(
    conversation_id: str,
    role: MessageRole,
    content: str,
    sources: list[SourceReference] | None = None,
) -> ConversationMessage:
    """Add a message to a conversation."""
    msg = ConversationMessage(
        role=role,
        content=content,
        sources=sources or [],
    )
    with _conv_lock:
        conv = _conversations.get(conversation_id)
        if conv:
            conv.messages.append(msg)
    return msg


def get_history_for_context(conversation_id: str, max_messages: int = 10) -> list[dict]:
    """Get recent conversation history formatted for LLM context."""
    conv = get_conversation(conversation_id)
    if not conv:
        return []

    recent = conv.messages[-max_messages:]
    return [{"role": m.role.value, "content": m.content} for m in recent]


def clear_conversation(conversation_id: str) -> bool:
    """Clear all messages in a conversation."""
    with _conv_lock:
        conv = _conversations.get(conversation_id)
        if conv:
            conv.messages.clear()
            return True
    return False


def delete_conversation(conversation_id: str) -> bool:
    """Delete a conversation entirely."""
    with _conv_lock:
        return _conversations.pop(conversation_id, None) is not None


def list_conversations(repository_id: str | None = None) -> list[Conversation]:
    """List conversations, optionally filtered by repository."""
    with _conv_lock:
        convs = list(_conversations.values())
    if repository_id:
        convs = [c for c in convs if c.repository_id == repository_id]
    return convs


def export_conversation(conversation_id: str) -> ConversationExport | None:
    """Export a conversation as Markdown."""
    conv = get_conversation(conversation_id)
    if not conv:
        return None

    lines: list[str] = []
    lines.append(f"# Chat with Code — Conversation Export")
    lines.append(f"**Repository:** {conv.repository_id}")
    lines.append(f"**Exported:** {datetime.utcnow().isoformat()}")
    lines.append("")
    lines.append("---")
    lines.append("")

    for msg in conv.messages:
        role_label = "🧑 **User**" if msg.role == MessageRole.USER else "🤖 **Assistant**"
        lines.append(f"### {role_label}")
        lines.append("")
        lines.append(msg.content)
        lines.append("")

        if msg.sources:
            lines.append("<details>")
            lines.append("<summary>Sources</summary>")
            lines.append("")
            for src in msg.sources:
                line_info = ""
                if src.start_line and src.end_line:
                    line_info = f" (L{src.start_line}-L{src.end_line})"
                lines.append(f"- [{src.file_path}{line_info}]({src.github_url})")
            lines.append("")
            lines.append("</details>")
            lines.append("")

        lines.append("---")
        lines.append("")

    return ConversationExport(markdown="\n".join(lines))
