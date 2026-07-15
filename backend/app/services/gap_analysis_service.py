"""Gap Analysis Service.

Computes missing, weak, and strong skills, prioritized learning tracks, and project recommendations.
"""

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.capability_score import CapabilityScore
from app.database.models.readiness_report import ReadinessReport
from app.database.models.candidate_skill import CandidateSkill
from app.database.models.evaluation_history import EvaluationHistory
from app.scoring.gap_analysis_engine import GapAnalysisEngine

logger = logging.getLogger(__name__)


class GapAnalysisService:
    """Service to coordinate gap analyses and suggest technical roads."""

    def __init__(self) -> None:
        self.engine = GapAnalysisEngine()

    async def generate_gap_analysis(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        extracted_skills: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Assess gaps between candidate tech stack and standard roles profiles."""
        # 1. Fetch capability scores from DB
        stmt_scores = select(CapabilityScore).where(
            CapabilityScore.candidate_profile_id == candidate_id,
            CapabilityScore.deleted_at.is_(None),
        )
        res_scores = await db.execute(stmt_scores)
        db_scores = res_scores.scalars().all()
        category_scores = {s.category: {"experience_score": s.experience_score} for s in db_scores}

        # 2. Fetch readiness reports from DB
        stmt_readiness = select(ReadinessReport).where(
            ReadinessReport.candidate_profile_id == candidate_id,
            ReadinessReport.deleted_at.is_(None),
        )
        res_readiness = await db.execute(stmt_readiness)
        report = res_readiness.scalars().first()
        
        readiness_reports = {}
        if report:
            readiness_reports = {
                "Backend": {"score": report.backend_score},
                "Frontend": {"score": report.frontend_score},
                "Full Stack": {"score": report.fullstack_score},
                "AI Engineer": {"score": report.ai_score},
                "Data Engineer": {"score": report.data_score},
                "DevOps": {"score": report.devops_score},
                "Cloud": {"score": report.cloud_score},
                "Cybersecurity": {"score": report.cybersecurity_score},
                "Embedded Systems": {"score": report.embedded_score},
            }

        # 3. Compute gaps
        gap_results = self.engine.compute_gap_analysis(
            category_scores=category_scores,
            extracted_skills=extracted_skills,
            readiness_reports=readiness_reports,
        )

        # 4. Save audit log
        history = EvaluationHistory(
            candidate_profile_id=candidate_id,
            action="GAP_ANALYSIS",
            metadata_json={
                "target_role": gap_results["target_role"],
                "missing_skills_count": len(gap_results["missing_skills"]),
                "strong_skills_count": len(gap_results["strong_skills"]),
            },
        )
        db.add(history)
        await db.commit()

        logger.info(
            "Gap analysis completed for candidate %s against track: %s",
            candidate_id,
            gap_results["target_role"],
        )

        return gap_results
