"""LeetCode sync service.

Platform-specific wrapper for LeetCode sync operations.
"""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.enums import PlatformType
from app.database.models.platform_sync import PlatformSync
from app.services.synchronization_service import SynchronizationService


class LeetCodeService:
    """Service to handle LeetCode data collection synchronization."""

    def __init__(self, redis_client: Any = None) -> None:
        self._sync_service = SynchronizationService(redis_client)

    async def sync_leetcode(
        self, db: AsyncSession, candidate_id: uuid.UUID, username: str, force: bool = False
    ) -> PlatformSync:
        """Trigger sync for LeetCode username."""
        return await self._sync_service.synchronize_profile(
            db=db,
            candidate_id=candidate_id,
            platform=PlatformType.LEETCODE,
            username=username,
            force=force,
        )
