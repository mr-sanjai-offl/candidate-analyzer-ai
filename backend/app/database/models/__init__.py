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
    ProficiencyLevel,
    GraphNodeType,
    GraphRelationshipType,
    EvidenceSource,
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
from app.database.models.skill_graph import SkillGraphNode, SkillGraphEdge
from app.database.models.capability_score import CapabilityScore
from app.database.models.evidence import Evidence
from app.database.models.aliases import SkillAlias, TechnologyAlias
from app.database.models.readiness_report import ReadinessReport
from app.database.models.evaluation_history import EvaluationHistory
from app.database.models.prompts import PromptTemplate, PromptVersion
from app.database.models.job_match import JobMatch
from app.database.models.chat import ChatConversation, ChatMessage

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
    "SkillGraphNode",
    "SkillGraphEdge",
    "CapabilityScore",
    "Evidence",
    "SkillAlias",
    "TechnologyAlias",
    "ReadinessReport",
    "EvaluationHistory",
    "PromptTemplate",
    "PromptVersion",
    "JobMatch",
    "ChatConversation",
    "ChatMessage",


    "ProficiencyLevel",
    "GraphNodeType",
    "GraphRelationshipType",
    "EvidenceSource",
]


