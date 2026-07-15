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


class ProficiencyLevel(enum.StrEnum):
    """Calculated proficiency levels."""
    BEGINNER = "BEGINNER"
    INTERMEDIATE = "INTERMEDIATE"
    ADVANCED = "ADVANCED"
    EXPERT = "EXPERT"


class GraphNodeType(enum.StrEnum):
    """Node types in the skill knowledge graph."""
    SKILL = "SKILL"
    PROJECT = "PROJECT"
    PLATFORM = "PLATFORM"
    EVIDENCE = "EVIDENCE"


class GraphRelationshipType(enum.StrEnum):
    """Relationship types in the skill knowledge graph."""
    KNOWS = "KNOWS"
    USES = "USES"
    IMPLEMENTS = "IMPLEMENTS"
    PROVES = "PROVES"
    CLAIMS = "CLAIMS"


class EvidenceSource(enum.StrEnum):
    """Sources of skill evaluation evidence."""
    RESUME = "RESUME"
    GITHUB = "GITHUB"
    LEETCODE = "LEETCODE"
    CODEFORCES = "CODEFORCES"
    PROJECT = "PROJECT"
    COMMIT = "COMMIT"

