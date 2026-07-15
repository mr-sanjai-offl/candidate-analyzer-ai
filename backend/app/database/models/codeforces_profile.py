"""Codeforces profile database model.

Stores aggregated metrics for a candidate's Codeforces profile.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class CodeforcesProfile(Base):
    """Codeforces profile and metrics for a candidate."""

    __tablename__ = "codeforces_profiles"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this Codeforces profile belongs to.",
    )
    username: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="Codeforces username (handle).",
    )
    rating: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Current Codeforces rating.",
    )
    max_rating: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Maximum Codeforces rating achieved.",
    )
    rank: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        doc="Current Codeforces rank (e.g., Expert, Master).",
    )
    max_rank: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
        doc="Maximum Codeforces rank achieved.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        back_populates="codeforces_profiles",
    )
