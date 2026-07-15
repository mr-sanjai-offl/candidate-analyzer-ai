"""Context Engine.

Assembles and trims structured evidence context for candidates from multiple sources.
Removes duplicate evidences to fit into model context windows.
"""

import logging
import uuid
from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.enums import PlatformType
from app.database.models.github_profile import GithubProfile
from app.database.models.leetcode_profile import LeetCodeProfile
from app.database.models.codeforces_profile import CodeforcesProfile
from app.database.models.evidence import Evidence
from app.database.models.capability_score import CapabilityScore
from app.database.models.readiness_report import ReadinessReport
from app.database.models.resume import UploadedResume, ResumeExtraction

logger = logging.getLogger(__name__)


class EvidenceAssembler:
    """Assembles and deduplicates verified pieces of evidence."""

    @staticmethod
    def assemble_evidence(evidences: list[Evidence]) -> list[dict[str, Any]]:
        """Remove duplicates and return serialized dictionary representation."""
        seen = set()
        deduped = []
        for ev in evidences:
            source_str = ev.source.value if hasattr(ev.source, "value") else str(ev.source)
            key = (source_str, ev.evidence_text.strip().lower())
            if key not in seen:
                seen.add(key)
                deduped.append({
                    "source": source_str,
                    "weight": ev.weight,
                    "confidence": ev.confidence,
                    "text": ev.evidence_text,
                    "verification": ev.verification_state,
                })
        return deduped


class ContextBuilder:
    """Aggregates candidate records into prompt context variables."""

    async def build_candidate_context(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        max_words: int = 2000,
    ) -> dict[str, Any]:
        """Queries and formats candidate records into a clean context dictionary."""
        # 1. Fetch Resume Data
        stmt_resume = (
            select(ResumeExtraction)
            .join(UploadedResume)
            .where(
                UploadedResume.owner_id == candidate_id, # fallback search matching user
                UploadedResume.deleted_at.is_(None)
            )
        )
        res_res = await db.execute(stmt_resume)
        resume = res_res.scalars().first()
        resume_text = resume.raw_text[:max_words] if resume and resume.raw_text else "No resume uploaded."

        # 2. Fetch platform profiles
        stmt_gh = select(GithubProfile).where(GithubProfile.candidate_profile_id == candidate_id)
        res_gh = await db.execute(stmt_gh)
        gh = res_gh.scalars().first()

        stmt_lc = select(LeetCodeProfile).where(LeetCodeProfile.candidate_profile_id == candidate_id)
        res_lc = await db.execute(stmt_lc)
        lc = res_lc.scalars().first()

        stmt_cf = select(CodeforcesProfile).where(CodeforcesProfile.candidate_profile_id == candidate_id)
        res_cf = await db.execute(stmt_cf)
        cf = res_cf.scalars().first()

        platforms_summary = []
        if gh:
            platforms_summary.append(f"GitHub: {gh.repositories_count} repos, {gh.stars_received} stars received.")
        if lc:
            platforms_summary.append(f"LeetCode: {lc.problems_solved} problems solved (Global rank: {lc.ranking}).")
        if cf:
            platforms_summary.append(f"Codeforces: Rating {cf.rating} (Rank: {cf.rank}).")

        # 3. Fetch capability scores
        stmt_scores = select(CapabilityScore).where(CapabilityScore.candidate_profile_id == candidate_id)
        res_scores = await db.execute(stmt_scores)
        scores = res_scores.scalars().all()
        scores_summary = [f"{s.category}: {s.proficiency.value} (Exp: {s.experience_score}, Depth: {s.depth_score})" for s in scores]

        # 4. Fetch readiness report
        stmt_readiness = select(ReadinessReport).where(ReadinessReport.candidate_profile_id == candidate_id)
        res_readiness = await db.execute(stmt_readiness)
        report = res_readiness.scalars().first()
        readiness_summary = []
        if report:
            readiness_summary = [
                f"Backend readiness: {report.backend_score}%",
                f"Frontend readiness: {report.frontend_score}%",
                f"Full Stack readiness: {report.fullstack_score}%",
                f"AI Engineer readiness: {report.ai_score}%",
                f"DevOps readiness: {report.devops_score}%",
            ]

        # 5. Fetch and deduplicate evidence
        stmt_ev = select(Evidence).where(Evidence.candidate_profile_id == candidate_id)
        res_ev = await db.execute(stmt_ev)
        evidences = res_ev.scalars().all()
        deduped_evs = EvidenceAssembler.assemble_evidence(evidences)

        return {
            "candidate_id": str(candidate_id),
            "resume_text": resume_text,
            "platforms": "\n".join(platforms_summary) if platforms_summary else "No platforms linked.",
            "scores": "; ".join(scores_summary) if scores_summary else "No capability scores available.",
            "readiness": "; ".join(readiness_summary) if readiness_summary else "No readiness reports calculated.",
            "evidence": deduped_evs,
        }
