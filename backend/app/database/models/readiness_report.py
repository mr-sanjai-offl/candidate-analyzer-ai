"""Readiness Report database model.

Stores evidence-backed role readiness scores (0-100) across frontend, backend, devops, etc.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class ReadinessReport(Base):
    """Calculated job readiness indicators for various software engineering profiles."""

    __tablename__ = "readiness_reports"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this readiness assessment belongs to.",
    )
    backend_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="Backend engineer readiness percentage."
    )
    frontend_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="Frontend engineer readiness percentage."
    )
    fullstack_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="Full Stack engineer readiness percentage."
    )
    ai_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="AI / ML engineer readiness percentage."
    )
    data_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="Data engineer readiness percentage."
    )
    devops_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="DevOps engineer readiness percentage."
    )
    cloud_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="Cloud architect readiness percentage."
    )
    cybersecurity_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="Cybersecurity engineer readiness percentage."
    )
    embedded_score: Mapped[float] = mapped_column(
        Float, default=0.0, nullable=False, doc="Embedded systems readiness percentage."
    )
    explanation: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Role-based gap analysis and reasoning metrics.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        backref="readiness_reports",
    )
