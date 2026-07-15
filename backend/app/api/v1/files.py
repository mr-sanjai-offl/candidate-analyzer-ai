"""File upload and management API endpoints.

Implements Phase 5: File Upload & Storage.

All heavy-lifting (parsing, extraction) is off-loaded to Celery.
Routes validate, store and enqueue only.
"""

import logging
import uuid
from typing import Any, List

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker, get_current_user
from app.core.exceptions import BadRequestException
from app.database.models.user import User, UserRole
from app.database.repositories.resume import (
    ResumeVersionRepository,
    UploadedResumeRepository,
)
from app.database.session import get_db_session
from app.schemas.resume import ResumeDetailResponse, ResumeUploadResponse, ResumeResponse
from app.services.file_validation import FileValidationService
from app.services.resume_service import ResumeService
from app.services.storage_service import StorageService
from app.tasks.resumes import process_resume

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Files"])


# ── Dependency helpers ────────────────────────────────────────────────────────

def _build_resume_service() -> ResumeService:
    """Construct the ResumeService with all required dependencies."""
    return ResumeService(
        resume_repo=UploadedResumeRepository(),
        version_repo=ResumeVersionRepository(),
        storage=StorageService(),
        validator=FileValidationService(),
    )


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post(
    "/upload-resume",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Upload a candidate resume",
    description=(
        "Accepts a multipart resume file (PDF, DOCX, TXT, PNG, JPG). "
        "Validates content, detects duplicates, stores in Supabase, and "
        "immediately enqueues a background parsing job. Returns before parsing completes."
    ),
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file. Max 5 MB."),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Upload a resume and kick off the background parsing pipeline."""
    if not file.filename:
        raise BadRequestException("No filename provided.")

    file_bytes = await file.read()
    service = _build_resume_service()

    resume = await service.upload_resume(
        db=db,
        owner_id=current_user.id,
        file_bytes=file_bytes,
        original_filename=file.filename,
    )

    # Enqueue background parsing — routes never do the heavy work
    process_resume.delay(str(resume.id))
    logger.info(
        "Enqueued parse task for resume %s (user %s)", resume.id, current_user.id
    )

    return ResumeUploadResponse(
        resume_id=resume.id,
        original_filename=resume.original_filename,
        parsing_status=resume.parsing_status,
    )


@router.get(
    "/",
    response_model=List[ResumeResponse],
    summary="List my resumes",
    description="Returns all active resumes owned by the authenticated user.",
)
async def list_my_resumes(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """List resumes for the current user."""
    service = _build_resume_service()
    return await service.list_resumes(
        db=db, owner_id=current_user.id, skip=skip, limit=limit
    )


@router.get(
    "/{id}",
    response_model=ResumeDetailResponse,
    summary="Get resume details and extraction",
    description=(
        "Returns the resume record plus any structured extraction data. "
        "Admins can access any resume; candidates only their own."
    ),
)
async def get_resume(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Retrieve a resume with extraction data by ID."""
    service = _build_resume_service()
    is_admin = current_user.role == UserRole.ADMIN
    return await service.get_resume(
        db=db,
        resume_id=id,
        requester_id=current_user.id,
        is_admin=is_admin,
    )


@router.get(
    "/{id}/download-url",
    summary="Get a signed download URL",
    description="Returns a time-limited signed URL to download the resume directly from storage.",
)
async def get_download_url(
    id: uuid.UUID,
    expires_in: int = Query(3600, ge=60, le=86400, description="URL expiry in seconds"),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> dict[str, str]:
    """Generate and return a signed URL for the requested resume."""
    service = _build_resume_service()
    is_admin = current_user.role == UserRole.ADMIN
    resume = await service.get_resume(
        db=db, resume_id=id, requester_id=current_user.id, is_admin=is_admin
    )
    url = service.get_signed_url(resume.storage_path, expires_in=expires_in)
    return {"signed_url": url, "expires_in_seconds": str(expires_in)}


@router.post(
    "/{id}/replace",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Replace a resume with a new version",
    description=(
        "Uploads a new file and archives the previous one as a ResumeVersion. "
        "Re-triggers the parsing pipeline for the new file."
    ),
)
async def replace_resume(
    id: uuid.UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> Any:
    """Replace an existing resume file and re-parse it."""
    if not file.filename:
        raise BadRequestException("No filename provided.")

    file_bytes = await file.read()
    service = _build_resume_service()

    resume = await service.replace_resume(
        db=db,
        resume_id=id,
        requester_id=current_user.id,
        file_bytes=file_bytes,
        original_filename=file.filename,
    )

    # Re-enqueue parsing for the new version
    process_resume.delay(str(resume.id))
    logger.info("Re-enqueued parse task after replacement for resume %s", resume.id)

    return ResumeUploadResponse(
        resume_id=resume.id,
        original_filename=resume.original_filename,
        parsing_status=resume.parsing_status,
    )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resume",
    description="Soft-deletes the database record and removes the file from storage.",
)
async def delete_resume(
    id: uuid.UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(
        RoleChecker([UserRole.ADMIN, UserRole.RECRUITER, UserRole.CANDIDATE])
    ),
) -> None:
    """Delete an uploaded resume."""
    service = _build_resume_service()
    is_admin = current_user.role == UserRole.ADMIN
    await service.delete_resume(
        db=db, resume_id=id, requester_id=current_user.id, is_admin=is_admin
    )
