"""Job Match database model.

Stores evaluations comparing candidate capability profiles against uploaded Job Descriptions.
"""

import uuid
from sqlalchemy import ForeignKey, String, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class JobMatch(Base):
    """Evaluation result of matching a candidate profile to a specific Job Description."""

    __tablename__ = "job_matches"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile matched.",
    )
    job_title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Title of the job description evaluated.",
    )
    match_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
        doc="Calculated match index percentage (0.0 to 100.0).",
    )
    match_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        doc="Structured match details (missing/transferable skills, roadmap).",
    )
