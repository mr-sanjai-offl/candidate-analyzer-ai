"""Search Engine.

Provides database querying and ranking filters to search candidates profiles by skills,
languages, readiness scores, and experience with explainable results rankings.
"""

import logging
from typing import Any, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.candidate_profile import CandidateProfile
from app.database.models.candidate_skill import CandidateSkill
from app.database.models.capability_score import CapabilityScore
from app.database.models.readiness_report import ReadinessReport
from app.database.models.user import User

logger = logging.getLogger(__name__)


class SearchEngineService:
    """Performs explainable, parameterized database queries to rank candidates."""

    async def search_candidates(
        self,
        db: AsyncSession,
        skills: List[str] | None = None,
        min_readiness: float | None = None,
        role: str | None = None,
        min_capability_score: float | None = None,
    ) -> List[dict[str, Any]]:
        """Query and rank candidates profiles based on criteria filters."""
        # 1. Base query selecting candidate profile with eager-loaded user
        stmt = (
            select(CandidateProfile)
            .join(User)
            .options(selectinload(CandidateProfile.user))
            .where(CandidateProfile.deleted_at.is_(None))
        )
        res = await db.execute(stmt)
        candidates = res.scalars().all()

        results = []
        for c in candidates:
            # Fetch capability scores for matching criteria
            stmt_scores = select(CapabilityScore).where(CapabilityScore.candidate_profile_id == c.id)
            res_scores = await db.execute(stmt_scores)
            c_scores = res_scores.scalars().all()

            # Fetch readiness
            stmt_read = select(ReadinessReport).where(ReadinessReport.candidate_profile_id == c.id)
            res_read = await db.execute(stmt_read)
            readiness = res_read.scalars().first()

            # Calculate match criteria and ranking score
            skills_found = [s.category for s in c_scores]
            matching_skills_count = 0
            if skills:
                for target in skills:
                    if any(target.lower() in s.category.lower() or target.lower() in getattr(s, "explanation", {}).get("summary", "").lower() for s in c_scores):
                        matching_skills_count += 1

            # Filter by readiness threshold
            readiness_val = 0.0
            if readiness:
                if role and role.lower() == "backend":
                    readiness_val = readiness.backend_score
                elif role and role.lower() == "frontend":
                    readiness_val = readiness.frontend_score
                else:
                    readiness_val = readiness.backend_score  # Default backend readiness index

            if min_readiness and readiness_val < min_readiness:
                continue

            # Calculate explainable score
            avg_cap = sum(s.experience_score for s in c_scores) / len(c_scores) if c_scores else 0.0
            if min_capability_score and avg_cap < min_capability_score:
                continue

            # Compute rank score: 50% readiness + 30% average capability + 20% skill matches boost
            rank_score = (readiness_val * 0.5) + (avg_cap * 0.3) + (matching_skills_count * 10.0)
            rank_score = min(100.0, rank_score)

            results.append({
                "candidate_id": str(c.id),
                "name": c.user.full_name if c.user else "Anonymous Candidate",
                "ranking_score": round(rank_score, 2),
                "readiness_score": readiness_val,
                "average_capability_score": round(avg_cap, 2),
                "matching_skills_count": matching_skills_count,
                "explanation": f"Ranked {round(rank_score, 1)}% because candidate has a readiness score of {readiness_val}% in target role and matched {matching_skills_count} skills criteria.",
            })

        # Sort results by ranking score descending
        results.sort(key=lambda x: x["ranking_score"], reverse=True)
        return results
