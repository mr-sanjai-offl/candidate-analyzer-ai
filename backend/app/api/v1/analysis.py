"""Analysis API endpoints.

Handles requests for starting and retrieving candidate capability analysis.
Routes NEVER execute heavy work; they enqueue jobs via Celery.
"""

import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.core.celery_app import celery_app
from app.database.session import get_db_session
from app.database.models.user import User, UserRole
from app.schemas.analysis import AnalysisCreate, AnalysisResponse
from app.services.analysis_service import AnalysisService
from app.database.repositories.analysis import AnalysisHistoryRepository, AnalysisRepository
from app.database.repositories.job import BackgroundJobRepository
from app.services.job_manager import BackgroundJobService

router = APIRouter(tags=["Analysis"])


def get_analysis_service() -> AnalysisService:
    return AnalysisService(
        analysis_repo=AnalysisRepository(model=AnalysisRepository.__orig_bases__[0].__args__[0]),
        history_repo=AnalysisHistoryRepository(model=AnalysisHistoryRepository.__orig_bases__[0].__args__[0]),
    )

def get_job_service() -> BackgroundJobService:
    return BackgroundJobService(
        job_repo=BackgroundJobRepository(model=BackgroundJobRepository.__orig_bases__[0].__args__[0])
    )


@router.post(
    "/start",
    response_model=AnalysisResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Start candidate capability analysis",
)
async def start_analysis(
    request: AnalysisCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER])),
) -> Any:
    """Initialize an analysis and enqueue a background job.
    
    This endpoint does not perform the heavy work itself. It starts the
    pipeline and returns the created Analysis record immediately.
    """
    # Initialize the analysis service with dependencies
    from app.database.models.analysis import Analysis, AnalysisHistory
    
    analysis_repo = AnalysisRepository(model=Analysis)
    history_repo = AnalysisHistoryRepository(model=AnalysisHistory)
    service = AnalysisService(analysis_repo, history_repo)

    # Start analysis
    analysis = await service.start_analysis(db=db, candidate_profile_id=request.candidate_profile_id)

    # Enqueue background job (task name from tasks package)
    task = celery_app.send_task("app.tasks.analysis.run_analysis", args=[str(analysis.id)])

    # Record the background job in the database
    from app.database.models.background_job import BackgroundJob
    job_repo = BackgroundJobRepository(model=BackgroundJob)
    job_service = BackgroundJobService(job_repo)
    
    await job_service.create_job(db=db, task_name="app.tasks.analysis.run_analysis", celery_task_id=task.id)

    return analysis


@router.get(
    "/{id}",
    response_model=AnalysisResponse,
    summary="Get analysis report",
)
async def get_analysis(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])),
) -> Any:
    """Retrieve an analysis report by ID."""
    from app.database.models.analysis import Analysis, AnalysisHistory
    analysis_repo = AnalysisRepository(model=Analysis)
    history_repo = AnalysisHistoryRepository(model=AnalysisHistory)
    service = AnalysisService(analysis_repo, history_repo)

    return await service.get_analysis(db=db, analysis_id=id)
