"""LeetCode profile database model.

Stores aggregated metrics for a candidate's LeetCode profile.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class LeetCodeProfile(Base):
    """LeetCode profile and metrics for a candidate."""

    __tablename__ = "leetcode_profiles"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this LeetCode profile belongs to.",
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="LeetCode username.",
    )
    problems_solved: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Total number of problems solved.",
    )
    easy_solved: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Easy problems solved.",
    )
    medium_solved: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Medium problems solved.",
    )
    hard_solved: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Hard problems solved.",
    )
    ranking: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Global LeetCode ranking.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        back_populates="leetcode_profiles",
    )
