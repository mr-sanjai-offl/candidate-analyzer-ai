"""GitHub profile database model.

Stores aggregated metrics for a candidate's GitHub profile.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class GithubProfile(Base):
    """GitHub profile and metrics for a candidate."""

    __tablename__ = "github_profiles"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this GitHub profile belongs to.",
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="GitHub username.",
    )
    repositories_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of public repositories.",
    )
    stars_received: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total stars received across all repositories.",
    )
    followers: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of GitHub followers.",
    )
    total_commits: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total commits over the past year.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        back_populates="github_profiles",
    )
