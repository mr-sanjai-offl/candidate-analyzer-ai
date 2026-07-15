"""Chat API Router.

Exposes endpoints for candidate capability QA conversation helper sessions.
"""

import logging
import uuid
from typing import Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.database.models.user import User, UserRole
from app.database.session import get_db_session
from app.services.chat_assistant import ChatAssistantService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Chat Assistant"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class ChatMessageRequest(BaseModel):
    """Schema to send chat message block."""

    candidate_id: uuid.UUID
    session_id: uuid.UUID | None = None
    message: str = Field(..., min_length=1, description="Message text.")


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post(
    "/chat/message",
    status_code=status.HTTP_200_OK,
    summary="Send chat message to assistant",
)
async def send_chat_message(
    body: ChatMessageRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Send user question regarding candidate profile and return assistant reply."""
    service = ChatAssistantService()
    user_msg, assistant_msg = await service.handle_chat_message(
        db=db,
        candidate_id=body.candidate_id,
        session_id=body.session_id,
        user_message=body.message,
    )

    return {
        "session_id": str(assistant_msg.conversation_id),
        "user_message": {
            "id": str(user_msg.id),
            "role": user_msg.role,
            "content": user_msg.content,
            "timestamp": user_msg.created_at.isoformat() if user_msg.created_at else None,
        },
        "reply": {
            "id": str(assistant_msg.id),
            "role": assistant_msg.role,
            "content": assistant_msg.content,
            "timestamp": assistant_msg.created_at.isoformat() if assistant_msg.created_at else None,
        },
    }
