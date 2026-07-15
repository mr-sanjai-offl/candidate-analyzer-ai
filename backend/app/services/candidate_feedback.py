"""Candidate Feedback Engine.

Orchestrates candidate feedback report generation including learning roadmaps,
resume and platform profile improvements suggestions.
"""

import logging
import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.analysis import Analysis
from app.agents.orchestrator import AIOrchestrator
from app.agents.context import ContextBuilder

logger = logging.getLogger(__name__)


class CandidateFeedbackService:
    """Coordinates AI generation of candidate roadmaps and improvement feedback."""

    def __init__(self, orchestrator: AIOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.context_builder = ContextBuilder()

    async def generate_candidate_feedback(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        analysis_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Build context and execute candidate feedback AI orchestration."""
        # Build context variables
        context = await self.context_builder.build_candidate_context(db, candidate_id)

        required_keys = [
            "Learning roadmap",
            "Missing technologies",
            "Recommended certifications",
            "Recommended projects",
            "Weekly roadmap",
            "Monthly roadmap",
            "Interview preparation plan",
            "Resume improvements",
            "GitHub improvements",
            "LeetCode improvements",
        ]

        logger.info("Triggering AI candidate feedback orchestration for candidate %s", candidate_id)
        feedback_payload, usage = await self.orchestrator.execute_task(
            db=db,
            task_name="candidate_feedback",
            variables=context,
            required_keys=required_keys,
        )

        return feedback_payload
