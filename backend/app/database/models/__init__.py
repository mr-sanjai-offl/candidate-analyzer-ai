"""Database models package — SQLAlchemy ORM model definitions."""

from app.database.models.analysis import Analysis, AnalysisHistory
from app.database.models.background_job import BackgroundJob
from app.database.models.candidate_profile import CandidateProfile
from app.database.models.candidate_skill import CandidateSkill
from app.database.models.codeforces_profile import CodeforcesProfile
from app.database.models.enums import (
    AnalysisState,
    JobStatus,
    PlatformType,
    ProjectType,
    SkillCategory,
)
from app.database.models.github_profile import GithubProfile
from app.database.models.leetcode_profile import LeetCodeProfile
from app.database.models.project import Project
from app.database.models.platform_sync import PlatformSync
from app.database.models.refresh_token import RefreshToken
from app.database.models.resume import (
    ParsingState,
    ResumeExtraction,
    ResumeMetadata,
    ResumeVersion,
    UploadedResume,
)
from app.database.models.skill import Skill
from app.database.models.uploaded_file import UploadedFile
from app.database.models.user import User, UserRole

__all__ = [
    "Analysis",
    "AnalysisHistory",
    "AnalysisState",
    "BackgroundJob",
    "CandidateProfile",
    "CandidateSkill",
    "CodeforcesProfile",
    "GithubProfile",
    "JobStatus",
    "LeetCodeProfile",
    "PlatformType",
    "PlatformSync",
    "Project",
    "ProjectType",
    "RefreshToken",
    "Skill",
    "SkillCategory",
    "UploadedFile",
    "UploadedResume",
    "ResumeVersion",
    "ResumeMetadata",
    "ResumeExtraction",
    "ParsingState",
    "User",
    "UserRole",
]
