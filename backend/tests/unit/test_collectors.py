"""Unit tests for concrete platform collectors (GitHub, LeetCode, Codeforces)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.collectors.base import CollectorConfig, CollectorContext
from app.collectors.exceptions import CollectorNotFoundException
from app.collectors.github.collector import GitHubCollector
from app.collectors.leetcode.collector import LeetCodeCollector
from app.collectors.codeforces.collector import CodeforcesCollector
from app.database.models.enums import PlatformType


# ── GitHubCollector Tests ───────────────────────────────────────────────────

class TestGitHubCollector:
    @pytest.mark.asyncio
    async def test_github_run_lifecycle_success(self):
        config = CollectorConfig(
            platform=PlatformType.GITHUB,
            base_url="https://api.github.com",
            api_token="test_token",
        )
        ctx = CollectorContext(username="octocat")

        collector = GitHubCollector(config)

        # Build a raw dict that matches what fetch_data would produce
        mock_raw = {
            "profile": {
                "name": "The Octocat",
                "avatar_url": "octo.png",
                "html_url": "https://github.com/octocat",
                "public_repos": 2,
                "followers": 100,
                "following": 10,
                "created_at": "2011-01-25T18:44:36Z",
            },
            "repositories": [
                {
                    "name": "hello-world",
                    "description": "A hello world repo",
                    "stargazers_count": 5,
                    "forks_count": 2,
                    "watchers_count": 5,
                    "html_url": "https://github.com/octocat/hello-world",
                    "language": "Python",
                    "fork": False,
                    "archived": False,
                    "topics": ["python"],
                    "open_issues_count": 1,
                    "created_at": "2011-01-25T18:44:36Z",
                    "updated_at": "2024-01-01T00:00:00Z",
                    "languages_breakdown": {"Python": 10000, "Shell": 500},
                    "_root_files": ["README.md", "Dockerfile"],
                    "_has_ci_cd": False,
                    "_has_docker": True,
                    "_has_tests": False,
                    "_package_managers": [],
                    "_frameworks": [],
                    "license": {"spdx_id": "MIT"},
                },
            ],
            "events": [],
            "organizations": [],
        }

        # Bypass fetch_data entirely — test only initialize→normalize→validate
        with (
            patch.object(collector, "initialize", AsyncMock()),
            patch.object(collector, "validate_input", AsyncMock()),
            patch.object(collector, "fetch_data", AsyncMock(return_value=mock_raw)),
            patch.object(collector, "teardown", AsyncMock()),
        ):
            res = await collector.run(ctx)

        assert res.success is True
        assert res.normalized is not None
        assert res.normalized.username == "octocat"
        assert res.normalized.display_name == "The Octocat"
        assert len(res.normalized.projects) == 1
        assert res.normalized.projects[0].name == "hello-world"
        assert res.normalized.has_docker is True
        assert "Python" in [s.name for s in res.normalized.skills]


# ── LeetCodeCollector Tests ──────────────────────────────────────────────────

class TestLeetCodeCollector:
    @pytest.mark.asyncio
    async def test_leetcode_gql_success(self):
        config = CollectorConfig(
            platform=PlatformType.LEETCODE,
            base_url="https://leetcode.com",
        )
        ctx = CollectorContext(username="leetcode_user")

        collector = LeetCodeCollector(config)

        mock_raw = {
            "matchedUser": {
                "username": "leetcode_user",
                "profile": {
                    "realName": "LeetCode King",
                    "userAvatar": "avatar.png",
                    "ranking": 100,
                    "aboutMe": "",
                    "reputation": 50,
                },
                "submitStats": {
                    "acSubmissionNum": [
                        {"difficulty": "All", "count": 150, "submissions": 300},
                        {"difficulty": "Easy", "count": 50, "submissions": 100},
                        {"difficulty": "Medium", "count": 70, "submissions": 140},
                        {"difficulty": "Hard", "count": 30, "submissions": 60},
                    ]
                },
                "badges": [],
                "tagProblemCounts": {"fundamental": [], "intermediate": [], "advanced": []},
            },
            "userContestRanking": {
                "attendedContestsCount": 5,
                "rating": 1600,
                "globalRanking": 500,
                "topPercentage": 1.5,
            },
        }

        # Bypass fetch_data — test only normalize
        with (
            patch.object(collector, "initialize", AsyncMock()),
            patch.object(collector, "validate_input", AsyncMock()),
            patch.object(collector, "fetch_data", AsyncMock(return_value=mock_raw)),
            patch.object(collector, "teardown", AsyncMock()),
        ):
            res = await collector.run(ctx)

        assert res.success is True
        assert res.normalized is not None
        assert res.normalized.problems_solved == 150
        assert res.normalized.easy_solved == 50
        assert res.normalized.rating == 1600


# ── CodeforcesCollector Tests ────────────────────────────────────────────────

class TestCodeforcesCollector:
    @pytest.mark.asyncio
    async def test_codeforces_rest_success(self):
        config = CollectorConfig(
            platform=PlatformType.CODEFORCES,
            base_url="https://codeforces.com/api",
        )
        ctx = CollectorContext(username="tourist")

        collector = CodeforcesCollector(config)

        mock_raw = {
            "user_info": {
                "handle": "tourist",
                "firstName": "Gennady",
                "lastName": "Korotkevich",
                "rating": 3800,
                "maxRating": 3800,
                "rank": "legendary grandmaster",
                "maxRank": "legendary grandmaster",
                "registrationTimeSeconds": 1265987288,
            },
            "rating_history": [],
            "submissions": [],
        }

        # Bypass fetch_data — test only normalize
        with (
            patch.object(collector, "initialize", AsyncMock()),
            patch.object(collector, "validate_input", AsyncMock()),
            patch.object(collector, "fetch_data", AsyncMock(return_value=mock_raw)),
            patch.object(collector, "teardown", AsyncMock()),
        ):
            res = await collector.run(ctx)

        assert res.success is True
        assert res.normalized is not None
        assert res.normalized.display_name == "Gennady Korotkevich"
        assert res.normalized.rating == 3800
        assert res.normalized.rank == "legendary grandmaster"
