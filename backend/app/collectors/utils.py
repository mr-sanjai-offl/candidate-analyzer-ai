"""Collector utilities: retry policy, rate-limit handling, and caching.

These are shared across all concrete collectors so that retry logic,
backoff calculations, and cache operations are never duplicated.
"""

import asyncio
import hashlib
import json
import logging
import random
import time
from typing import Any, Callable, TypeVar

import httpx

from app.collectors.exceptions import (
    CollectorNotFoundException,
    CollectorRateLimitException,
    CollectorTimeoutException,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RetryPolicy:
    """Implements HTTP retry with exponential backoff and jitter.

    Attributes:
        max_retries: Maximum number of retry attempts.
        base_delay: Initial delay in seconds before the first retry.
        max_delay: Cap on the computed backoff delay.
        jitter: Maximum random jitter added to each delay.
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        jitter: float = 0.5,
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def compute_delay(self, attempt: int) -> float:
        """Calculate the backoff delay for the given attempt number."""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        delay += random.uniform(0, self.jitter)
        return delay

    async def execute(
        self,
        func: Callable[..., Any],
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Execute an async function with retry logic.

        Args:
            func: The async callable to retry.

        Returns:
            The return value of the successful call.

        Raises:
            The last exception if all retries are exhausted.
        """
        last_exception: Exception | None = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)
            except CollectorRateLimitException as exc:
                last_exception = exc
                wait = exc.retry_after or self.compute_delay(attempt)
                logger.warning(
                    "Rate limited (attempt %d/%d). Waiting %.1fs...",
                    attempt + 1,
                    self.max_retries + 1,
                    wait,
                )
                await asyncio.sleep(wait)
            except (httpx.TimeoutException, CollectorTimeoutException) as exc:
                last_exception = exc
                if attempt >= self.max_retries:
                    break
                wait = self.compute_delay(attempt)
                logger.warning(
                    "Timeout (attempt %d/%d). Retrying in %.1fs...",
                    attempt + 1,
                    self.max_retries + 1,
                    wait,
                )
                await asyncio.sleep(wait)
            except httpx.HTTPStatusError as exc:
                last_exception = exc
                if exc.response.status_code in (500, 502, 503):
                    if attempt >= self.max_retries:
                        break
                    wait = self.compute_delay(attempt)
                    logger.warning(
                        "Server error %d (attempt %d/%d). Retrying in %.1fs...",
                        exc.response.status_code,
                        attempt + 1,
                        self.max_retries + 1,
                        wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    raise

        raise last_exception  # type: ignore[misc]


class RateLimitHandler:
    """Detects and handles rate-limit responses from external APIs.

    Inspects HTTP response headers (``X-RateLimit-Remaining``,
    ``X-RateLimit-Reset``, ``Retry-After``) to determine when
    the next request can safely be made.
    """

    @staticmethod
    def check_response(response: httpx.Response, platform: str) -> None:
        """Raise CollectorRateLimitException if the response indicates throttling.

        Args:
            response: The HTTPX response to inspect.
            platform: Platform name for logging and exception context.

        Raises:
            CollectorRateLimitException: If the API is rate-limiting.
        """
        if response.status_code == 429:
            retry_after = RateLimitHandler._parse_retry_after(response)
            logger.warning(
                "[%s] Rate limited. retry_after=%s",
                platform,
                retry_after,
            )
            raise CollectorRateLimitException(
                retry_after=retry_after, platform=platform
            )

        # Preemptive detection: some APIs return 200 but signal exhaustion
        remaining = response.headers.get("X-RateLimit-Remaining")
        if remaining is not None and int(remaining) <= 0:
            reset_ts = response.headers.get("X-RateLimit-Reset")
            retry_after = None
            if reset_ts:
                retry_after = max(0, int(reset_ts) - int(time.time()))
            logger.warning(
                "[%s] Rate limit exhausted. remaining=0, retry_after=%s",
                platform,
                retry_after,
            )
            raise CollectorRateLimitException(
                retry_after=retry_after, platform=platform
            )

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> int | None:
        """Extract retry-after delay from response headers."""
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                return int(retry_after)
            except ValueError:
                return 60  # Fallback to 60s if header is non-numeric
        reset_ts = response.headers.get("X-RateLimit-Reset")
        if reset_ts:
            try:
                return max(0, int(reset_ts) - int(time.time()))
            except ValueError:
                pass
        return 60  # Conservative default

    @staticmethod
    def check_not_found(response: httpx.Response, platform: str, username: str) -> None:
        """Raise CollectorNotFoundException if user profile was not found."""
        if response.status_code == 404:
            raise CollectorNotFoundException(
                message=f"User '{username}' not found on {platform}",
                platform=platform,
                username=username,
            )


class CacheManager:
    """Simple cache operations using Redis for fetched platform payloads.

    Uses a key pattern of ``collector:{platform}:{username}:{data_type}``
    to namespace cached items.
    """

    def __init__(self, redis_client: Any = None) -> None:
        self._redis = redis_client

    @staticmethod
    def build_key(platform: str, username: str, data_type: str = "profile") -> str:
        """Build a namespaced cache key."""
        return f"collector:{platform.lower()}:{username.lower()}:{data_type}"

    async def get(self, key: str) -> dict[str, Any] | None:
        """Retrieve cached JSON payload by key."""
        if self._redis is None:
            return None
        try:
            raw = await self._redis.get(key)
            if raw:
                logger.debug("Cache HIT for key=%s", key)
                return json.loads(raw)
        except Exception as exc:
            logger.warning("Cache GET failed for key=%s: %s", key, exc)
        return None

    async def set(self, key: str, data: dict[str, Any], ttl: int = 3600) -> None:
        """Store a JSON payload in cache with a TTL."""
        if self._redis is None:
            return
        try:
            await self._redis.set(key, json.dumps(data, default=str), ex=ttl)
            logger.debug("Cache SET for key=%s ttl=%ds", key, ttl)
        except Exception as exc:
            logger.warning("Cache SET failed for key=%s: %s", key, exc)

    async def delete(self, key: str) -> None:
        """Remove a cached entry."""
        if self._redis is None:
            return
        try:
            await self._redis.delete(key)
        except Exception as exc:
            logger.warning("Cache DELETE failed for key=%s: %s", key, exc)
