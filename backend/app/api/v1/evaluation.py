"""API Router for Candidate Technical Evaluation.

Provides endpoints for triggering full capabilities analysis, querying skills,
scores, role readiness, and gaps analysis.
"""

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.core.celery_app import celery_app
from app.core.exceptions import NotFoundException
from app.database.models.candidate_profile import CandidateProfile
from app.database.models.candidate_skill import CandidateSkill
from app.database.models.capability_score import CapabilityScore
from app.database.models.readiness_report import ReadinessReport
from app.database.models.user import User, UserRole
from app.database.models.background_job import BackgroundJob
from app.database.repositories.job import BackgroundJobRepository
from app.database.session import get_db_session
from app.services.job_manager import BackgroundJobService
from app.services.gap_analysis_service import GapAnalysisService
from app.services.skill_extraction_service import SkillExtractionService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Evaluation Engine"])


# ── Request / Response Schemas ────────────────────────────────────────────────

class AnalyzeSkillsRequest(BaseModel):
    """Schema to trigger candidate capability evaluation pipeline."""

    candidate_id: uuid.UUID = Field(..., description="Target candidate profile UUID.")


class EvaluationTriggerResponse(BaseModel):
    """Response containing background job status."""

    job_id: str
    celery_task_id: str
    status: str = "QUEUED"


# ── API Endpoints ─────────────────────────────────────────────────────────────

@router.post(
    "/analyze/skills",
    response_model=EvaluationTriggerResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger full capability evaluation pipeline",
)
async def analyze_skills(
    body: AnalyzeSkillsRequest,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Trigger background capability analysis including skill parsing, graph, and scoring."""
    # Ensure CandidateProfile exists
    candidate = await db.get(CandidateProfile, body.candidate_id)
    if not candidate:
        raise NotFoundException("Candidate profile not found.")

    # Enqueue pipeline task
    task = celery_app.send_task(
        "app.tasks.analysis.run_full_evaluation_pipeline",
        args=[str(body.candidate_id)],
    )

    # Register BackgroundJob in postgres
    job_repo = BackgroundJobRepository()
    job_service = BackgroundJobService(job_repo)
    job_id = await job_service.create_job(
        db=db,
        task_name=f"evaluation_{body.candidate_id.hex[:6]}",
        celery_task_id=task.id,
    )

    return {
        "job_id": str(job_id),
        "celery_task_id": task.id,
        "status": "QUEUED",
    }


@router.get(
    "/skills/{candidate_id}",
    summary="Get candidate extracted skills",
)
async def get_candidate_skills(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Retrieve all normalized skills and backing evidence for a candidate."""
    stmt = select(CandidateSkill).where(
        CandidateSkill.candidate_profile_id == candidate_id,
        CandidateSkill.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    candidate_skills = result.scalars().all()

    skills_data = []
    for cs in candidate_skills:
        # Fetch evidences
        from app.database.models.evidence import Evidence
        stmt_ev = select(Evidence).where(
            Evidence.candidate_profile_id == candidate_id,
            Evidence.skill_id == cs.skill_id,
            Evidence.deleted_at.is_(None),
        )
        res_ev = await db.execute(stmt_ev)
        evs = res_ev.scalars().all()

        skills_data.append({
            "skill_name": cs.skill.name,
            "category": cs.skill.category,
            "proficiency_score": cs.proficiency_score,
            "evidences": [
                {
                    "source": ev.source,
                    "weight": ev.weight,
                    "confidence": ev.confidence,
                    "evidence_text": ev.evidence_text,
                    "verification_state": ev.verification_state,
                    "timestamp": ev.created_at.isoformat() if ev.created_at else None,
                }
                for ev in evs
            ],
        })

    return {"candidate_id": str(candidate_id), "skills": skills_data}


@router.get(
    "/scores/{candidate_id}",
    summary="Get candidate capability scores",
)
async def get_candidate_scores(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Retrieve capability scores across the 20 technical categories."""
    stmt = select(CapabilityScore).where(
        CapabilityScore.candidate_profile_id == candidate_id,
        CapabilityScore.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    scores = result.scalars().all()

    if not scores:
        raise NotFoundException("Capability scores not found for this candidate.")

    return {
        "candidate_id": str(candidate_id),
        "scores": [
            {
                "category": s.category,
                "confidence_score": s.confidence_score,
                "experience_score": s.experience_score,
                "depth_score": s.depth_score,
                "breadth_score": s.breadth_score,
                "proficiency": s.proficiency,
                "explanation": s.explanation,
            }
            for s in scores
        ],
    }


@router.get(
    "/readiness/{candidate_id}",
    summary="Get candidate role readiness assessment",
)
async def get_candidate_readiness(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Retrieve job role readiness percentages (0-100) and gaps context."""
    stmt = select(ReadinessReport).where(
        ReadinessReport.candidate_profile_id == candidate_id,
        ReadinessReport.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    report = result.scalars().first()

    if not report:
        raise NotFoundException("Readiness report not found for this candidate.")

    return {
        "candidate_id": str(candidate_id),
        "backend_score": report.backend_score,
        "frontend_score": report.frontend_score,
        "fullstack_score": report.fullstack_score,
        "ai_score": report.ai_score,
        "data_score": report.data_score,
        "devops_score": report.devops_score,
        "cloud_score": report.cloud_score,
        "cybersecurity_score": report.cybersecurity_score,
        "embedded_score": report.embedded_score,
        "explanation": report.explanation,
    }


@router.get(
    "/gap-analysis/{candidate_id}",
    summary="Get candidate capability gap analysis",
)
async def get_candidate_gap_analysis(
    candidate_id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Retrieve detailed skills gaps and project roadmaps."""
    # 1. Fetch current skills map from database
    stmt = select(CandidateSkill).where(
        CandidateSkill.candidate_profile_id == candidate_id,
        CandidateSkill.deleted_at.is_(None),
    )
    result = await db.execute(stmt)
    candidate_skills = result.scalars().all()

    extracted_skills = {}
    for cs in candidate_skills:
        extracted_skills[cs.skill.name] = {
            "category": cs.skill.category,
        }

    # 2. Run service logic dynamically
    service = GapAnalysisService()
    return await service.generate_gap_analysis(
        db=db,
        candidate_id=candidate_id,
        extracted_skills=extracted_skills,
    )
