"""GitHub sync service.

Platform-specific wrapper for GitHub sync operations.
"""

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.enums import PlatformType
from app.database.models.platform_sync import PlatformSync
from app.services.synchronization_service import SynchronizationService


class GitHubService:
    """Service to handle GitHub data collection synchronization."""

    def __init__(self, redis_client: Any = None) -> None:
        self._sync_service = SynchronizationService(redis_client)

    async def sync_github(
        self, db: AsyncSession, candidate_id: uuid.UUID, username: str, force: bool = False
    ) -> PlatformSync:
        """Trigger sync for GitHub username."""
        return await self._sync_service.synchronize_profile(
            db=db,
            candidate_id=candidate_id,
            platform=PlatformType.GITHUB,
            username=username,
            force=force,
        )
