"""Repository for resume-related models."""

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models.resume import (
    ResumeExtraction,
    ResumeMetadata,
    ResumeVersion,
    UploadedResume,
)
from app.database.repositories.base import BaseRepository
from app.schemas.resume import ResumeResponse


class UploadedResumeRepository(
    BaseRepository[UploadedResume, ResumeResponse, ResumeResponse]
):
    """Repository for UploadedResume model with helper queries."""

    def __init__(self) -> None:
        super().__init__(model=UploadedResume)

    async def get_by_id_with_extraction(
        self, db: AsyncSession, resume_id: uuid.UUID
    ) -> Optional[UploadedResume]:
        """Fetch resume with its extraction record eagerly loaded."""
        stmt = (
            select(UploadedResume)
            .options(selectinload(UploadedResume.extraction))
            .where(UploadedResume.id == resume_id)
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_hash(
        self, db: AsyncSession, file_hash: str, owner_id: uuid.UUID
    ) -> Optional[UploadedResume]:
        """Check if the same owner already uploaded this exact file."""
        stmt = select(UploadedResume).where(
            UploadedResume.file_hash == file_hash,
            UploadedResume.owner_id == owner_id,
            UploadedResume.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_by_owner(
        self, db: AsyncSession, owner_id: uuid.UUID, skip: int = 0, limit: int = 100
    ) -> list[UploadedResume]:
        """Get all resumes belonging to a user."""
        stmt = (
            select(UploadedResume)
            .where(
                UploadedResume.owner_id == owner_id,
                UploadedResume.deleted_at.is_(None),
            )
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())


class ResumeVersionRepository(
    BaseRepository[ResumeVersion, ResumeResponse, ResumeResponse]
):
    """Repository for ResumeVersion model."""

    def __init__(self) -> None:
        super().__init__(model=ResumeVersion)

    async def get_latest_version_number(
        self, db: AsyncSession, resume_id: uuid.UUID
    ) -> int:
        """Get the current highest version number for a resume."""
        versions = await self.filter(db=db, resume_id=resume_id)
        if not versions:
            return 0
        return max(v.version_number for v in versions)


class ResumeExtractionRepository(
    BaseRepository[ResumeExtraction, ResumeResponse, ResumeResponse]
):
    """Repository for ResumeExtraction model."""

    def __init__(self) -> None:
        super().__init__(model=ResumeExtraction)

    async def get_by_resume_id(
        self, db: AsyncSession, resume_id: uuid.UUID
    ) -> Optional[ResumeExtraction]:
        """Get the extraction for a specific resume."""
        stmt = select(ResumeExtraction).where(
            ResumeExtraction.resume_id == resume_id
        )
        result = await db.execute(stmt)
        return result.scalars().first()
