"""Celery background tasks for Phase 10 & 11 evaluation engines.

Defines tasks for async skill extraction, graph generation, capability scoring,
and gap analysis metrics.
"""

import asyncio
import logging
import uuid
from typing import Any

from sqlalchemy import select

from app.core.celery_app import celery_app
from app.database.models.enums import JobStatus
from app.database.models.candidate_profile import CandidateProfile
from app.database.models.github_profile import GithubProfile
from app.database.models.leetcode_profile import LeetCodeProfile
from app.database.models.codeforces_profile import CodeforcesProfile
from app.database.models.resume import UploadedResume, ResumeExtraction
from app.database.repositories.job import BackgroundJobRepository
from app.database.session import get_db_session_ctx
from app.services.job_manager import BackgroundJobService
from app.services.skill_extraction_service import SkillExtractionService
from app.services.knowledge_graph_service import KnowledgeGraphService
from app.services.capability_scoring_service import CapabilityScoringService
from app.services.readiness_service import ReadinessService
from app.services.gap_analysis_service import GapAnalysisService
from app.tasks.base import RetryableTask

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    base=RetryableTask,
    name="app.tasks.analysis.run_full_evaluation_pipeline",
)
def run_full_evaluation_pipeline(
    self,
    candidate_id: str,
) -> dict[str, Any]:
    """Orchestrates the entire evaluation pipeline sequentially."""
    return asyncio.run(_async_run_pipeline(self, uuid.UUID(candidate_id)))


async def _async_run_pipeline(task: Any, candidate_id: uuid.UUID) -> dict[str, Any]:
    """Execute all evaluation tasks sequentially inside a single background job."""
    celery_task_id = task.request.id
    task.log_progress(10, "Starting candidate capability evaluation...")

    job_repo = BackgroundJobRepository()
    job_service = BackgroundJobService(job_repo)

    async with get_db_session_ctx() as db:
        # Resolve tracking BackgroundJob
        jobs = await job_repo.filter(db=db, celery_task_id=celery_task_id)
        job = jobs[0] if jobs else None

        if not job:
            logger.error("No BackgroundJob found for celery task %s", celery_task_id)
            return {"status": "ERROR", "message": "No job tracker found."}

        job_id = job.id
        await job_service.update_status(db=db, job_id=job_id, status=JobStatus.RUNNING)

        try:
            # ── 1. Fetch Candidate Profile & input parameters ─────────────────
            candidate = await db.get(CandidateProfile, candidate_id)
            if not candidate:
                raise ValueError("Candidate profile not found.")

            # Load Resume Extraction
            stmt_resume = (
                select(ResumeExtraction)
                .join(UploadedResume)
                .where(
                    UploadedResume.owner_id == candidate.user_id,
                    UploadedResume.deleted_at.is_(None),
                )
                .order_by(UploadedResume.created_at.desc())
            )
            res_res = await db.execute(stmt_resume)
            resume = res_res.scalars().first()
            resume_data = resume.structured_data if resume else None

            # Load GitHub Profile
            stmt_gh = select(GithubProfile).where(
                GithubProfile.candidate_profile_id == candidate_id,
                GithubProfile.deleted_at.is_(None),
            )
            res_gh = await db.execute(stmt_gh)
            gh_profile = res_gh.scalars().first()
            gh_data = {
                "primary_language": getattr(gh_profile, "primary_language", ""),
                "skills": [],
                "public_repos": getattr(gh_profile, "repositories_count", 0),
                "total_contributions": getattr(gh_profile, "stars_received", 0),
                "followers": getattr(gh_profile, "followers", 0),
            } if gh_profile else None

            # Load LeetCode Profile
            stmt_lc = select(LeetCodeProfile).where(
                LeetCodeProfile.candidate_profile_id == candidate_id,
                LeetCodeProfile.deleted_at.is_(None),
            )
            res_lc = await db.execute(stmt_lc)
            lc_profile = res_lc.scalars().first()
            lc_data = {
                "problems_solved": getattr(lc_profile, "problems_solved", 0),
                "easy_solved": getattr(lc_profile, "easy_solved", 0),
                "medium_solved": getattr(lc_profile, "medium_solved", 0),
                "hard_solved": getattr(lc_profile, "hard_solved", 0),
                "ranking": getattr(lc_profile, "ranking", 0),
                "topic_distribution": {},
            } if lc_profile else None

            # Load Codeforces Profile
            stmt_cf = select(CodeforcesProfile).where(
                CodeforcesProfile.candidate_profile_id == candidate_id,
                CodeforcesProfile.deleted_at.is_(None),
            )
            res_cf = await db.execute(stmt_cf)
            cf_profile = res_cf.scalars().first()
            cf_data = {
                "rating": getattr(cf_profile, "rating", 0),
                "max_rating": getattr(cf_profile, "max_rating", 0),
                "rank": getattr(cf_profile, "rank", ""),
                "max_rank": getattr(cf_profile, "max_rank", ""),
                "topic_distribution": {},
            } if cf_profile else None

            # ── 2. Run Skill Extraction ───────────────────────────────────────
            task.log_progress(30, "Extracting skills and mapping aliases...")
            extractor = SkillExtractionService()
            extracted_skills = await extractor.extract_and_persist_skills(
                db=db,
                candidate_id=candidate_id,
                resume_data=resume_data,
                github_profile=gh_data,
                leetcode_profile=lc_data,
                codeforces_profile=cf_data,
            )

            # ── 3. Build Knowledge Graph ──────────────────────────────────────
            task.log_progress(50, "Generating Knowledge Graph representation...")
            graph_service = KnowledgeGraphService()
            await graph_service.build_graph(
                db=db,
                candidate_id=candidate_id,
                extracted_skills=extracted_skills,
                github_profile=gh_data,
            )

            # ── 4. Capability Scoring ─────────────────────────────────────────
            task.log_progress(70, "Computing deterministic capability scores...")
            scoring = CapabilityScoringService()
            await scoring.compute_and_persist_scores(
                db=db,
                candidate_id=candidate_id,
                extracted_skills=extracted_skills,
            )

            # ── 5. Job Readiness Assessment ──────────────────────────────────
            task.log_progress(85, "Evaluating job role readiness percentages...")
            readiness = ReadinessService()
            await readiness.compute_and_persist_readiness(
                db=db,
                candidate_id=candidate_id,
                extracted_skills=extracted_skills,
            )

            # ── 6. Gap Analysis ───────────────────────────────────────────────
            task.log_progress(95, "Running candidate skill gap calculations...")
            gaps = GapAnalysisService()
            await gaps.generate_gap_analysis(
                db=db,
                candidate_id=candidate_id,
                extracted_skills=extracted_skills,
            )

            await job_service.update_status(db=db, job_id=job_id, status=JobStatus.SUCCESS)
            task.log_progress(100, "Evaluation pipeline finished successfully.")
            return {"status": "SUCCESS", "candidate_id": str(candidate_id)}

        except Exception as exc:
            logger.error("Pipeline failure: %s", exc, exc_info=True)
            await job_service.update_status(
                db=db,
                job_id=job_id,
                status=JobStatus.FAILED,
                error_message=str(exc),
            )
            raise exc
