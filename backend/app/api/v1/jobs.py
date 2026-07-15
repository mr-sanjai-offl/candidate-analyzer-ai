"""Jobs API endpoints.

Handles tracking and managing background jobs.
"""

import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.database.session import get_db_session
from app.core.celery_app import celery_app
from app.database.models.user import User, UserRole
from app.schemas.job import BackgroundJobResponse
from app.database.models.background_job import BackgroundJob
from app.database.repositories.job import BackgroundJobRepository
from app.services.job_manager import BackgroundJobService

router = APIRouter(tags=["Jobs"])


def get_job_service() -> BackgroundJobService:
    return BackgroundJobService(
        job_repo=BackgroundJobRepository(model=BackgroundJob)
    )


@router.get(
    "/",
    response_model=List[BackgroundJobResponse],
    summary="List background jobs",
)
async def list_jobs(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN])),
) -> Any:
    """Retrieve a list of background jobs."""
    service = get_job_service()
    return await service.get_all_jobs(db=db, skip=skip, limit=limit)


@router.get(
    "/{id}",
    response_model=BackgroundJobResponse,
    summary="Get background job",
)
async def get_job(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN])),
) -> Any:
    """Retrieve a background job by ID."""
    service = get_job_service()
    job = await service.get_job(db=db, job_id=id)
    if not job:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Job not found.")
    return job


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a background job record",
)
async def delete_job(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN])),
) -> None:
    """Delete a background job record."""
    service = get_job_service()
    job = await service.get_job(db=db, job_id=id)
    if not job:
        from app.core.exceptions import NotFoundException
        raise NotFoundException("Job not found.")
        
    # Cancel the actual celery task if it's running
    if job.celery_task_id:
        celery_app.control.revoke(job.celery_task_id, terminate=True)
        
    await service.delete_job(db=db, job_id=id)
