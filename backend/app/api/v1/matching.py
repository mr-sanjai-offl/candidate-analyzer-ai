"""Job Matching API Router.

Exposes REST endpoints for matching candidate capability profiles against Job Descriptions.
"""

import logging
import uuid
from typing import Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.database.models.user import User, UserRole
from app.database.session import get_db_session
from app.services.job_matching import JobMatchingService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Job Matching"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class JobMatchRequest(BaseModel):
    """Schema to trigger job matching evaluations."""

    candidate_id: uuid.UUID
    job_title: str = Field(..., max_length=150)
    job_description: str = Field(..., min_length=10, description="Raw JD text.")


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post(
    "/jobs/match",
    status_code=status.HTTP_200_OK,
    summary="Evaluate candidate profile match against JD",
)
async def match_candidate(
    body: JobMatchRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER])),
) -> Any:
    """Assess suitability match score, missing skills and suggestions against a JD."""
    service = JobMatchingService()
    return await service.match_candidate_to_jd(
        db=db,
        candidate_id=body.candidate_id,
        job_title=body.job_title,
        job_description=body.job_description,
    )
