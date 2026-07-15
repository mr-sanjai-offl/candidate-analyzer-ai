"""Capability Scoring Service.

Computes candidate category scores based on evidence databases and registers them.
"""

import logging
import uuid
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.enums import PlatformType
from app.database.models.github_profile import GithubProfile
from app.database.models.leetcode_profile import LeetCodeProfile
from app.database.models.codeforces_profile import CodeforcesProfile
from app.database.models.evidence import Evidence
from app.database.models.capability_score import CapabilityScore
from app.database.models.evaluation_history import EvaluationHistory
from app.scoring.scoring_engine import CapabilityScoringEngine

logger = logging.getLogger(__name__)


class CapabilityScoringService:
    """Service to coordinate metric scoring and persist capability results."""

    def __init__(self) -> None:
        self.engine = CapabilityScoringEngine()

    async def compute_and_persist_scores(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        extracted_skills: dict[str, dict[str, Any]],
    ) -> dict[str, dict[str, Any]]:
        """Calculate score metrics using deterministic formulas and save to DB."""
        # 1. Fetch profile metrics from database for context
        github_profile = await self._fetch_github_metrics(db, candidate_id)
        leetcode_profile = await self._fetch_leetcode_metrics(db, candidate_id)
        codeforces_profile = await self._fetch_codeforces_metrics(db, candidate_id)

        # 2. Query all evidence logs to reconstruct weights and lists
        stmt_ev = select(Evidence).where(
            Evidence.candidate_profile_id == candidate_id,
            Evidence.deleted_at.is_(None),
        )
        res_ev = await db.execute(stmt_ev)
        evidences = res_ev.scalars().all()

        # Re-populate extracted skills dict with persisted evidence details
        for skill_name, info in extracted_skills.items():
            skill_evs = [
                {
                    "source": ev.source,
                    "weight": ev.weight,
                    "confidence": ev.confidence,
                    "evidence": ev.evidence_text,
                    "verification_state": ev.verification_state,
                }
                for ev in evidences
                if ev.skill.name.lower() == skill_name.lower()
            ]
            info["evidences"] = skill_evs

        # 3. Calculate scores
        scores = self.engine.compute_category_scores(
            extracted_skills=extracted_skills,
            github_metrics=github_profile,
            leetcode_metrics=leetcode_profile,
            codeforces_metrics=codeforces_profile,
        )

        # 4. Purge existing scores
        await db.execute(
            delete(CapabilityScore).where(CapabilityScore.candidate_profile_id == candidate_id)
        )
        await db.flush()

        # 5. Persist scores
        for category, info in scores.items():
            db_score = CapabilityScore(
                candidate_profile_id=candidate_id,
                category=category,
                confidence_score=info["confidence_score"],
                experience_score=info["experience_score"],
                depth_score=info["depth_score"],
                breadth_score=info["breadth_score"],
                proficiency=info["proficiency"],
                explanation=info["explanation"],
            )
            db.add(db_score)

        # 6. Log history run
        history = EvaluationHistory(
            candidate_profile_id=candidate_id,
            action="SCORING",
            metadata_json={"categories_scored": len(scores)},
        )
        db.add(history)
        await db.commit()

        logger.info(
            "Capability scores calculated and persisted for candidate %s (%d categories)",
            candidate_id,
            len(scores),
        )

        return scores

    # ── Platform queries helpers ──────────────────────────────────────

    async def _fetch_github_metrics(self, db: AsyncSession, candidate_id: uuid.UUID) -> dict[str, Any] | None:
        stmt = select(GithubProfile).where(
            GithubProfile.candidate_profile_id == candidate_id,
            GithubProfile.deleted_at.is_(None),
        )
        res = await db.execute(stmt)
        profile = res.scalars().first()
        if not profile:
            return None

        # Fetch projects list
        from app.database.models.project import Project
        stmt_proj = select(Project).where(
            Project.candidate_profile_id == candidate_id,
            Project.deleted_at.is_(None),
        )
        res_proj = await db.execute(stmt_proj)
        projects = res_proj.scalars().all()

        return {
            "public_repos": profile.repositories_count,
            "followers": profile.followers,
            "total_contributions": profile.stars_received,
            "contribution_consistency": 0.8,  # Default fallback
            "projects": [
                {
                    "name": p.name,
                    "primary_language": p.url.split("/")[-1] if p.url else "Python", # mock fallback
                    "languages": [],
                    "stars": 2,
                }
                for p in projects
            ]
        }

    async def _fetch_leetcode_metrics(self, db: AsyncSession, candidate_id: uuid.UUID) -> dict[str, Any] | None:
        stmt = select(LeetCodeProfile).where(
            LeetCodeProfile.candidate_profile_id == candidate_id,
            LeetCodeProfile.deleted_at.is_(None),
        )
        res = await db.execute(stmt)
        profile = res.scalars().first()
        if not profile:
            return None
        return {
            "problems_solved": profile.problems_solved,
            "rating": 1500,
            "topic_distribution": {},
        }

    async def _fetch_codeforces_metrics(self, db: AsyncSession, candidate_id: uuid.UUID) -> dict[str, Any] | None:
        stmt = select(CodeforcesProfile).where(
            CodeforcesProfile.candidate_profile_id == candidate_id,
            CodeforcesProfile.deleted_at.is_(None),
        )
        res = await db.execute(stmt)
        profile = res.scalars().first()
        if not profile:
            return None
        return {
            "problems_solved": 0,
            "rating": profile.rating,
            "max_rating": profile.max_rating,
            "rank": profile.rank,
            "contribution_consistency": 0.5,
            "topic_distribution": {},
        }
