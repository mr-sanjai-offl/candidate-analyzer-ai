"""Unit tests for the platform collector framework utilities."""

import asyncio

import pytest
import httpx
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.exceptions import (
    CollectorNotFoundException,
    CollectorRateLimitException,
    CollectorTimeoutException,
)
from app.collectors.utils import RateLimitHandler, RetryPolicy, CacheManager


# ── RateLimitHandler Tests ───────────────────────────────────────────────────

class TestRateLimitHandler:
    def test_handles_429_status(self):
        response = httpx.Response(429, headers={"Retry-After": "30"})
        with pytest.raises(CollectorRateLimitException) as exc:
            RateLimitHandler.check_response(response, "GITHUB")
        assert exc.value.retry_after == 30
        assert exc.value.platform == "GITHUB"

    def test_preemptive_detection_remaining_zero(self):
        response = httpx.Response(200, headers={"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "9999999999"})
        with pytest.raises(CollectorRateLimitException):
            RateLimitHandler.check_response(response, "GITHUB")

    def test_check_not_found(self):
        response = httpx.Response(404)
        with pytest.raises(CollectorNotFoundException) as exc:
            RateLimitHandler.check_not_found(response, "LEETCODE", "fake_user")
        assert exc.value.platform == "LEETCODE"


# ── RetryPolicy Tests ─────────────────────────────────────────────────────────

class TestRetryPolicy:
    @pytest.mark.asyncio
    async def test_successful_execution(self):
        policy = RetryPolicy(max_retries=2)
        mock_func = AsyncMock(return_value="success")

        result = await policy.execute(mock_func)
        assert result == "success"
        mock_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_retries_on_rate_limit(self):
        policy = RetryPolicy(max_retries=2, base_delay=0.01, jitter=0.0)
        mock_func = AsyncMock(
            side_effect=[
                CollectorRateLimitException(retry_after=0, platform="TEST"),
                "success",
            ]
        )

        with patch("app.collectors.utils.asyncio.sleep", new_callable=AsyncMock):
            result = await policy.execute(mock_func)

        assert result == "success"
        assert mock_func.call_count == 2

    @pytest.mark.asyncio
    async def test_exhausts_retries(self):
        policy = RetryPolicy(max_retries=1, base_delay=0.01, jitter=0.0)
        mock_func = AsyncMock(side_effect=httpx.TimeoutException("Timed out"))

        with patch("app.collectors.utils.asyncio.sleep", new_callable=AsyncMock):
            with pytest.raises(httpx.TimeoutException):
                await policy.execute(mock_func)

        assert mock_func.call_count == 2


# ── CacheManager Tests ────────────────────────────────────────────────────────

class TestCacheManager:
    @pytest.mark.asyncio
    async def test_cache_hit(self):
        mock_redis = AsyncMock()
        mock_redis.get.return_value = '{"foo": "bar"}'
        manager = CacheManager(mock_redis)

        key = CacheManager.build_key("GITHUB", "john_doe")
        data = await manager.get(key)
        assert data == {"foo": "bar"}
        mock_redis.get.assert_called_once_with(key)

    @pytest.mark.asyncio
    async def test_cache_set(self):
        mock_redis = AsyncMock()
        manager = CacheManager(mock_redis)

        key = CacheManager.build_key("LEETCODE", "candidate1")
        await manager.set(key, {"stats": 12}, ttl=60)
        mock_redis.set.assert_called_once_with(key, '{"stats": 12}', ex=60)
