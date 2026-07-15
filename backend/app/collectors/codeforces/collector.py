"""Codeforces platform collector.

Uses the official Codeforces API to collect user profile information,
contest history, and past submission statistics. Normalizes tags to
map DSA algorithm proficiencies.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from app.collectors.base import BaseCollector, CollectorConfig, CollectorContext
from app.collectors.exceptions import CollectorException, CollectorParsingException
from app.collectors.utils import RateLimitHandler, RetryPolicy
from app.database.models.enums import PlatformType
from app.schemas.normalization import (
    UnifiedActivity,
    UnifiedPlatformProfile,
    UnifiedSkill,
)

logger = logging.getLogger(__name__)

# Topic mapping from Codeforces tags to internal Category/Keywords
TAG_MAP = {
    "dp": "Dynamic Programming",
    "graphs": "Graphs",
    "shortest paths": "Graphs",
    "dfs and similar": "Graphs",
    "greedy": "Greedy Algorithms",
    "trees": "Trees",
    "math": "Mathematics",
    "number theory": "Mathematics",
    "binary search": "Binary Search",
    "implementation": "Implementation",
    "data structures": "Data Structures",
    "strings": "Strings",
    "combinatorics": "Mathematics",
    "sorting": "Sorting Algorithms",
    "bitmasks": "Bit Manipulation",
}


class CodeforcesCollector(BaseCollector[dict[str, Any], UnifiedPlatformProfile]):
    """Collector for Codeforces profile and contest submissions using REST API."""

    def __init__(self, config: CollectorConfig) -> None:
        super().__init__(config)
        self._retry = RetryPolicy(
            max_retries=config.max_retries,
            base_delay=1.0,
            max_delay=60.0,
        )

    async def initialize(self, ctx: CollectorContext) -> None:
        """Create async HTTPX client for Codeforces."""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
        )

    async def validate_input(self, ctx: CollectorContext) -> None:
        """Validate the Codeforces handle (username)."""
        username = ctx.username.strip()
        if not username or len(username) > 50:
            raise CollectorException(
                message=f"Invalid Codeforces handle: '{username}'",
                platform="CODEFORCES",
            )
        # CF handles are letters, digits, underscores, dashes, 3-24 chars usually
        if not re.match(r"^[a-zA-Z0-9_\-]{3,24}$", username):
            raise CollectorException(
                message=f"Invalid Codeforces handle format: '{username}'",
                platform="CODEFORCES",
            )

    async def fetch_data(self, ctx: CollectorContext) -> dict[str, Any]:
        """Fetch stats from official Codeforces API endpoints."""
        raw: dict[str, Any] = {}

        # 1. User profile info
        info_resp = await self._get_cf(f"/user.info?handles={ctx.username}", ctx)
        if not info_resp.get("result"):
            raise CollectorException(
                message=f"Failed to fetch user.info for '{ctx.username}'",
                platform="CODEFORCES",
            )
        raw["user_info"] = info_resp["result"][0]

        # 2. User rating/contest history
        try:
            rating_resp = await self._get_cf(f"/user.rating?handle={ctx.username}", ctx)
            raw["rating_history"] = rating_resp.get("result", [])
        except Exception:
            raw["rating_history"] = []

        # 3. User submissions (status)
        try:
            status_resp = await self._get_cf(f"/user.status?handle={ctx.username}&from=1&count=1000", ctx)
            raw["submissions"] = status_resp.get("result", [])
        except Exception:
            raw["submissions"] = []

        return raw

    async def normalize(
        self, ctx: CollectorContext, raw: dict[str, Any]
    ) -> UnifiedPlatformProfile:
        """Normalize Codeforces data into UnifiedPlatformProfile."""
        user = raw.get("user_info") or {}
        rating_history = raw.get("rating_history") or []
        submissions = raw.get("submissions") or []

        # Count accepted solutions and extract tags
        solved_problems: set[str] = set()
        tag_counts: dict[str, int] = {}
        activities: list[UnifiedActivity] = []

        for sub in submissions:
            # Codeforces status: OK = Accepted
            verdict = sub.get("verdict", "")
            prob = sub.get("problem", {})
            p_id = f"{prob.get('contestId')}_{prob.get('index')}"
            
            # Map activities
            sub_time = sub.get("creationTimeSeconds")
            activities.append(UnifiedActivity(
                activity_type="SUBMISSION",
                title=f"Submitted problem {prob.get('name', p_id)}",
                timestamp=datetime.fromtimestamp(sub_time, tz=timezone.utc) if sub_time else None,
                url=f"https://codeforces.com/contest/{prob.get('contestId')}/problem/{prob.get('index')}",
                metadata={"verdict": verdict, "problem_id": p_id},
            ))

            if verdict == "OK" and p_id not in solved_problems:
                solved_problems.add(p_id)
                for tag in prob.get("tags", []):
                    norm_tag = TAG_MAP.get(tag, tag.title())
                    tag_counts[norm_tag] = tag_counts.get(norm_tag, 0) + 1

        # Map tag counts to UnifiedSkills
        skills: list[UnifiedSkill] = []
        total_solves = len(solved_problems) or 1
        for tag, count in tag_counts.items():
            skills.append(UnifiedSkill(
                name=tag,
                category="PARADIGM",
                relevance_score=round(count / total_solves, 3),
                source="CODEFORCES",
            ))

        # Check contest consistency
        contest_count = len(rating_history)
        contest_consistency = min(1.0, contest_count / 15.0)

        # Parse joined timestamp if present
        registration_time = user.get("registrationTimeSeconds")
        joined_at = (
            datetime.fromtimestamp(registration_time, tz=timezone.utc)
            if registration_time
            else None
        )

        return UnifiedPlatformProfile(
            platform="CODEFORCES",
            username=ctx.username,
            display_name=f"{user.get('firstName', '')} {user.get('lastName', '')}".strip() or ctx.username,
            avatar_url=user.get("titlePhoto", ""),
            profile_url=f"https://codeforces.com/profile/{ctx.username}",
            joined_at=joined_at,
            rating=user.get("rating", 0),
            max_rating=user.get("maxRating", 0),
            rank=user.get("rank") or "",
            max_rank=user.get("maxRank") or "",
            problems_solved=len(solved_problems),
            contest_count=contest_count,
            skills=skills,
            activities=activities[:100],  # cap list of events
            contribution_consistency=contest_consistency,
            topic_distribution=tag_counts,
            extra={
                "contribution": user.get("contribution", 0),
                "friend_of_count": user.get("friendOfCount", 0),
            },
        )

    async def validate_result(
        self, ctx: CollectorContext, normalized: UnifiedPlatformProfile
    ) -> None:
        """Validate normalized user is set."""
        if not normalized.username:
            raise CollectorParsingException("Unified profile missing username.", "CODEFORCES")

    # ── CF API helpers ────────────────────────────────────────────────

    async def _get_cf(self, path: str, ctx: CollectorContext) -> Any:
        """Retrieve Codeforces API response with retry and 404 handler."""
        async def _do_get() -> Any:
            assert self._client is not None
            resp = await self._client.get(path)
            
            # Codeforces handles 404 differently, sometimes returns 400 with "handles: not found"
            if resp.status_code == 400:
                data = resp.json()
                comment = data.get("comment", "")
                if "not found" in comment.lower() or "handles:" in comment.lower():
                    RateLimitHandler.check_not_found(
                        httpx.Response(404, request=resp.request),
                        "CODEFORCES",
                        ctx.username,
                    )
            
            RateLimitHandler.check_response(resp, "CODEFORCES")
            RateLimitHandler.check_not_found(resp, "CODEFORCES", ctx.username)
            resp.raise_for_status()
            
            data = resp.json()
            if data.get("status") != "OK":
                raise CollectorException(
                    message=f"Codeforces API error: {data.get('comment')}",
                    platform="CODEFORCES",
                )
            return data

        return await self._retry.execute(_do_get)
