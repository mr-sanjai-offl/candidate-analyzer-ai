"""Uploaded file database model.

Tracks metadata for files (such as resumes) uploaded to the platform.
"""

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.candidate_profile import CandidateProfile


class UploadedFile(Base):
    """Metadata for a file uploaded by a candidate."""

    __tablename__ = "uploaded_files"

    candidate_profile_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("candidate_profiles.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The candidate profile this file belongs to.",
    )
    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Original filename.",
    )
    file_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="MIME type or extension (e.g., application/pdf).",
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Size of the file in bytes.",
    )
    storage_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        doc="Path or URL to the file in the storage system (e.g., Supabase Storage).",
    )

    # Relationships
    candidate_profile: Mapped["CandidateProfile"] = relationship(
        "CandidateProfile",
        back_populates="uploaded_files",
    )
