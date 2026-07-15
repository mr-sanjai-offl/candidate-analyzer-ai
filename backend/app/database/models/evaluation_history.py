"""Evaluation History database model.

Tracks metadata, execution time, and counts for candidate evaluation pipeline phases.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class EvaluationHistory(Base):
    """Tracks historical evaluation events for a candidate."""

    __tablename__ = "evaluation_histories"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this history event belongs to.",
    )
    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Type of action performed (e.g. SKILL_EXTRACTION, SCORING).",
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Arbitrary metrics, timings, and results summary.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        backref="evaluation_histories",
    )
