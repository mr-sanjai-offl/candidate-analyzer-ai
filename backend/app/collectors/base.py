"""Collector base framework.

Defines the abstract collector lifecycle, configuration, context,
result structures, and metrics. Every concrete collector must inherit
from BaseCollector and implement its abstract methods.
"""

import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Generic, TypeVar

from app.collectors.exceptions import CollectorException
from app.database.models.enums import PlatformType

logger = logging.getLogger(__name__)

RawT = TypeVar("RawT")
NormT = TypeVar("NormT")


@dataclass
class CollectorConfig:
    """Configuration for a specific collector instance.

    Attributes:
        platform: The target platform enum value.
        base_url: Root API URL for the platform.
        api_token: Optional authentication token (sourced from env).
        timeout: HTTP request timeout in seconds.
        max_retries: Maximum retry attempts on transient failures.
        cache_ttl: Cache time-to-live in seconds (0 = no cache).
    """

    platform: PlatformType
    base_url: str
    api_token: str | None = None
    timeout: int = 30
    max_retries: int = 3
    cache_ttl: int = 3600


@dataclass
class CollectorContext:
    """Execution context for a single collection run.

    Carries identifiers used for correlation, logging, and tracing.
    """

    correlation_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    job_id: str | None = None
    user_id: str | None = None
    username: str = ""
    platform: PlatformType | None = None


@dataclass
class CollectorMetrics:
    """Observability metrics captured during a collection run."""

    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    duration_seconds: float = 0.0
    api_calls_made: int = 0
    bytes_fetched: int = 0
    retry_count: int = 0
    rate_limit_hits: int = 0
    cache_hits: int = 0
    success: bool = False

    def finish(self) -> None:
        """Mark the collection as finished and compute duration."""
        self.finished_at = datetime.now(timezone.utc)
        self.duration_seconds = (self.finished_at - self.started_at).total_seconds()


@dataclass
class CollectorResult(Generic[RawT, NormT]):
    """Container for a completed collection run.

    Attributes:
        raw: The unmodified platform response payload.
        normalized: The unified schema representation.
        metrics: Performance and observability metrics.
        platform: The platform this result was collected from.
        username: The external username that was collected.
    """

    raw: RawT | None = None
    normalized: NormT | None = None
    metrics: CollectorMetrics = field(default_factory=CollectorMetrics)
    platform: PlatformType | None = None
    username: str = ""
    success: bool = False
    error: str | None = None


class BaseCollector(ABC, Generic[RawT, NormT]):
    """Abstract base class defining the collector lifecycle.

    Lifecycle stages executed by ``run()``:
        1. initialize  — prepare HTTP clients, load config
        2. validate_input — check username format
        3. fetch_data — call external APIs
        4. normalize — transform raw payload → unified schema
        5. validate — verify normalized data integrity
        6. store — persist raw + normalized payloads (optional override)
        7. return result

    Every stage emits structured logs with the correlation ID.
    """

    def __init__(self, config: CollectorConfig) -> None:
        self.config = config
        self._client: Any = None

    # ── Abstract methods ──────────────────────────────────────────────

    @abstractmethod
    async def initialize(self, ctx: CollectorContext) -> None:
        """Prepare the collector (e.g. create HTTPX client)."""
        ...

    @abstractmethod
    async def validate_input(self, ctx: CollectorContext) -> None:
        """Validate that the username / input is well-formed."""
        ...

    @abstractmethod
    async def fetch_data(self, ctx: CollectorContext) -> RawT:
        """Execute external API calls and return the raw payload."""
        ...

    @abstractmethod
    async def normalize(self, ctx: CollectorContext, raw: RawT) -> NormT:
        """Transform raw platform data into the unified schema."""
        ...

    @abstractmethod
    async def validate_result(self, ctx: CollectorContext, normalized: NormT) -> None:
        """Validate the normalized result for data integrity."""
        ...

    # ── Optional hooks ────────────────────────────────────────────────

    async def teardown(self, ctx: CollectorContext) -> None:
        """Release resources (e.g. close HTTP client). Override if needed."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    # ── Orchestrator ──────────────────────────────────────────────────

    async def run(self, ctx: CollectorContext) -> CollectorResult[RawT, NormT]:
        """Execute the full collector lifecycle.

        This method should NOT be overridden. It orchestrates the abstract
        stage methods, captures metrics, and handles errors uniformly.
        """
        result: CollectorResult[RawT, NormT] = CollectorResult(
            platform=self.config.platform,
            username=ctx.username,
        )
        metrics = result.metrics

        logger.info(
            "[%s] Collection started for '%s' | correlation_id=%s",
            self.config.platform,
            ctx.username,
            ctx.correlation_id,
        )

        try:
            # 1. Initialize
            await self.initialize(ctx)
            logger.debug("[%s] Initialized | cid=%s", self.config.platform, ctx.correlation_id)

            # 2. Validate Input
            await self.validate_input(ctx)
            logger.debug("[%s] Input validated | cid=%s", self.config.platform, ctx.correlation_id)

            # 3. Fetch Data
            raw = await self.fetch_data(ctx)
            result.raw = raw
            logger.info(
                "[%s] Data fetched | api_calls=%d | cid=%s",
                self.config.platform,
                metrics.api_calls_made,
                ctx.correlation_id,
            )

            # 4. Normalize
            normalized = await self.normalize(ctx, raw)
            result.normalized = normalized
            logger.debug("[%s] Data normalized | cid=%s", self.config.platform, ctx.correlation_id)

            # 5. Validate Result
            await self.validate_result(ctx, normalized)
            logger.debug("[%s] Result validated | cid=%s", self.config.platform, ctx.correlation_id)

            result.success = True
            metrics.success = True

        except CollectorException:
            raise
        except Exception as exc:
            result.error = str(exc)
            logger.error(
                "[%s] Collection failed for '%s': %s | cid=%s",
                self.config.platform,
                ctx.username,
                exc,
                ctx.correlation_id,
                exc_info=True,
            )
            raise CollectorException(
                message=f"Collection failed: {exc}",
                platform=str(self.config.platform),
            ) from exc
        finally:
            metrics.finish()
            await self.teardown(ctx)
            logger.info(
                "[%s] Collection finished for '%s' | success=%s | duration=%.2fs | cid=%s",
                self.config.platform,
                ctx.username,
                result.success,
                metrics.duration_seconds,
                ctx.correlation_id,
            )

        return result
