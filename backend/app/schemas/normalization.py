"""Unified normalization schemas.

Platform-agnostic Pydantic models that every collector normalizes into.
No platform-specific logic should leak outside collectors — downstream
services only consume these schemas.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class UnifiedSkill(BaseModel):
    """A single technology or skill detected from platform data."""

    name: str = Field(..., description="Skill or technology name (e.g. 'Python', 'React').")
    category: str = Field(
        default="OTHER",
        description="Category: LANGUAGE, FRAMEWORK, DATABASE, TOOL, CLOUD, PARADIGM, OTHER.",
    )
    relevance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence score 0–1."
    )
    source: str = Field(default="", description="Platform that detected this skill.")


class UnifiedProject(BaseModel):
    """Normalized representation of a code repository or project."""

    name: str
    description: str = ""
    url: str = ""
    primary_language: str = ""
    languages: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    stars: int = 0
    forks: int = 0
    watchers: int = 0
    is_fork: bool = False
    is_archived: bool = False
    has_ci_cd: bool = False
    has_docker: bool = False
    has_tests: bool = False
    license_name: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    commit_count: int = 0
    open_issues: int = 0
    contributors_count: int = 0


class UnifiedActivity(BaseModel):
    """A single activity event (commit, submission, contest, PR)."""

    activity_type: str = Field(
        ..., description="Type: COMMIT, SUBMISSION, CONTEST, PR, ISSUE, RELEASE."
    )
    title: str = ""
    timestamp: Optional[datetime] = None
    url: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class UnifiedAchievement(BaseModel):
    """A notable achievement or badge."""

    name: str
    description: str = ""
    achieved_at: Optional[datetime] = None
    platform: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class UnifiedTimeline(BaseModel):
    """Aggregated chronological activity summary."""

    period: str = Field(..., description="ISO date or period label (e.g. '2024-01', 'Q1-2024').")
    activity_count: int = 0
    details: dict[str, Any] = Field(default_factory=dict)


class UnifiedPlatformProfile(BaseModel):
    """Top-level unified profile combining all normalized platform data.

    This is the single output schema that every collector produces.
    Downstream services (scoring, reports) consume only this model.
    """

    platform: str
    username: str
    display_name: str = ""
    avatar_url: str = ""
    bio: str = ""
    location: str = ""
    profile_url: str = ""
    joined_at: Optional[datetime] = None

    # Aggregated metrics
    followers: int = 0
    following: int = 0
    public_repos: int = 0
    total_contributions: int = 0
    rating: int = 0
    max_rating: int = 0
    rank: str = ""
    max_rank: str = ""

    # Problem solving (LeetCode / Codeforces)
    problems_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    acceptance_rate: float = 0.0
    contest_count: int = 0

    # Inferred capabilities
    primary_language: str = ""
    skills: list[UnifiedSkill] = Field(default_factory=list)
    projects: list[UnifiedProject] = Field(default_factory=list)
    activities: list[UnifiedActivity] = Field(default_factory=list)
    achievements: list[UnifiedAchievement] = Field(default_factory=list)
    timeline: list[UnifiedTimeline] = Field(default_factory=list)

    # Engineering maturity indicators
    has_ci_cd: bool = False
    has_docker: bool = False
    has_tests: bool = False
    uses_monorepo: bool = False
    contribution_consistency: float = 0.0  # 0–1 score
    technology_breadth: int = 0  # number of unique technologies

    # Topic distribution (for LeetCode/Codeforces)
    topic_distribution: dict[str, int] = Field(default_factory=dict)

    # Raw extra data that doesn't fit the schema
    extra: dict[str, Any] = Field(default_factory=dict)
