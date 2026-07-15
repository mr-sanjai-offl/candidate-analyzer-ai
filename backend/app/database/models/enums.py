"""Shared enumerations for database models.

This module contains the shared Enums used across the core database domain
to prevent circular imports and maintain a single source of truth for choices.
"""

import enum


class ProjectType(enum.StrEnum):
    """Types of software engineering projects."""
    PERSONAL = "PERSONAL"
    OPEN_SOURCE = "OPEN_SOURCE"
    PROFESSIONAL = "PROFESSIONAL"
    ACADEMIC = "ACADEMIC"


class AnalysisState(enum.StrEnum):
    """Lifecycle states of a candidate analysis report."""
    PENDING = "PENDING"
    COLLECTING = "COLLECTING"
    ANALYZING = "ANALYZING"
    SCORING = "SCORING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PlatformType(enum.StrEnum):
    """Supported third-party platforms."""
    GITHUB = "GITHUB"
    LEETCODE = "LEETCODE"
    CODEFORCES = "CODEFORCES"


class JobStatus(enum.StrEnum):
    """Status of background jobs."""
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    RETRY = "RETRY"
    CANCELLED = "CANCELLED"


class SkillCategory(enum.StrEnum):
    """Categories for extracted skills."""
    LANGUAGE = "LANGUAGE"
    FRAMEWORK = "FRAMEWORK"
    DATABASE = "DATABASE"
    TOOL = "TOOL"
    CLOUD = "CLOUD"
    PARADIGM = "PARADIGM"
    OTHER = "OTHER"
