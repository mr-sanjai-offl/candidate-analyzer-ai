"""Candidate service.

Handles business logic for candidate profiles.
"""

import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.database.repositories.candidate import CandidateProfileRepository
from app.schemas.candidate import CandidateProfileCreate, CandidateProfileUpdate


class CandidateService:
    """Service layer for candidate operations."""

    def __init__(self, profile_repo: CandidateProfileRepository):
        self.profile_repo = profile_repo

    async def get_profile(self, db: AsyncSession, profile_id: uuid.UUID) -> Any:
        """Get a profile by ID."""
        profile = await self.profile_repo.get_by_id(db=db, id=profile_id)
        if not profile:
            raise NotFoundException("Candidate profile not found.")
        return profile

    async def get_profile_by_user(self, db: AsyncSession, user_id: uuid.UUID) -> Optional[Any]:
        """Get a profile by user ID."""
        profiles = await self.profile_repo.filter(db=db, user_id=user_id)
        return profiles[0] if profiles else None

    async def create_profile(
        self, db: AsyncSession, user_id: uuid.UUID, obj_in: CandidateProfileCreate
    ) -> Any:
        """Create a new candidate profile for a user."""
        existing = await self.get_profile_by_user(db=db, user_id=user_id)
        if existing:
            raise ValueError("User already has a candidate profile.")

        create_data = obj_in.model_dump()
        create_data["user_id"] = user_id
        return await self.profile_repo.create(db=db, obj_in=create_data)

    async def update_profile(
        self, db: AsyncSession, profile_id: uuid.UUID, obj_in: CandidateProfileUpdate
    ) -> Any:
        """Update an existing candidate profile."""
        profile = await self.get_profile(db=db, profile_id=profile_id)
        return await self.profile_repo.update(db=db, db_obj=profile, obj_in=obj_in)
