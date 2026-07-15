"""Job Matching Engine.

Compares candidate capability profiles against Job Descriptions to generate match scores,
missing skills, transferable skills, and roadmaps.
"""

import logging
import uuid
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.job_match import JobMatch
from app.agents.orchestrator import AIOrchestrator
from app.agents.context import ContextBuilder

logger = logging.getLogger(__name__)


class JobMatchingService:
    """Coordinates AI matching analysis of candidates against job descriptions."""

    def __init__(self, orchestrator: AIOrchestrator | None = None) -> None:
        self.orchestrator = orchestrator or AIOrchestrator()
        self.context_builder = ContextBuilder()

    async def match_candidate_to_jd(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        job_title: str,
        job_description: str,
    ) -> dict[str, Any]:
        """Match candidate against target JD text and save results to DB."""
        # 1. Build candidate context
        context = await self.context_builder.build_candidate_context(db, candidate_id)

        # Append JD variables to variables dict
        variables = {
            "job_description": job_description,
            "candidate_profile": f"Skills: {context.get('scores')}\nReadiness: {context.get('readiness')}",
        }

        # 2. Trigger orchestrator matching task
        required_keys = [
            "match_score",
            "missing_skills",
            "transferable_skills",
            "suggested_learning_plan",
        ]

        logger.info("Triggering AI Job Matching assessment for candidate %s", candidate_id)
        match_payload, usage = await self.orchestrator.execute_task(
            db=db,
            task_name="job_matching",
            variables=variables,
            required_keys=required_keys,
        )

        # 3. Normalize payload to dict
        if isinstance(match_payload, str):
            import json as _json
            try:
                match_payload = _json.loads(match_payload)
            except Exception:
                match_payload = {"match_score": 0.0, "raw_response": match_payload}

        # 4. Save matching to DB
        score = float(match_payload.get("match_score", 0.0))
        db_match = JobMatch(
            candidate_profile_id=candidate_id,
            job_title=job_title,
            match_score=score,
            match_data=match_payload,
        )
        db.add(db_match)
        await db.commit()

        logger.info(
            "Job Match analysis completed for candidate %s with score %s",
            candidate_id,
            score,
        )
        return match_payload
