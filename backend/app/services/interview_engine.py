"""Interview Generation Engine.

Generates tailored interview questions in Backend, DevOps, DSA etc. at Easy, Medium,
and Hard levels based on candidate evidence.
"""

import logging
import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import AIOrchestrator
from app.agents.context import ContextBuilder

logger = logging.getLogger(__name__)


class InterviewEngineService:
    """Generates tailored interview questions based on candidate capabilities."""

    def __init__(self, orchestrator: AIOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.context_builder = ContextBuilder()

    async def generate_questions_for_candidate(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        categories: list[str],
        difficulties: list[str],
    ) -> list[dict[str, Any]]:
        """Generate targeted technical and behavioral interview questions based on verified tech skills."""
        # Build context
        context = await self.context_builder.build_candidate_context(db, candidate_id)

        variables = {
            "topics": ", ".join(categories),
            "skills": context.get("scores"),
        }

        logger.info("Triggering AI Interview Questions generation for candidate %s", candidate_id)
        questions, usage = await self.orchestrator.execute_task(
            db=db,
            task_name="interview_generation",
            variables=variables,
        )

        # Parse JSON output from orchestrator if it is a string representation of a list of questions
        import json
        try:
            parsed = json.loads(questions)
            if isinstance(parsed, list):
                return parsed
        except Exception:
            logger.warning("Could not parse generated questions, using default fallbacks.")

        # Fallback dynamic mock generation if LLM did not return valid JSON format
        fallback_questions = []
        for cat in categories:
            for diff in difficulties:
                fallback_questions.append({
                    "category": cat,
                    "question": f"Based on your profile, explain your experience using standard tools in {cat} ({diff} level).",
                    "difficulty": diff,
                })
        return fallback_questions
