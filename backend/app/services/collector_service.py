"""Collector service.

Top-level service that FastAPI routes interact with to trigger and track platform
data collection background tasks.
"""

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, NotFoundException
from app.database.models.candidate_profile import CandidateProfile
from app.database.models.enums import JobStatus, PlatformType
from app.database.models.platform_sync import PlatformSync
from app.database.repositories.job import BackgroundJobRepository
from app.database.repositories.platform_sync import PlatformSyncRepository
from app.services.job_manager import BackgroundJobService
from app.services.github_service import GitHubService
from app.services.leetcode_service import LeetCodeService
from app.services.codeforces_service import CodeforcesService

logger = logging.getLogger(__name__)


class CollectorService:
    """Service to coordinate all third-party sync operations and background job generation."""

    def __init__(self, redis_client: Any = None) -> None:
        self.job_service = BackgroundJobService(BackgroundJobRepository())
        self.sync_repo = PlatformSyncRepository()
        self.github_service = GitHubService(redis_client)
        self.leetcode_service = LeetCodeService(redis_client)
        self.codeforces_service = CodeforcesService(redis_client)

    async def trigger_collection(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        platform: PlatformType,
        username: str,
        force: bool = False,
    ) -> dict[str, str]:
        """Trigger sync job and register a background task in the database."""
        # Validate that the candidate exists
        candidate = await db.get(CandidateProfile, candidate_id)
        if not candidate:
            raise NotFoundException("Candidate profile not found.")

        # Check existing or create PlatformSync entity
        sync = await self.sync_repo.get_by_platform_and_username(
            db=db, platform=platform, username=username
        )
        if not sync:
            sync = PlatformSync(
                candidate_profile_id=candidate_id,
                platform=platform,
                username=username,
                sync_status=JobStatus.PENDING,
            )
            db.add(sync)
            await db.commit()
            await db.refresh(sync)

        # Enqueue the Celery task
        # Lazy import to avoid circular dependency
        from app.tasks.collectors import sync_platform_data

        celery_task = sync_platform_data.delay(
            str(candidate_id), str(platform), username, force
        )

        # Register inside background_jobs table
        job_id = await self.job_service.create_job(
            db=db,
            task_name=f"sync_{platform.lower()}_{username}",
            celery_task_id=celery_task.id,
        )

        return {
            "job_id": str(job_id),
            "celery_task_id": celery_task.id,
            "status": "QUEUED",
        }

    async def get_sync_status(
        self, db: AsyncSession, job_id: uuid.UUID
    ) -> dict[str, Any]:
        """Query background job details by job_id."""
        job = await self.job_service.get_job(db=db, job_id=job_id)
        if not job:
            raise NotFoundException("Job not found.")

        return {
            "job_id": str(job.id),
            "task_name": job.task_name,
            "status": job.status,
            "error_message": job.error_message,
            "started_at": job.started_at,
            "finished_at": job.finished_at,
            "duration_ms": job.duration_ms,
        }
