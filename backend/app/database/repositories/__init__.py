"""Repository package — Database access operations."""

from app.database.repositories.analysis import AnalysisHistoryRepository, AnalysisRepository
from app.database.repositories.base import BaseRepository
from app.database.repositories.candidate import (
    CandidateProfileRepository,
    CodeforcesProfileRepository,
    GithubProfileRepository,
    LeetCodeProfileRepository,
    ProjectRepository,
    UploadedFileRepository,
)
from app.database.repositories.job import BackgroundJobRepository
from app.database.repositories.resume import (
    ResumeExtractionRepository,
    ResumeVersionRepository,
    UploadedResumeRepository,
)
from app.database.repositories.skill import CandidateSkillRepository, SkillRepository

__all__ = [
    "BaseRepository",
    "CandidateProfileRepository",
    "GithubProfileRepository",
    "LeetCodeProfileRepository",
    "CodeforcesProfileRepository",
    "ProjectRepository",
    "UploadedFileRepository",
    "AnalysisRepository",
    "AnalysisHistoryRepository",
    "BackgroundJobRepository",
    "SkillRepository",
    "CandidateSkillRepository",
    "UploadedResumeRepository",
    "ResumeVersionRepository",
    "ResumeExtractionRepository",
]
