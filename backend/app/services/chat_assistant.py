"""Chat Assistant Service.

Coordinates conversational helpers, loads session history, builds context,
and saves message blocks to chat history databases.
"""

import logging
import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.chat import ChatConversation, ChatMessage
from app.agents.orchestrator import AIOrchestrator
from app.agents.context import ContextBuilder

logger = logging.getLogger(__name__)


class ChatAssistantService:
    """Orchestrates interactive chat sessions with recruiters and candidates."""

    def __init__(self, orchestrator: AIOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.context_builder = ContextBuilder()

    async def get_or_create_session(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        session_id: uuid.UUID | None = None,
    ) -> ChatConversation:
        """Fetch active session or initialize a new chat conversation log."""
        if session_id:
            stmt = select(ChatConversation).where(ChatConversation.id == session_id)
            res = await db.execute(stmt)
            session = res.scalars().first()
            if session:
                return session

        session = ChatConversation(candidate_profile_id=candidate_id, title="QA Session")
        db.add(session)
        await db.flush()
        return session

    async def handle_chat_message(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        session_id: uuid.UUID | None,
        user_message: str,
    ) -> tuple[ChatMessage, ChatMessage]:
        """Process user message, execute AI orchestrator context queries, and save both logs."""
        # 1. Resolve session
        session = await self.get_or_create_session(db, candidate_id, session_id)

        # 2. Save user message
        db_user = ChatMessage(conversation_id=session.id, role="user", content=user_message)
        db.add(db_user)
        await db.flush()

        # 3. Retrieve conversation history (latest 5 logs)
        stmt_hist = (
            select(ChatMessage)
            .where(ChatMessage.conversation_id == session.id)
            .order_by(ChatMessage.created_at.desc())
            .limit(5)
        )
        res_hist = await db.execute(stmt_hist)
        history = list(res_hist.scalars().all())
        history.reverse()

        history_str = "\n".join([f"{msg.role}: {msg.content}" for msg in history[:-1]])

        # 4. Fetch candidate details context
        context = await self.context_builder.build_candidate_context(db, candidate_id)

        variables = {
            "skill_name": user_message, # fallback variable template mapping
            "evidence": str(context.get("evidence", [])),
            "history": history_str,
            "user_query": user_message,
        }

        # 5. Call AI Orchestrator
        logger.info("Executing chat assistant query for candidate %s", candidate_id)
        reply, usage = await self.orchestrator.execute_task(
            db=db,
            task_name="skill_explanation", # uses general explanation template
            variables=variables,
        )

        # 6. Save assistant reply
        db_assistant = ChatMessage(conversation_id=session.id, role="assistant", content=reply)
        db.add(db_assistant)
        await db.commit()

        return db_user, db_assistant
