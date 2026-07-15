"""Recruiter Report Engine.

Orchestrates context building and AI prompting to generate structured recruitment
evaluations with evidence references.
"""

import logging
import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession


from app.database.models.analysis import Analysis, AnalysisState
from app.agents.orchestrator import AIOrchestrator
from app.agents.context import ContextBuilder

logger = logging.getLogger(__name__)


class RecruiterReportService:
    """Coordinates AI generation of structured candidate evaluation reports for recruiters."""

    def __init__(self, orchestrator: AIOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.context_builder = ContextBuilder()

    async def generate_recruiter_report(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        analysis_id: uuid.UUID,
    ) -> dict[str, Any]:
        """Build context and execute recruiter report AI orchestration. Saves report to DB."""
        # 1. Update analysis state to ANALYZING
        analysis = await db.get(Analysis, analysis_id)
        if not analysis:
            raise ValueError("Analysis record not found.")

        analysis.state = AnalysisState.ANALYZING
        await db.flush()

        # 2. Build detailed context
        context = await self.context_builder.build_candidate_context(db, candidate_id)

        # 3. Request evaluation payload
        required_keys = [
            "Executive Summary",
            "Technical Profile",
            "Strengths",
            "Weaknesses",
            "Risks",
            "Interview Focus Areas",
            "Hiring Recommendation",
            "Confidence Explanation",
            "Evidence References",
        ]

        logger.info("Triggering AI recruiter report orchestration for candidate %s", candidate_id)
        report_payload, usage = await self.orchestrator.execute_task(
            db=db,
            task_name="recruiter_report",
            variables=context,
            required_keys=required_keys,
        )

        # 4. Save to Analysis report data
        analysis.report_data = report_payload
        analysis.overall_score = 80.0  # Mock overall capability score placeholder
        analysis.state = AnalysisState.COMPLETED
        await db.commit()

        logger.info("Recruiter report completed and saved for candidate %s", candidate_id)
        return report_payload

