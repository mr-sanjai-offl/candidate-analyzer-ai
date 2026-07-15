"""LeetCode platform collector.

Uses LeetCode's public GraphQL API to fetch user stats, problem solving metrics,
contest ratings, badges, and topic distribution.
"""

import logging
import re
from typing import Any

import httpx

from app.collectors.base import BaseCollector, CollectorConfig, CollectorContext
from app.collectors.exceptions import CollectorException, CollectorParsingException
from app.collectors.utils import RateLimitHandler, RetryPolicy
from app.database.models.enums import PlatformType
from app.schemas.normalization import (
    UnifiedAchievement,
    UnifiedActivity,
    UnifiedPlatformProfile,
    UnifiedSkill,
)

logger = logging.getLogger(__name__)


class LeetCodeCollector(BaseCollector[dict[str, Any], UnifiedPlatformProfile]):
    """Collector for LeetCode profile metrics using GraphQL."""

    def __init__(self, config: CollectorConfig) -> None:
        super().__init__(config)
        self._retry = RetryPolicy(
            max_retries=config.max_retries,
            base_delay=1.0,
            max_delay=60.0,
        )

    async def initialize(self, ctx: CollectorContext) -> None:
        """Initialize HTTPX async client for LeetCode GraphQL."""
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com",
            },
        )

    async def validate_input(self, ctx: CollectorContext) -> None:
        """Validate the LeetCode username."""
        username = ctx.username.strip()
        if not username or len(username) > 50:
            raise CollectorException(
                message=f"Invalid LeetCode username: '{username}'",
                platform="LEETCODE",
            )
        if not re.match(r"^[a-zA-Z0-9_\-]{3,50}$", username):
            raise CollectorException(
                message=f"Invalid LeetCode username format: '{username}'",
                platform="LEETCODE",
            )

    async def fetch_data(self, ctx: CollectorContext) -> dict[str, Any]:
        """Fetch LeetCode stats using a aggregated GraphQL query."""
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                profile {
                    realName
                    aboutMe
                    userAvatar
                    reputation
                    ranking
                }
                submitStats {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
                badges {
                    id
                    name
                    displayName
                    icon
                }
                tagProblemCounts {
                    advanced {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                    intermediate {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                    fundamental {
                        tagName
                        tagSlug
                        problemsSolved
                    }
                }
            }
            userContestRanking(username: $username) {
                attendedContestsCount
                rating
                globalRanking
                totalParticipants
                topPercentage
                badge {
                    name
                }
            }
        }
        """
        payload = {
            "query": query,
            "variables": {"username": ctx.username},
        }

        async def _execute_gql() -> httpx.Response:
            assert self._client is not None
            resp = await self._client.post("/graphql", json=payload)
            RateLimitHandler.check_response(resp, "LEETCODE")
            resp.raise_for_status()
            return resp

        response = await self._retry.execute(_execute_gql)
        data = response.json()

        if "errors" in data and data["errors"]:
            # If LeetCode returns user not found
            err_msg = data["errors"][0].get("message", "")
            if "not exist" in err_msg.lower() or "not found" in err_msg.lower():
                RateLimitHandler.check_not_found(
                    httpx.Response(404, request=response.request),
                    "LEETCODE",
                    ctx.username,
                )
            raise CollectorException(
                message=f"LeetCode GraphQL error: {err_msg}",
                platform="LEETCODE",
            )

        user_data = data.get("data", {}).get("matchedUser")
        if not user_data:
            # Another form of not found
            RateLimitHandler.check_not_found(
                httpx.Response(404, request=response.request),
                "LEETCODE",
                ctx.username,
            )

        return data.get("data", {})

    async def normalize(
        self, ctx: CollectorContext, raw: dict[str, Any]
    ) -> UnifiedPlatformProfile:
        """Normalize GraphQL data into UnifiedPlatformProfile."""
        user = raw.get("matchedUser") or {}
        profile = user.get("profile") or {}
        contest = raw.get("userContestRanking") or {}
        submit_stats = user.get("submitStats", {}).get("acSubmissionNum") or []
        badges = user.get("badges") or []
        tags = user.get("tagProblemCounts") or {}

        # Resolve solved counts
        solved_map = {item["difficulty"]: item["count"] for item in submit_stats}
        easy = solved_map.get("Easy", 0)
        medium = solved_map.get("Medium", 0)
        hard = solved_map.get("Hard", 0)
        total = solved_map.get("All", 0)

        # Build achievements
        achievements: list[UnifiedAchievement] = []
        for badge in badges:
            achievements.append(UnifiedAchievement(
                name=badge.get("displayName") or badge.get("name", ""),
                description=badge.get("displayName") or "",
                platform="LEETCODE",
                metadata={"icon": badge.get("icon", "")},
            ))

        # Skill tags mapping from LeetCode categories
        skills: list[UnifiedSkill] = []
        topic_distribution: dict[str, int] = {}
        for category in ["fundamental", "intermediate", "advanced"]:
            for item in tags.get(category, []):
                tname = item.get("tagName", "")
                psolved = item.get("problemsSolved", 0)
                if psolved > 0:
                    topic_distribution[tname] = psolved
                    skills.append(UnifiedSkill(
                        name=tname,
                        category="PARADIGM",
                        relevance_score=min(1.0, psolved / 10.0),
                        source="LEETCODE",
                    ))

        # Inferred acceptance rate
        all_ac = solved_map.get("All", 0)
        all_sub = sum(
            item.get("submissions", 0) for item in submit_stats if item["difficulty"] == "All"
        )
        acceptance_rate = (all_ac / all_sub * 100.0) if all_sub > 0 else 0.0

        return UnifiedPlatformProfile(
            platform="LEETCODE",
            username=ctx.username,
            display_name=profile.get("realName") or ctx.username,
            avatar_url=profile.get("userAvatar", ""),
            bio=profile.get("aboutMe") or "",
            profile_url=f"https://leetcode.com/{ctx.username}",
            ranking=profile.get("ranking", 0),
            problems_solved=total,
            easy_solved=easy,
            medium_solved=medium,
            hard_solved=hard,
            rating=int(contest.get("rating", 0)),
            contest_count=contest.get("attendedContestsCount", 0),
            acceptance_rate=round(acceptance_rate, 2),
            skills=skills,
            achievements=achievements,
            topic_distribution=topic_distribution,
            extra={
                "reputation": profile.get("reputation", 0),
                "contest_global_ranking": contest.get("globalRanking", 0),
                "contest_top_percentage": contest.get("topPercentage", 0.0),
            },
        )

    async def validate_result(
        self, ctx: CollectorContext, normalized: UnifiedPlatformProfile
    ) -> None:
        """Validate normalized user is set."""
        if not normalized.username:
            raise CollectorParsingException("Unified profile missing username.", "LEETCODE")
