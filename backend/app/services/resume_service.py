"""Resume service.

Orchestrates the upload, storage, version management and retrieval of
candidate resumes. Routes must never call parser or storage logic directly —
all heavy work is delegated to Celery.
"""

import hashlib
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import BadRequestException, ForbiddenException, NotFoundException
from app.database.models.resume import ParsingState, UploadedResume, ResumeVersion
from app.database.repositories.resume import (
    ResumeVersionRepository,
    UploadedResumeRepository,
)
from app.services.file_validation import FileValidationService
from app.services.storage_service import StorageService

logger = logging.getLogger(__name__)

RESUME_BUCKET = "resumes"


class ResumeService:
    """Service for managing resume upload and retrieval lifecycle."""

    def __init__(
        self,
        resume_repo: UploadedResumeRepository,
        version_repo: ResumeVersionRepository,
        storage: StorageService,
        validator: FileValidationService,
    ) -> None:
        self.resume_repo = resume_repo
        self.version_repo = version_repo
        self.storage = storage
        self.validator = validator

    @staticmethod
    def _compute_hash(file_bytes: bytes) -> str:
        """Compute SHA-256 hex digest of raw file bytes."""
        return hashlib.sha256(file_bytes).hexdigest()

    @staticmethod
    def _build_storage_path(owner_id: uuid.UUID, resume_id: uuid.UUID, filename: str) -> str:
        """Build a namespaced, non-guessable storage path."""
        return f"{owner_id}/{resume_id}/{filename}"

    async def upload_resume(
        self,
        db: AsyncSession,
        owner_id: uuid.UUID,
        file_bytes: bytes,
        original_filename: str,
    ) -> UploadedResume:
        """Validate, deduplicate, store, and register a new resume.

        Does NOT parse or extract — that is the Celery pipeline's job.

        Args:
            db: Async database session.
            owner_id: UUID of the uploading user.
            file_bytes: Raw bytes of the uploaded file.
            original_filename: The name provided by the user's browser.

        Returns:
            The newly created UploadedResume record.

        Raises:
            BadRequestException: On validation or duplicate detection failure.
        """
        # 1. Sanitize filename
        safe_name = FileValidationService.sanitize_filename(original_filename)

        # 2. Validate size
        FileValidationService.validate_size(len(file_bytes))

        # 3. Deep MIME / content validation
        mime_type = FileValidationService.validate_content(file_bytes, safe_name)

        # 4. Duplicate detection
        file_hash = self._compute_hash(file_bytes)
        existing = await self.resume_repo.get_by_hash(
            db=db, file_hash=file_hash, owner_id=owner_id
        )
        if existing:
            raise BadRequestException(
                "This exact file has already been uploaded.",
                details={"existing_resume_id": str(existing.id)},
            )

        # 5. Build storage path and upload to Supabase
        resume_id = uuid.uuid4()
        storage_path = self._build_storage_path(owner_id, resume_id, safe_name)
        self.storage.upload_file(RESUME_BUCKET, storage_path, file_bytes, mime_type)
        logger.info(
            "Stored resume to bucket '%s' at path '%s'", RESUME_BUCKET, storage_path
        )

        # 6. Persist database record
        resume = UploadedResume(
            id=resume_id,
            owner_id=owner_id,
            original_filename=safe_name,
            storage_path=storage_path,
            file_hash=file_hash,
            file_size=len(file_bytes),
            mime_type=mime_type,
            parsing_status=ParsingState.PENDING,
        )
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        logger.info("Created UploadedResume record %s for user %s", resume_id, owner_id)
        return resume

    async def get_resume(
        self,
        db: AsyncSession,
        resume_id: uuid.UUID,
        requester_id: uuid.UUID,
        is_admin: bool = False,
    ) -> UploadedResume:
        """Retrieve a resume record with ownership validation."""
        resume = await self.resume_repo.get_by_id_with_extraction(
            db=db, resume_id=resume_id
        )
        if not resume or resume.deleted_at is not None:
            raise NotFoundException("Resume not found.")
        if not is_admin and resume.owner_id != requester_id:
            raise ForbiddenException("You do not own this resume.")
        return resume

    async def delete_resume(
        self,
        db: AsyncSession,
        resume_id: uuid.UUID,
        requester_id: uuid.UUID,
        is_admin: bool = False,
    ) -> None:
        """Soft-delete database record and remove from storage."""
        resume = await self.get_resume(
            db=db, resume_id=resume_id, requester_id=requester_id, is_admin=is_admin
        )

        # Delete from Supabase
        self.storage.delete_file(RESUME_BUCKET, resume.storage_path)

        # Soft-delete in database
        resume.deleted_at = datetime.now(timezone.utc)
        db.add(resume)
        await db.commit()
        logger.info("Soft-deleted resume %s", resume_id)

    async def replace_resume(
        self,
        db: AsyncSession,
        resume_id: uuid.UUID,
        requester_id: uuid.UUID,
        file_bytes: bytes,
        original_filename: str,
    ) -> UploadedResume:
        """Upload a new version of an existing resume.

        Archives the old storage path as a ResumeVersion and replaces
        the active record with the new file.
        """
        resume = await self.get_resume(
            db=db, resume_id=resume_id, requester_id=requester_id
        )

        safe_name = FileValidationService.sanitize_filename(original_filename)
        FileValidationService.validate_size(len(file_bytes))
        mime_type = FileValidationService.validate_content(file_bytes, safe_name)
        new_hash = self._compute_hash(file_bytes)

        # Archive existing version
        current_version_num = await self.version_repo.get_latest_version_number(
            db=db, resume_id=resume_id
        )
        version = ResumeVersion(
            resume_id=resume_id,
            version_number=current_version_num + 1,
            storage_path=resume.storage_path,
            file_hash=resume.file_hash,
        )
        db.add(version)

        # Upload new file to storage (replace)
        new_storage_path = self._build_storage_path(
            resume.owner_id, resume_id, safe_name
        )
        self.storage.replace_file(RESUME_BUCKET, new_storage_path, file_bytes, mime_type)

        # Update database record and reset parsing state
        resume.original_filename = safe_name
        resume.storage_path = new_storage_path
        resume.file_hash = new_hash
        resume.file_size = len(file_bytes)
        resume.mime_type = mime_type
        resume.parsing_status = ParsingState.PENDING
        db.add(resume)
        await db.commit()
        await db.refresh(resume)
        logger.info("Replaced resume %s, archived version %d", resume_id, current_version_num + 1)
        return resume

    async def list_resumes(
        self,
        db: AsyncSession,
        owner_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> list[UploadedResume]:
        """Return all active resumes for a user."""
        return await self.resume_repo.get_by_owner(
            db=db, owner_id=owner_id, skip=skip, limit=limit
        )

    def get_signed_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """Generate a signed download URL for a resume file."""
        return self.storage.get_signed_url(RESUME_BUCKET, storage_path, expires_in)
