"""Candidate profile database model.

Represents a candidate's overall profile, linking to a user and all
third-party profiles, projects, skills, and analyses.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import User
    from app.database.models.github_profile import GithubProfile
    from app.database.models.leetcode_profile import LeetCodeProfile
    from app.database.models.codeforces_profile import CodeforcesProfile
    from app.database.models.project import Project
    from app.database.models.candidate_skill import CandidateSkill
    from app.database.models.analysis import Analysis
    from app.database.models.uploaded_file import UploadedFile


class CandidateProfile(Base):
    """Candidate profile linking a user to all their evaluation data."""

    __tablename__ = "candidate_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
        doc="The system user this profile belongs to.",
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        default=None,
        doc="Short biography or summary.",
    )
    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        doc="Candidate's self-reported location.",
    )
    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        default=None,
        doc="Personal website URL.",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        backref="candidate_profile",
        single_parent=True,
    )
    github_profiles: Mapped[list["GithubProfile"]] = relationship(
        "GithubProfile",
        back_populates="candidate_profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    leetcode_profiles: Mapped[list["LeetCodeProfile"]] = relationship(
        "LeetCodeProfile",
        back_populates="candidate_profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    codeforces_profiles: Mapped[list["CodeforcesProfile"]] = relationship(
        "CodeforcesProfile",
        back_populates="candidate_profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="candidate_profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    skills: Mapped[list["CandidateSkill"]] = relationship(
        "CandidateSkill",
        back_populates="candidate_profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    analyses: Mapped[list["Analysis"]] = relationship(
        "Analysis",
        back_populates="candidate_profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    uploaded_files: Mapped[list["UploadedFile"]] = relationship(
        "UploadedFile",
        back_populates="candidate_profile",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
