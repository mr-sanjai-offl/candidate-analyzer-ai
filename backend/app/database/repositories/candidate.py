"""Candidate repository layer.

Provides database access operations for candidate profiles and related models.
"""

from typing import Type

from app.database.models.candidate_profile import CandidateProfile
from app.database.models.codeforces_profile import CodeforcesProfile
from app.database.models.github_profile import GithubProfile
from app.database.models.leetcode_profile import LeetCodeProfile
from app.database.models.project import Project
from app.database.models.uploaded_file import UploadedFile
from app.database.repositories.base import BaseRepository
from app.schemas.candidate import (
    CandidateProfileCreate,
    CandidateProfileUpdate,
    ProjectCreate,
)


class CandidateProfileRepository(
    BaseRepository[CandidateProfile, CandidateProfileCreate, CandidateProfileUpdate]
):
    """Repository for CandidateProfile model."""
    pass


class GithubProfileRepository(
    BaseRepository[GithubProfile, Type[dict], Type[dict]]
):
    """Repository for GithubProfile model."""
    pass


class LeetCodeProfileRepository(
    BaseRepository[LeetCodeProfile, Type[dict], Type[dict]]
):
    """Repository for LeetCodeProfile model."""
    pass


class CodeforcesProfileRepository(
    BaseRepository[CodeforcesProfile, Type[dict], Type[dict]]
):
    """Repository for CodeforcesProfile model."""
    pass


class ProjectRepository(
    BaseRepository[Project, ProjectCreate, Type[dict]]
):
    """Repository for Project model."""
    pass


class UploadedFileRepository(
    BaseRepository[UploadedFile, Type[dict], Type[dict]]
):
    """Repository for UploadedFile model."""
    pass
