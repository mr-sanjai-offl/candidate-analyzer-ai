"""Reports API Router.

Exposes REST endpoints for generating and retrieving recruiter reports and candidate feedback.
"""

import logging
import uuid
from typing import Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.core.exceptions import NotFoundException
from app.database.models.user import User, UserRole
from app.database.models.analysis import Analysis
from app.database.session import get_db_session
from app.services.recruiter_report import RecruiterReportService
from app.services.candidate_feedback import CandidateFeedbackService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Reports Engine"])


# ── Schemas ───────────────────────────────────────────────────────────────────

class GenerateReportRequest(BaseModel):
    """Schema to trigger report generation runs."""

    candidate_id: uuid.UUID
    analysis_id: uuid.UUID


# ── Routes ────────────────────────────────────────────────────────────────────

@router.post(
    "/reports/recruiter",
    status_code=status.HTTP_200_OK,
    summary="Generate recruiter evaluation report",
)
async def generate_recruiter_report(
    body: GenerateReportRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER])),
) -> Any:
    """Generate structured technical assessment report for recruiters."""
    service = RecruiterReportService()
    return await service.generate_recruiter_report(
        db=db,
        candidate_id=body.candidate_id,
        analysis_id=body.analysis_id,
    )


@router.post(
    "/reports/candidate",
    status_code=status.HTTP_200_OK,
    summary="Generate candidate feedback report",
)
async def generate_candidate_feedback(
    body: GenerateReportRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Generate developmental feedback roadmaps for candidate."""
    service = CandidateFeedbackService()
    return await service.generate_candidate_feedback(
        db=db,
        candidate_id=body.candidate_id,
        analysis_id=body.analysis_id,
    )


@router.get(
    "/reports/{analysis_id}",
    summary="Get saved analysis report data",
)
async def get_saved_report(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Retrieve saved evaluation analysis report data by ID."""
    analysis = await db.get(Analysis, analysis_id)
    if not analysis:
        raise NotFoundException("Analysis report record not found.")

    return {
        "analysis_id": str(analysis.id),
        "state": analysis.state,
        "overall_score": analysis.overall_score,
        "report_data": analysis.report_data,
    }
