"""Celery background tasks for platform collection synchronization.

Provides tasks for async triggering, progress reporting, and recovery of GitHub,
LeetCode, and Codeforces synchronization workflows.
"""

import asyncio
import logging
import uuid
from typing import Any

from app.core.celery_app import celery_app
from app.database.models.enums import JobStatus, PlatformType
from app.database.repositories.job import BackgroundJobRepository
from app.database.session import get_db_session_ctx
from app.services.job_manager import BackgroundJobService
from app.services.synchronization_service import SynchronizationService
from app.tasks.base import RetryableTask

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    base=RetryableTask,
    name="app.tasks.collectors.sync_platform_data",
)
def sync_platform_data(
    self,
    candidate_id: str,
    platform: str,
    username: str,
    force: bool = False,
) -> None:
    """Orchestrates sync execution in background, updating job status inside postgres."""
    asyncio.run(
        _async_sync_platform_data(
            self,
            uuid.UUID(candidate_id),
            PlatformType(platform.upper()),
            username,
            force,
        )
    )


async def _async_sync_platform_data(
    task: Any,
    candidate_id: uuid.UUID,
    platform: PlatformType,
    username: str,
    force: bool = False,
) -> None:
    """Async handler for platform synchronization Celery task."""
    celery_task_id = task.request.id
    task.log_progress(10, f"Initializing synchronization for {platform} handle {username}...")

    job_repo = BackgroundJobRepository()
    job_service = BackgroundJobService(job_repo)
    sync_service = SynchronizationService(redis_client=celery_app.backend.client)

    async with get_db_session_ctx() as db:
        # Resolve the BackgroundJob record via Celery task ID
        stmt = job_repo.model.celery_task_id == celery_task_id
        jobs = await job_repo.filter(db=db, celery_task_id=celery_task_id)
        job = jobs[0] if jobs else None

        if not job:
            logger.error("No BackgroundJob found tracking celery task: %s", celery_task_id)
            return

        job_id = job.id

        try:
            # 1. Update job to RUNNING
            await job_service.update_status(db=db, job_id=job_id, status=JobStatus.RUNNING)
            task.log_progress(30, f"Querying {platform} platform API...")

            # 2. Trigger Synchronization
            await sync_service.synchronize_profile(
                db=db,
                candidate_id=candidate_id,
                platform=platform,
                username=username,
                force=force,
            )

            task.log_progress(90, "Finalizing database normalization...")
            
            # 3. Update job to SUCCESS
            await job_service.update_status(db=db, job_id=job_id, status=JobStatus.SUCCESS)
            task.log_progress(100, f"Successfully synchronized {platform} profile.")

        except Exception as exc:
            logger.error(
                "Task execution failed for platform sync job %s: %s", job_id, exc, exc_info=True
            )
            # Update job to FAILED
            await job_service.update_status(
                db=db,
                job_id=job_id,
                status=JobStatus.FAILED,
                error_message=str(exc),
            )
            raise exc
