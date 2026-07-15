"""Background job manager service.

Handles the job lifecycle tracking inside the database.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.enums import JobStatus
from app.database.repositories.job import BackgroundJobRepository

logger = logging.getLogger(__name__)


class BackgroundJobService:
    """Service for tracking Celery tasks in the database."""

    def __init__(self, job_repo: BackgroundJobRepository):
        self.job_repo = job_repo

    async def create_job(
        self, db: AsyncSession, task_name: str, celery_task_id: str
    ) -> uuid.UUID:
        """Create a new job record with PENDING status."""
        job = await self.job_repo.create(
            db=db,
            obj_in={
                "task_name": task_name,
                "celery_task_id": celery_task_id,
                "status": JobStatus.PENDING,
            },
        )
        logger.info(f"Created BackgroundJob {job.id} for task {task_name}")
        return job.id

    async def update_status(
        self,
        db: AsyncSession,
        job_id: uuid.UUID,
        status: JobStatus,
        worker_id: Optional[str] = None,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
    ) -> None:
        """Update job status and tracking timestamps."""
        job = await self.job_repo.get_by_id(db=db, id=job_id)
        if not job:
            logger.warning(f"BackgroundJob {job_id} not found for status update.")
            return

        update_data: dict[str, Any] = {"status": status}
        if worker_id:
            update_data["worker_id"] = worker_id
        if error_message:
            update_data["error_message"] = error_message
        if stack_trace:
            update_data["stack_trace"] = stack_trace

        now = datetime.now(timezone.utc)
        if status == JobStatus.RUNNING and not job.started_at:
            update_data["started_at"] = now
        elif status in (JobStatus.SUCCESS, JobStatus.FAILED, JobStatus.CANCELLED):
            update_data["finished_at"] = now
            if job.started_at:
                delta = now - job.started_at
                update_data["duration_ms"] = int(delta.total_seconds() * 1000)

        if status == JobStatus.RETRY:
            update_data["retry_count"] = job.retry_count + 1

        await self.job_repo.update(db=db, db_obj=job, obj_in=update_data)
        logger.info(f"BackgroundJob {job_id} status updated to {status}")

    async def get_job(self, db: AsyncSession, job_id: uuid.UUID) -> Any:
        return await self.job_repo.get_by_id(db=db, id=job_id)

    async def get_all_jobs(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> Any:
        return await self.job_repo.get_all(db=db, skip=skip, limit=limit)

    async def delete_job(self, db: AsyncSession, job_id: uuid.UUID) -> None:
        await self.job_repo.delete(db=db, id=job_id)
