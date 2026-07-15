"""Platform Collection API routes.

Provides endpoints for triggering background collection/sync jobs and querying
sync status or normalized profile payloads.
"""

import logging
import uuid
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.core.exceptions import NotFoundException
from app.database.models.enums import PlatformType, JobStatus
from app.database.models.platform_sync import PlatformSync
from app.database.models.user import User, UserRole
from app.database.session import get_db_session
from app.services.collector_service import CollectorService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Collection & Profiles"])


# ── Pydantic Request/Response models ──────────────────────────────────────────

class CollectRequest(BaseModel):
    """Schema for individual platform collection trigger."""

    candidate_id: uuid.UUID = Field(..., description="Target candidate profile UUID.")
    username: str = Field(..., min_length=1, max_length=100, description="Platform handle.")
    force: bool = Field(default=False, description="Bypass cache and force api fetch.")


class CollectAllRequest(BaseModel):
    """Schema for sync all platforms trigger."""

    candidate_id: uuid.UUID
    github_username: Optional[str] = None
    leetcode_username: Optional[str] = None
    codeforces_username: Optional[str] = None
    force: bool = False


class CollectResponse(BaseModel):
    """Response containing background tracking identifiers."""

    job_id: str
    celery_task_id: str
    status: str = "QUEUED"


# ── Dependency helpers ────────────────────────────────────────────────────────

def _build_collector_service() -> CollectorService:
    """Instantiate CollectorService."""
    return CollectorService()


# ── Trigger Endpoints ─────────────────────────────────────────────────────────

@router.post(
    "/collect/github",
    response_model=CollectResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger GitHub sync background task",
)
async def collect_github(
    body: CollectRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Enqueue background GitHub repository and profile collection task."""
    service = _build_collector_service()
    return await service.trigger_collection(
        db=db,
        candidate_id=body.candidate_id,
        platform=PlatformType.GITHUB,
        username=body.username,
        force=body.force,
    )


@router.post(
    "/collect/leetcode",
    response_model=CollectResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger LeetCode sync background task",
)
async def collect_leetcode(
    body: CollectRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Enqueue background LeetCode problem solving collection task."""
    service = _build_collector_service()
    return await service.trigger_collection(
        db=db,
        candidate_id=body.candidate_id,
        platform=PlatformType.LEETCODE,
        username=body.username,
        force=body.force,
    )


@router.post(
    "/collect/codeforces",
    response_model=CollectResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger Codeforces sync background task",
)
async def collect_codeforces(
    body: CollectRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Enqueue background Codeforces contest and algorithm submission task."""
    service = _build_collector_service()
    return await service.trigger_collection(
        db=db,
        candidate_id=body.candidate_id,
        platform=PlatformType.CODEFORCES,
        username=body.username,
        force=body.force,
    )


@router.post(
    "/collect/all",
    response_model=list[dict[str, Any]],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Sync all coding profiles for a candidate",
)
async def collect_all(
    body: CollectAllRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Enqueue sync tasks for all supplied usernames in parallel."""
    service = _build_collector_service()
    jobs: list[dict[str, Any]] = []

    if body.github_username:
        j = await service.trigger_collection(
            db=db,
            candidate_id=body.candidate_id,
            platform=PlatformType.GITHUB,
            username=body.github_username,
            force=body.force,
        )
        j["platform"] = "GITHUB"
        jobs.append(j)

    if body.leetcode_username:
        j = await service.trigger_collection(
            db=db,
            candidate_id=body.candidate_id,
            platform=PlatformType.LEETCODE,
            username=body.leetcode_username,
            force=body.force,
        )
        j["platform"] = "LEETCODE"
        jobs.append(j)

    if body.codeforces_username:
        j = await service.trigger_collection(
            db=db,
            candidate_id=body.candidate_id,
            platform=PlatformType.CODEFORCES,
            username=body.codeforces_username,
            force=body.force,
        )
        j["platform"] = "CODEFORCES"
        jobs.append(j)

    return jobs


@router.get(
    "/collect/status/{job_id}",
    summary="Get sync background job status",
)
async def get_sync_status(
    job_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Retrieve job execution state and runtime diagnostics by ID."""
    service = _build_collector_service()
    return await service.get_sync_status(db=db, job_id=job_id)


# ── Profile Fetch Endpoints ──────────────────────────────────────────────────

async def _get_profile_by_platform(
    db: AsyncSession, platform: PlatformType, username: str
) -> Any:
    """Helper to query normalized platform payload."""
    stmt = select(PlatformSync).where(
        PlatformSync.platform == platform,
        PlatformSync.username == username,
        PlatformSync.sync_status == JobStatus.SUCCESS,
        PlatformSync.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    sync = result.scalars().first()

    if not sync or not sync.normalized_payload:
        raise NotFoundException(
            f"Normalized data not found for {platform} handle '{username}'."
        )

    return sync.normalized_payload


@router.get(
    "/profile/github/{username}",
    summary="Get normalized GitHub profile",
)
async def get_github_profile(
    username: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Get normalized GitHub profile payload."""
    return await _get_profile_by_platform(db, PlatformType.GITHUB, username)


@router.get(
    "/profile/leetcode/{username}",
    summary="Get normalized LeetCode profile",
)
async def get_leetcode_profile(
    username: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Get normalized LeetCode profile payload."""
    return await _get_profile_by_platform(db, PlatformType.LEETCODE, username)


@router.get(
    "/profile/codeforces/{username}",
    summary="Get normalized Codeforces profile",
)
async def get_codeforces_profile(
    username: str,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Get normalized Codeforces profile payload."""
    return await _get_profile_by_platform(db, PlatformType.CODEFORCES, username)

