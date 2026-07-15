"""GitHub platform collector.

Collects user profile data, repositories, languages, topics, CI/CD presence,
Dockerfiles, testing frameworks, and contribution metrics using the GitHub
REST API via HTTPX async.
"""

import logging
import re
from datetime import datetime, timezone
from typing import Any

import httpx

from app.collectors.base import BaseCollector, CollectorConfig, CollectorContext
from app.collectors.exceptions import (
    CollectorException,
    CollectorNotFoundException,
    CollectorParsingException,
)
from app.collectors.utils import RateLimitHandler, RetryPolicy
from app.database.models.enums import PlatformType
from app.schemas.normalization import (
    UnifiedActivity,
    UnifiedPlatformProfile,
    UnifiedProject,
    UnifiedSkill,
)

logger = logging.getLogger(__name__)

# Technology inference maps
CI_CD_FILES = {
    ".github/workflows", "Jenkinsfile", ".gitlab-ci.yml",
    ".circleci", ".travis.yml", "azure-pipelines.yml",
    "bitbucket-pipelines.yml",
}
DOCKER_FILES = {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"}
TEST_PATTERNS = re.compile(
    r"(test_|_test\.py|\.test\.(js|ts)|spec\.(js|ts)|__tests__|pytest|jest|mocha|vitest)",
    re.IGNORECASE,
)
PACKAGE_MANAGERS = {
    "package.json": "npm/yarn",
    "requirements.txt": "pip",
    "Pipfile": "pipenv",
    "pyproject.toml": "poetry/pip",
    "go.mod": "go modules",
    "Cargo.toml": "cargo",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "Gemfile": "bundler",
    "composer.json": "composer",
}
FRAMEWORK_INDICATORS: dict[str, str] = {
    "next.config": "Next.js",
    "nuxt.config": "Nuxt.js",
    "angular.json": "Angular",
    "svelte.config": "Svelte",
    "vite.config": "Vite",
    "webpack.config": "Webpack",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "express": "Express.js",
    "nestjs": "NestJS",
    "spring": "Spring",
}
LANGUAGE_CATEGORY = {
    "Python": "LANGUAGE", "JavaScript": "LANGUAGE", "TypeScript": "LANGUAGE",
    "Java": "LANGUAGE", "Go": "LANGUAGE", "Rust": "LANGUAGE", "C++": "LANGUAGE",
    "C#": "LANGUAGE", "Ruby": "LANGUAGE", "PHP": "LANGUAGE", "Kotlin": "LANGUAGE",
    "Swift": "LANGUAGE", "Dart": "LANGUAGE", "Shell": "LANGUAGE", "Scala": "LANGUAGE",
}


class GitHubCollector(BaseCollector[dict[str, Any], UnifiedPlatformProfile]):
    """Concrete collector for GitHub profiles and repositories.

    Uses the GitHub REST API to gather user profile info, public repos,
    languages, commit counts, and infers engineering capabilities.
    """

    def __init__(self, config: CollectorConfig) -> None:
        super().__init__(config)
        self._retry = RetryPolicy(
            max_retries=config.max_retries,
            base_delay=1.0,
            max_delay=60.0,
        )

    # ── Lifecycle methods ─────────────────────────────────────────────

    async def initialize(self, ctx: CollectorContext) -> None:
        """Create an async HTTPX client with GitHub auth headers."""
        headers: dict[str, str] = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.config.api_token:
            headers["Authorization"] = f"Bearer {self.config.api_token}"

        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers=headers,
            timeout=self.config.timeout,
        )

    async def validate_input(self, ctx: CollectorContext) -> None:
        """Validate the GitHub username format."""
        username = ctx.username.strip()
        if not username or len(username) > 39:
            raise CollectorException(
                message=f"Invalid GitHub username: '{username}'",
                platform="GITHUB",
            )
        if not re.match(r"^[a-zA-Z0-9](?:[a-zA-Z0-9]|-(?=[a-zA-Z0-9])){0,38}$", username):
            raise CollectorException(
                message=f"Invalid GitHub username format: '{username}'",
                platform="GITHUB",
            )

    async def fetch_data(self, ctx: CollectorContext) -> dict[str, Any]:
        """Fetch user profile, repos, and repo details from GitHub REST API."""
        raw: dict[str, Any] = {}

        # 1. User profile
        profile = await self._get(f"/users/{ctx.username}", ctx)
        raw["profile"] = profile

        # 2. Public repositories (paginated, up to 100)
        repos = await self._get_paginated(
            f"/users/{ctx.username}/repos?type=owner&sort=updated&per_page=100",
            ctx,
            max_pages=3,
        )
        raw["repositories"] = repos

        # 3. Per-repo details (languages, tree inspection for top repos)
        enriched_repos: list[dict[str, Any]] = []
        for repo in repos[:30]:  # Limit deep inspection to top 30
            repo_detail: dict[str, Any] = dict(repo)
            try:
                languages = await self._get(
                    f"/repos/{ctx.username}/{repo['name']}/languages", ctx
                )
                repo_detail["languages_breakdown"] = languages
            except Exception:
                repo_detail["languages_breakdown"] = {}

            # Check for CI/CD, Docker, tests via repo tree (root only)
            try:
                tree = await self._get(
                    f"/repos/{ctx.username}/{repo['name']}/contents", ctx
                )
                if isinstance(tree, list):
                    filenames = {item.get("name", "") for item in tree}
                    paths = {item.get("path", "") for item in tree}
                    repo_detail["_root_files"] = list(filenames)
                    repo_detail["_has_ci_cd"] = bool(
                        CI_CD_FILES & filenames or CI_CD_FILES & paths
                        or any(".github" in p for p in paths)
                    )
                    repo_detail["_has_docker"] = bool(DOCKER_FILES & filenames)
                    repo_detail["_has_tests"] = any(
                        TEST_PATTERNS.search(f) for f in filenames
                    )
                    repo_detail["_package_managers"] = [
                        PACKAGE_MANAGERS[f] for f in filenames if f in PACKAGE_MANAGERS
                    ]
                    repo_detail["_frameworks"] = [
                        FRAMEWORK_INDICATORS[k]
                        for k in FRAMEWORK_INDICATORS
                        if any(k in f for f in filenames)
                    ]
            except Exception:
                repo_detail["_root_files"] = []
                repo_detail["_has_ci_cd"] = False
                repo_detail["_has_docker"] = False
                repo_detail["_has_tests"] = False

            enriched_repos.append(repo_detail)

        raw["repositories"] = enriched_repos

        # 4. Recent events (contributions)
        try:
            events = await self._get(
                f"/users/{ctx.username}/events/public?per_page=100", ctx
            )
            raw["events"] = events
        except Exception:
            raw["events"] = []

        # 5. Organizations
        try:
            orgs = await self._get(f"/users/{ctx.username}/orgs", ctx)
            raw["organizations"] = orgs
        except Exception:
            raw["organizations"] = []

        return raw

    async def normalize(
        self, ctx: CollectorContext, raw: dict[str, Any]
    ) -> UnifiedPlatformProfile:
        """Transform raw GitHub data into a UnifiedPlatformProfile."""
        profile_data = raw.get("profile", {})
        repos_data = raw.get("repositories", [])
        events_data = raw.get("events", [])

        # Aggregate language bytes across all repos
        all_languages: dict[str, int] = {}
        for repo in repos_data:
            for lang, bytes_count in repo.get("languages_breakdown", {}).items():
                all_languages[lang] = all_languages.get(lang, 0) + bytes_count

        total_bytes = sum(all_languages.values()) or 1
        primary_language = max(all_languages, key=all_languages.get) if all_languages else ""

        # Build skills from languages
        skills: list[UnifiedSkill] = []
        for lang, byte_count in sorted(all_languages.items(), key=lambda x: -x[1]):
            skills.append(UnifiedSkill(
                name=lang,
                category=LANGUAGE_CATEGORY.get(lang, "LANGUAGE"),
                relevance_score=round(byte_count / total_bytes, 3),
                source="GITHUB",
            ))

        # Detect frameworks from repo data
        seen_frameworks: set[str] = set()
        for repo in repos_data:
            for fw in repo.get("_frameworks", []):
                if fw not in seen_frameworks:
                    seen_frameworks.add(fw)
                    skills.append(UnifiedSkill(
                        name=fw, category="FRAMEWORK", relevance_score=0.7, source="GITHUB"
                    ))

        # Build projects
        projects: list[UnifiedProject] = []
        has_ci_cd_global = False
        has_docker_global = False
        has_tests_global = False

        for repo in repos_data:
            if repo.get("_has_ci_cd"):
                has_ci_cd_global = True
            if repo.get("_has_docker"):
                has_docker_global = True
            if repo.get("_has_tests"):
                has_tests_global = True

            projects.append(UnifiedProject(
                name=repo.get("name", ""),
                description=repo.get("description") or "",
                url=repo.get("html_url", ""),
                primary_language=repo.get("language") or "",
                languages=list(repo.get("languages_breakdown", {}).keys()),
                topics=repo.get("topics", []),
                stars=repo.get("stargazers_count", 0),
                forks=repo.get("forks_count", 0),
                watchers=repo.get("watchers_count", 0),
                is_fork=repo.get("fork", False),
                is_archived=repo.get("archived", False),
                has_ci_cd=repo.get("_has_ci_cd", False),
                has_docker=repo.get("_has_docker", False),
                has_tests=repo.get("_has_tests", False),
                license_name=(repo.get("license") or {}).get("spdx_id", ""),
                created_at=self._parse_dt(repo.get("created_at")),
                updated_at=self._parse_dt(repo.get("updated_at")),
                open_issues=repo.get("open_issues_count", 0),
            ))

        # Build activities from events
        activities: list[UnifiedActivity] = []
        for event in events_data[:50]:
            activity_type_map = {
                "PushEvent": "COMMIT",
                "PullRequestEvent": "PR",
                "IssuesEvent": "ISSUE",
                "ReleaseEvent": "RELEASE",
                "CreateEvent": "COMMIT",
            }
            etype = event.get("type", "")
            activities.append(UnifiedActivity(
                activity_type=activity_type_map.get(etype, etype),
                title=f"{etype} on {event.get('repo', {}).get('name', '')}",
                timestamp=self._parse_dt(event.get("created_at")),
                url="",
                metadata={"event_type": etype},
            ))

        # Calculate contribution consistency (how many of last 90 events are recent)
        contribution_consistency = min(1.0, len(events_data) / 100.0)

        total_stars = sum(r.get("stargazers_count", 0) for r in repos_data)

        return UnifiedPlatformProfile(
            platform="GITHUB",
            username=ctx.username,
            display_name=profile_data.get("name") or ctx.username,
            avatar_url=profile_data.get("avatar_url", ""),
            bio=profile_data.get("bio") or "",
            location=profile_data.get("location") or "",
            profile_url=profile_data.get("html_url", ""),
            joined_at=self._parse_dt(profile_data.get("created_at")),
            followers=profile_data.get("followers", 0),
            following=profile_data.get("following", 0),
            public_repos=profile_data.get("public_repos", 0),
            total_contributions=total_stars,
            primary_language=primary_language,
            skills=skills,
            projects=projects,
            activities=activities,
            has_ci_cd=has_ci_cd_global,
            has_docker=has_docker_global,
            has_tests=has_tests_global,
            contribution_consistency=contribution_consistency,
            technology_breadth=len(all_languages),
            extra={
                "organizations": [
                    org.get("login") for org in raw.get("organizations", [])
                ],
                "total_stars_received": total_stars,
            },
        )

    async def validate_result(
        self, ctx: CollectorContext, normalized: UnifiedPlatformProfile
    ) -> None:
        """Ensure the normalized profile has at minimum the username set."""
        if not normalized.username:
            raise CollectorParsingException(
                message="Normalized GitHub profile missing username.",
                platform="GITHUB",
            )

    # ── HTTP helpers ──────────────────────────────────────────────────

    async def _get(self, path: str, ctx: CollectorContext) -> Any:
        """Execute an authenticated GET request with retry and rate-limit handling."""
        async def _do_get() -> Any:
            assert self._client is not None
            response = await self._client.get(path)
            RateLimitHandler.check_response(response, "GITHUB")
            RateLimitHandler.check_not_found(response, "GITHUB", ctx.username)
            response.raise_for_status()
            ctx_metrics = getattr(ctx, "_metrics", None)
            return response.json()

        result = await self._retry.execute(_do_get)
        return result

    async def _get_paginated(
        self, url: str, ctx: CollectorContext, max_pages: int = 3
    ) -> list[dict[str, Any]]:
        """Fetch multiple pages of a GitHub list endpoint."""
        all_items: list[dict[str, Any]] = []
        current_url = url

        for page in range(max_pages):
            async def _do_page() -> httpx.Response:
                assert self._client is not None
                resp = await self._client.get(current_url)
                RateLimitHandler.check_response(resp, "GITHUB")
                resp.raise_for_status()
                return resp

            response = await self._retry.execute(_do_page)
            items = response.json()
            if not isinstance(items, list) or not items:
                break
            all_items.extend(items)

            # Follow Link: <url>; rel="next"
            link_header = response.headers.get("Link", "")
            next_match = re.search(r'<([^>]+)>;\s*rel="next"', link_header)
            if not next_match:
                break
            current_url = next_match.group(1)
            # Strip base_url prefix if present for relative path
            if current_url.startswith(self.config.base_url):
                current_url = current_url[len(self.config.base_url):]

        return all_items

    @staticmethod
    def _parse_dt(value: str | None) -> datetime | None:
        """Parse an ISO 8601 datetime string."""
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return None
