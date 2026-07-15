"""Capability Score database model.

Stores deterministic scoring calculations, proficiency levels, and breakdown explanation.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models.enums import ProficiencyLevel

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class CapabilityScore(Base):
    """Calculated capability scores across various technical dimensions."""

    __tablename__ = "capability_scores"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this score belongs to.",
    )
    category: Mapped[str] = mapped_column(
        doc="The technical score category (e.g. Programming Languages, DevOps).",
    )
    confidence_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Reliability / trust score (0 to 100).",
    )
    experience_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Years/volume of experience metric (0 to 100).",
    )
    depth_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Quality/intensity/complexity metric (0 to 100).",
    )
    breadth_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Scope of technology breadth metric (0 to 100).",
    )
    proficiency: Mapped[ProficiencyLevel] = mapped_column(
        Enum(ProficiencyLevel, name="proficiency_level", native_enum=True),
        nullable=False,
        default=ProficiencyLevel.BEGINNER,
        doc="Inferred expertise level.",
    )
    explanation: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Explains why this score was assigned.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        backref="capability_scores",
    )
