"""Chat Assistant database models.

Stores conversational assistant logs between recruiters/candidates and the AI.
"""

import uuid
from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ChatConversation(Base):
    """A chat session containing multiple messages."""

    __tablename__ = "chat_conversations"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this conversation is about.",
    )
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="New Session",
    )


class ChatMessage(Base):
    """An individual message inside a conversation."""

    __tablename__ = "chat_messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chat_conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="user or assistant",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
