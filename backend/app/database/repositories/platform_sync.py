"""PlatformSync database repository.

Handles persistence operations for raw and normalized platform payloads.
"""

import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.enums import PlatformType
from app.database.models.platform_sync import PlatformSync
from app.database.repositories.base import BaseRepository


class PlatformSyncRepository(BaseRepository[PlatformSync, Any, Any]):
    """Repository operations for PlatformSync models."""

    def __init__(self) -> None:
        super().__init__(model=PlatformSync)

    async def get_by_platform_and_username(
        self, db: AsyncSession, platform: PlatformType, username: str
    ) -> Optional[PlatformSync]:
        """Fetch sync info for a given platform and username combo."""
        stmt = select(PlatformSync).where(
            PlatformSync.platform == platform,
            PlatformSync.username == username,
            PlatformSync.deleted_at.is_(None),
        )
        result = await db.execute(stmt)
        return result.scalars().first()

    async def get_latest_sync(
        self, db: AsyncSession, candidate_profile_id: uuid.UUID, platform: PlatformType
    ) -> Optional[PlatformSync]:
        """Fetch latest sync details for a candidate and platform."""
        stmt = (
            select(PlatformSync)
            .where(
                PlatformSync.candidate_profile_id == candidate_profile_id,
                PlatformSync.platform == platform,
                PlatformSync.deleted_at.is_(None),
            )
            .order_by(PlatformSync.updated_at.desc())
        )
        result = await db.execute(stmt)
        return result.scalars().first()
