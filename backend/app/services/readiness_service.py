"""Readiness Service.

Computes candidate job role readiness metrics and saves readiness reports.
"""

import logging
import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.capability_score import CapabilityScore
from app.database.models.candidate_skill import CandidateSkill
from app.database.models.readiness_report import ReadinessReport
from app.database.models.evaluation_history import EvaluationHistory
from app.scoring.readiness_engine import ReadinessAssessmentEngine

logger = logging.getLogger(__name__)


class ReadinessService:
    """Service to drive role readiness checks and persist reports."""

    def __init__(self) -> None:
        self.engine = ReadinessAssessmentEngine()

    async def compute_and_persist_readiness(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        extracted_skills: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Assess role-readiness using mathematical engines and write to DB."""
        # 1. Fetch capability scores from database
        stmt_scores = select(CapabilityScore).where(
            CapabilityScore.candidate_profile_id == candidate_id,
            CapabilityScore.deleted_at.is_(None),
        )
        res_scores = await db.execute(stmt_scores)
        db_scores = res_scores.scalars().all()

        category_scores = {
            s.category: {
                "confidence_score": s.confidence_score,
                "experience_score": s.experience_score,
                "depth_score": s.depth_score,
                "breadth_score": s.breadth_score,
            }
            for s in db_scores
        }

        # 2. Compute readiness metrics
        readiness = self.engine.assess_readiness(
            category_scores=category_scores,
            extracted_skills=extracted_skills,
        )

        # 3. Purge existing readiness reports
        await db.execute(
            delete(ReadinessReport).where(ReadinessReport.candidate_profile_id == candidate_id)
        )
        await db.flush()

        # 4. Save report
        db_report = ReadinessReport(
            candidate_profile_id=candidate_id,
            backend_score=readiness.get("Backend", {}).get("score", 0.0),
            frontend_score=readiness.get("Frontend", {}).get("score", 0.0),
            fullstack_score=readiness.get("Full Stack", {}).get("score", 0.0),
            ai_score=readiness.get("AI Engineer", {}).get("score", 0.0),
            data_score=readiness.get("Data Engineer", {}).get("score", 0.0),
            devops_score=readiness.get("DevOps", {}).get("score", 0.0),
            cloud_score=readiness.get("Cloud", {}).get("score", 0.0),
            cybersecurity_score=readiness.get("Cybersecurity", {}).get("score", 0.0),
            embedded_score=readiness.get("Embedded Systems", {}).get("score", 0.0),
            explanation={r: val.get("explanation", {}) for r, val in readiness.items()},
        )
        db.add(db_report)

        # 5. Log history
        history = EvaluationHistory(
            candidate_profile_id=candidate_id,
            action="READINESS_ASSESSMENT",
            metadata_json={"roles_assessed": len(readiness)},
        )
        db.add(history)
        await db.commit()

        logger.info(
            "Readiness report completed and saved for candidate %s", candidate_id
        )

        return readiness
