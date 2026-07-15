"""Candidate skill association model.

Links a candidate profile to a specific skill, including proficiency scoring.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile
    from app.database.models.skill import Skill


class CandidateSkill(Base):
    """An association between a candidate profile and a skill with a proficiency score."""

    __tablename__ = "candidate_skills"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile.",
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The skill.",
    )
    proficiency_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Calculated proficiency score (0.0 to 100.0).",
    )

    __table_args__ = (
        UniqueConstraint("candidate_profile_id", "skill_id", name="uq_candidate_skill"),
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        back_populates="skills",
    )
    skill: Mapped["Skill"] = relationship(
        "Skill",
        back_populates="candidate_skills",
    )
