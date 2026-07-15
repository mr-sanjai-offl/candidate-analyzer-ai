"""Evidence database model.

Stores verification records backing candidate skills with weights and confidence attributes.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Float, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models.enums import EvidenceSource

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile
    from app.database.models.skill import Skill


class Evidence(Base):
    """Detailed evidence backing candidate skills."""

    __tablename__ = "evidences"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this evidence belongs to.",
    )
    skill_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The skill backed by this evidence.",
    )
    source: Mapped[EvidenceSource] = mapped_column(
        Enum(EvidenceSource, name="evidence_source", native_enum=True),
        nullable=False,
        doc="The source of this evidence (RESUME, GITHUB, etc.).",
    )
    weight: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Relevance/importance weight (0.0 to 1.0).",
    )
    confidence: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Confidence level percentage (0 to 100).",
    )
    evidence_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="Descriptive verification details of the evidence.",
    )
    verification_state: Mapped[str] = mapped_column(
        default="CLAIMED",
        doc="State of verification (CLAIMED, VERIFIED).",
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Arbitrary key-value evidence characteristics.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        backref="evidences",
    )
    skill: Mapped["Skill"] = relationship(
        "Skill",
        backref="evidences",
    )
