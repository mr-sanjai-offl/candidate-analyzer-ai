"""Schemas package — Pydantic models for request/response validation."""

from app.schemas.analysis import AnalysisCreate, AnalysisHistorySchema, AnalysisResponse
from app.schemas.auth import (
    MessageResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.schemas.candidate import (
    CandidateProfileCreate,
    CandidateProfileResponse,
    CandidateProfileUpdate,
    CandidateSkillSchema,
    CodeforcesProfileSchema,
    GithubProfileSchema,
    LeetCodeProfileSchema,
    ProjectCreate,
    ProjectSchema,
)
from app.schemas.health import HealthResponse
from app.schemas.job import BackgroundJobResponse
from app.schemas.resume import (
    ResumeDetailResponse,
    ResumeExtractionResponse,
    ResumeResponse,
    ResumeUploadResponse,
)

__all__ = [
    "HealthResponse",
    "UserRegisterRequest",
    "UserLoginRequest",
    "TokenResponse",
    "TokenRefreshRequest",
    "UserResponse",
    "MessageResponse",
    "CandidateProfileCreate",
    "CandidateProfileUpdate",
    "CandidateProfileResponse",
    "GithubProfileSchema",
    "LeetCodeProfileSchema",
    "CodeforcesProfileSchema",
    "ProjectSchema",
    "ProjectCreate",
    "CandidateSkillSchema",
    "AnalysisCreate",
    "AnalysisResponse",
    "AnalysisHistorySchema",
    "BackgroundJobResponse",
    "ResumeResponse",
    "ResumeDetailResponse",
    "ResumeExtractionResponse",
    "ResumeUploadResponse",
]
