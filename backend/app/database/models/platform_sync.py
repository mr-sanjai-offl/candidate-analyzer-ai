"""Platform synchronization tracking database model.

Stores raw payloads, normalized payloads, sync metadata, API/platform versions,
error messages, and timestamps for candidate coding platforms.
"""

from datetime import datetime
import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.database.models.enums import JobStatus, PlatformType

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class PlatformSync(Base):
    """Tracks synchronization state and payloads for external candidate platforms."""

    __tablename__ = "platform_syncs"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this sync tracking record belongs to.",
    )
    platform: Mapped[PlatformType] = mapped_column(
        Enum(PlatformType, name="platform_type", inherit_schema=True),
        index=True,
        nullable=False,
        doc="The external platform (GitHub, LeetCode, Codeforces).",
    )
    username: Mapped[str] = mapped_column(
        String(255),
        index=True,
        nullable=False,
        doc="The external platform username.",
    )
    sync_status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", inherit_schema=True),
        index=True,
        nullable=False,
        default=JobStatus.PENDING,
        doc="State of the sync job.",
    )
    raw_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Unmodified response payloads collected from the external platform APIs.",
    )
    normalized_payload: Mapped[dict[str, Any] | None] = mapped_column(
        JSONB,
        nullable=True,
        doc="Extracted schema data normalized for downstream scoring engines.",
    )
    platform_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="External platform data format version.",
    )
    api_version: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="The API version used during collection.",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Detailed error details if execution failed.",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of execution retries.",
    )
    last_synced_at: Mapped[datetime | None] = mapped_column(
        doc="Date and time of the last successful synchronization.",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        backref="platform_syncs",
    )
