"""Skill Extraction Service.

Orchestrates the deterministic skill extraction process, standardizes skills,
and records verification evidence in the database.
"""

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.candidate_profile import CandidateProfile
from app.database.models.candidate_skill import CandidateSkill
from app.database.models.enums import EvidenceSource
from app.database.models.evidence import Evidence
from app.database.models.skill import Skill
from app.database.models.evaluation_history import EvaluationHistory
from app.scoring.skill_engine import SkillExtractionEngine

logger = logging.getLogger(__name__)


class SkillExtractionService:
    """Service to execute skill extraction and persist evidence records."""

    def __init__(self) -> None:
        self.engine = SkillExtractionEngine()

    async def extract_and_persist_skills(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        resume_data: dict[str, Any] | None = None,
        github_profile: dict[str, Any] | None = None,
        leetcode_profile: dict[str, Any] | None = None,
        codeforces_profile: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute deterministic skill parsing and save mappings and evidence to DB."""
        # 1. Run extraction logic
        skills_dict = self.engine.extract_skills(
            resume_data=resume_data,
            github_profile=github_profile,
            leetcode_profile=leetcode_profile,
            codeforces_profile=codeforces_profile,
        )

        logger.info(
            "Extracted %d skills for candidate %s", len(skills_dict), candidate_id
        )

        # 2. Persist to tables
        evidence_count = 0
        for sname, info in skills_dict.items():
            # Get or create Skill definition
            stmt = select(Skill).where(Skill.name == sname)
            result = await db.execute(stmt)
            db_skill = result.scalars().first()

            if not db_skill:
                db_skill = Skill(
                    name=sname,
                    category=info["category"],
                    description=f"Standardized technology: {sname}",
                )
                db.add(db_skill)
                await db.flush()

            # Link to CandidateSkill
            stmt_link = select(CandidateSkill).where(
                CandidateSkill.candidate_profile_id == candidate_id,
                CandidateSkill.skill_id == db_skill.id,
            )
            result_link = await db.execute(stmt_link)
            db_link = result_link.scalars().first()

            if not db_link:
                db_link = CandidateSkill(
                    candidate_profile_id=candidate_id,
                    skill_id=db_skill.id,
                    proficiency_score=0.0,
                )
                db.add(db_link)
                await db.flush()

            # Save Evidence lists
            for ev in info["evidences"]:
                # Check for existing duplicate evidence
                stmt_ev = select(Evidence).where(
                    Evidence.candidate_profile_id == candidate_id,
                    Evidence.skill_id == db_skill.id,
                    Evidence.source == ev["source"],
                    Evidence.evidence_text == ev["evidence"],
                )
                result_ev = await db.execute(stmt_ev)
                db_ev = result_ev.scalars().first()

                if not db_ev:
                    db_ev = Evidence(
                        candidate_profile_id=candidate_id,
                        skill_id=db_skill.id,
                        source=ev["source"],
                        weight=ev["weight"],
                        confidence=ev["confidence"],
                        evidence_text=ev["evidence"],
                        verification_state=ev["verification_state"],
                        metadata_json=ev["metadata"],
                    )
                    db.add(db_ev)
                    evidence_count += 1

        # 3. Log execution stats in EvaluationHistory
        history = EvaluationHistory(
            candidate_profile_id=candidate_id,
            action="SKILL_EXTRACTION",
            metadata_json={
                "skills_count": len(skills_dict),
                "new_evidence_count": evidence_count,
            },
        )
        db.add(history)
        await db.commit()

        return skills_dict
