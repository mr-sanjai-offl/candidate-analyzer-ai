"""Normalization service.

Persists unified normalized profiles into the normalized relational database schema
(github_profiles, leetcode_profiles, codeforces_profiles, projects, skills).
"""

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.candidate_profile import CandidateProfile
from app.database.models.codeforces_profile import CodeforcesProfile
from app.database.models.enums import PlatformType, ProjectType, SkillCategory
from app.database.models.github_profile import GithubProfile
from app.database.models.leetcode_profile import LeetCodeProfile
from app.database.models.project import Project
from app.database.models.skill import Skill
from app.database.models.candidate_skill import CandidateSkill
from app.schemas.normalization import UnifiedPlatformProfile

logger = logging.getLogger(__name__)


class NormalizationService:
    """Processes UnifiedPlatformProfile and maps them to relational DB models."""

    async def persist_normalized_profile(
        self, db: AsyncSession, candidate_id: uuid.UUID, unified: UnifiedPlatformProfile
    ) -> None:
        """Persist unified profiles, projects, and skills to database."""
        platform = unified.platform.upper()

        if platform == "GITHUB":
            await self._persist_github(db, candidate_id, unified)
        elif platform == "LEETCODE":
            await self._persist_leetcode(db, candidate_id, unified)
        elif platform == "CODEFORCES":
            await self._persist_codeforces(db, candidate_id, unified)
        else:
            raise ValueError(f"Unsupported platform for normalization: {platform}")

        # Persist common elements: projects and skills
        await self._persist_projects(db, candidate_id, unified)
        await self._persist_skills(db, candidate_id, unified)

    # ── Platform-specific persistence ──────────────────────────────────

    async def _persist_github(
        self, db: AsyncSession, candidate_id: uuid.UUID, unified: UnifiedPlatformProfile
    ) -> None:
        """Create or update GithubProfile metrics."""
        stmt = select(GithubProfile).where(
            GithubProfile.candidate_profile_id == candidate_id,
            GithubProfile.username == unified.username,
        )
        res = await db.execute(stmt)
        profile = res.scalars().first()

        if not profile:
            profile = GithubProfile(
                candidate_profile_id=candidate_id,
                username=unified.username,
            )
            db.add(profile)

        profile.repositories_count = unified.public_repos
        profile.stars_received = unified.total_contributions
        profile.followers = unified.followers
        profile.total_commits = unified.extra.get("total_commits_count", 0)
        await db.commit()

    async def _persist_leetcode(
        self, db: AsyncSession, candidate_id: uuid.UUID, unified: UnifiedPlatformProfile
    ) -> None:
        """Create or update LeetCodeProfile metrics."""
        stmt = select(LeetCodeProfile).where(
            LeetCodeProfile.candidate_profile_id == candidate_id,
            LeetCodeProfile.username == unified.username,
        )
        res = await db.execute(stmt)
        profile = res.scalars().first()

        if not profile:
            profile = LeetCodeProfile(
                candidate_profile_id=candidate_id,
                username=unified.username,
            )
            db.add(profile)

        profile.problems_solved = unified.problems_solved
        profile.easy_solved = unified.easy_solved
        profile.medium_solved = unified.medium_solved
        profile.hard_solved = unified.hard_solved
        profile.ranking = unified.ranking
        await db.commit()

    async def _persist_codeforces(
        self, db: AsyncSession, candidate_id: uuid.UUID, unified: UnifiedPlatformProfile
    ) -> None:
        """Create or update CodeforcesProfile metrics."""
        stmt = select(CodeforcesProfile).where(
            CodeforcesProfile.candidate_profile_id == candidate_id,
            CodeforcesProfile.username == unified.username,
        )
        res = await db.execute(stmt)
        profile = res.scalars().first()

        if not profile:
            profile = CodeforcesProfile(
                candidate_profile_id=candidate_id,
                username=unified.username,
            )
            db.add(profile)

        profile.rating = unified.rating
        profile.max_rating = unified.max_rating
        profile.rank = unified.rank
        profile.max_rank = unified.max_rank
        await db.commit()

    # ── Projects and Skills persistence ────────────────────────────────

    async def _persist_projects(
        self, db: AsyncSession, candidate_id: uuid.UUID, unified: UnifiedPlatformProfile
    ) -> None:
        """Persist repositories to the projects table."""
        for uproj in unified.projects:
            # Check if project already exists
            stmt = select(Project).where(
                Project.candidate_profile_id == candidate_id,
                Project.name == uproj.name,
            )
            res = await db.execute(stmt)
            db_proj = res.scalars().first()

            if not db_proj:
                db_proj = Project(
                    candidate_profile_id=candidate_id,
                    name=uproj.name,
                )
                db.add(db_proj)

            db_proj.description = uproj.description
            db_proj.url = uproj.url
            db_proj.project_type = ProjectType.OPEN_SOURCE if uproj.is_fork else ProjectType.PERSONAL
            
        await db.commit()

    async def _persist_skills(
        self, db: AsyncSession, candidate_id: uuid.UUID, unified: UnifiedPlatformProfile
    ) -> None:
        """Map extracted platform skills into skills & candidate_skills tables."""
        for uskill in unified.skills:
            # 1. Fetch or create global Skill definition
            stmt = select(Skill).where(Skill.name == uskill.name)
            res = await db.execute(stmt)
            db_skill = res.scalars().first()

            if not db_skill:
                db_skill = Skill(
                    name=uskill.name,
                    category=SkillCategory(uskill.category),
                )
                db.add(db_skill)
                await db.commit()
                await db.refresh(db_skill)

            # 2. Map to CandidateSkill mapping table
            stmt_mapping = select(CandidateSkill).where(
                CandidateSkill.candidate_profile_id == candidate_id,
                CandidateSkill.skill_id == db_skill.id,
            )
            res_mapping = await db.execute(stmt_mapping)
            mapping = res_mapping.scalars().first()

            if not mapping:
                mapping = CandidateSkill(
                    candidate_profile_id=candidate_id,
                    skill_id=db_skill.id,
                )
                db.add(mapping)

            # Update proficiency score dynamically based on relevance
            mapping.proficiency_score = max(mapping.proficiency_score or 0.0, uskill.relevance_score)
            await db.commit()
