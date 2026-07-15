"""Synchronization service.

Orchestrates the platform collector execution, cache management, raw DB storage,
and triggers downstream relational normalization.
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.base import CollectorConfig, CollectorContext
from app.collectors.exceptions import CollectorNotFoundException
from app.collectors.registry import get_factory
from app.collectors.utils import CacheManager
from app.core.config import get_settings
from app.core.exceptions import NotFoundException
from app.database.models.candidate_profile import CandidateProfile
from app.database.models.enums import JobStatus, PlatformType
from app.database.models.platform_sync import PlatformSync
from app.database.repositories.platform_sync import PlatformSyncRepository
from app.services.normalization_service import NormalizationService

logger = logging.getLogger(__name__)


class SynchronizationService:
    """Orchestrator for cache checks, sync job runs, and raw/normalized DB updates."""

    def __init__(self, redis_client: Any = None) -> None:
        self.cache = CacheManager(redis_client)
        self.sync_repo = PlatformSyncRepository()
        self.normalizer = NormalizationService()

    async def synchronize_profile(
        self,
        db: AsyncSession,
        candidate_id: uuid.UUID,
        platform: PlatformType,
        username: str,
        force: bool = False,
    ) -> PlatformSync:
        """Run platform sync, cache check, execute collector, and save results.

        This orchestrates the collection lifecycle and commits the output back to
        both PlatformSync and relational models.
        """
        # Ensure candidate exists
        candidate = await db.get(CandidateProfile, candidate_id)
        if not candidate:
            raise NotFoundException("Candidate profile not found.")

        # Check existing or create PlatformSync tracking model
        sync = await self.sync_repo.get_by_platform_and_username(
            db=db, platform=platform, username=username
        )
        if not sync:
            sync = PlatformSync(
                candidate_profile_id=candidate_id,
                platform=platform,
                username=username,
                sync_status=JobStatus.PENDING,
            )
            db.add(sync)
            await db.commit()
            await db.refresh(sync)

        # Cache check (unless force is requested)
        settings = get_settings()
        cache_key = CacheManager.build_key(str(platform), username, "profile")
        
        if not force:
            cached_raw = await self.cache.get(cache_key)
            if cached_raw:
                logger.info(
                    "[%s] Found cached payload for '%s'. Skipping API hits.",
                    platform,
                    username,
                )
                
                # Instantiate collector just to normalize cached data
                factory = get_factory()
                config = self._build_config(platform, settings)
                collector = factory.create(platform, config)
                ctx = CollectorContext(username=username, platform=platform)
                
                normalized = await collector.normalize(ctx, cached_raw)
                
                # Update status
                sync.sync_status = JobStatus.SUCCESS
                sync.raw_payload = cached_raw
                sync.normalized_payload = normalized.model_dump()
                sync.last_synced_at = datetime.now(timezone.utc)
                db.add(sync)
                await db.commit()
                
                # Normalize values to DB tables
                await self.normalizer.persist_normalized_profile(db, candidate_id, normalized)
                return sync

        # Execute Collector
        sync.sync_status = JobStatus.RUNNING
        db.add(sync)
        await db.commit()

        ctx = CollectorContext(
            username=username,
            platform=platform,
            job_id=str(sync.id),
            user_id=str(candidate.user_id),
        )

        factory = get_factory()
        config = self._build_config(platform, settings)
        collector = factory.create(platform, config)

        try:
            result = await collector.run(ctx)
            
            if result.success and result.raw and result.normalized:
                # Save to Cache
                await self.cache.set(
                    cache_key, result.raw, ttl=settings.COLLECTOR_CACHE_TTL
                )

                # Update Sync Table
                sync.sync_status = JobStatus.SUCCESS
                sync.raw_payload = result.raw
                sync.normalized_payload = result.normalized.model_dump()
                sync.error_message = None
                sync.platform_version = settings.APP_VERSION
                sync.api_version = "v1" if platform == PlatformType.GITHUB else "GQL/REST"
                sync.last_synced_at = datetime.now(timezone.utc)
                sync.retry_count = result.metrics.retry_count

                db.add(sync)
                await db.commit()

                # Normalize relational entities
                await self.normalizer.persist_normalized_profile(db, candidate_id, result.normalized)
            else:
                raise ValueError("Collector run finished unsuccessfully with no raw data.")

        except Exception as exc:
            logger.error("[%s] Sync orchestrator failed: %s", platform, exc)
            sync.sync_status = JobStatus.FAILED
            sync.error_message = str(exc)
            db.add(sync)
            await db.commit()
            raise exc

        return sync

    def _build_config(self, platform: PlatformType, settings: Any) -> CollectorConfig:
        """Create configuration settings for the targeted platform."""
        token_map = {
            PlatformType.GITHUB: settings.GITHUB_API_TOKEN,
            PlatformType.LEETCODE: None,
            PlatformType.CODEFORCES: None,
        }
        url_map = {
            PlatformType.GITHUB: settings.GITHUB_API_URL,
            PlatformType.LEETCODE: settings.LEETCODE_API_URL,
            PlatformType.CODEFORCES: settings.CODEFORCES_API_URL,
        }
        return CollectorConfig(
            platform=platform,
            base_url=url_map[platform],
            api_token=token_map[platform],
            timeout=settings.COLLECTOR_TIMEOUT,
            max_retries=settings.COLLECTOR_MAX_RETRIES,
            cache_ttl=settings.COLLECTOR_CACHE_TTL,
        )
