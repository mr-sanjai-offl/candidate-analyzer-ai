"""Candidate schemas.

Defines the Pydantic models for CandidateProfiles, third-party profiles,
projects, and skills.
"""

import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from app.database.models.enums import PlatformType, ProjectType


class GithubProfileSchema(BaseModel):
    username: str = Field(..., max_length=255)
    repositories_count: int = 0
    stars_received: int = 0
    followers: int = 0
    total_commits: int = 0

    model_config = ConfigDict(from_attributes=True)


class LeetCodeProfileSchema(BaseModel):
    username: str = Field(..., max_length=255)
    problems_solved: int = 0
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    ranking: int = 0

    model_config = ConfigDict(from_attributes=True)


class CodeforcesProfileSchema(BaseModel):
    username: str = Field(..., max_length=255)
    rating: int = 0
    max_rating: int = 0
    rank: Optional[str] = None
    max_rank: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectSchema(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    project_type: ProjectType
    url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    project_type: ProjectType = ProjectType.PERSONAL
    url: Optional[str] = None


class CandidateSkillSchema(BaseModel):
    skill_id: uuid.UUID
    skill_name: str
    proficiency_score: float

    model_config = ConfigDict(from_attributes=True)


class CandidateProfileBase(BaseModel):
    bio: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None


class CandidateProfileCreate(CandidateProfileBase):
    pass


class CandidateProfileUpdate(CandidateProfileBase):
    pass


class CandidateProfileResponse(CandidateProfileBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    github_profiles: List[GithubProfileSchema] = []
    leetcode_profiles: List[LeetCodeProfileSchema] = []
    codeforces_profiles: List[CodeforcesProfileSchema] = []
    projects: List[ProjectSchema] = []

    model_config = ConfigDict(from_attributes=True)
