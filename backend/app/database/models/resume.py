"""Resume models for Phase 5 & 9.

Tracks uploaded resumes, parsing status, versions, metadata, and JSON extraction.
"""

import uuid
from typing import TYPE_CHECKING
from enum import StrEnum

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.database.models.user import User


class ParsingState(StrEnum):
    """Resume parsing states."""
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    STORING = "STORING"
    PARSING = "PARSING"
    EXTRACTING = "EXTRACTING"
    NORMALIZING = "NORMALIZING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class UploadedResume(Base):
    """An uploaded resume document."""

    __tablename__ = "uploaded_resumes"

    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
        doc="The user who uploaded this resume.",
    )
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        doc="Original filename uploaded by the user.",
    )
    storage_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
        unique=True,
        doc="Path in Supabase Storage.",
    )
    file_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="SHA-256 hash of the file to detect duplicates.",
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Size in bytes.",
    )
    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        doc="Detected MIME type.",
    )
    parsing_status: Mapped[ParsingState] = mapped_column(
        Enum(ParsingState, name="resume_parsing_state", native_enum=True),
        nullable=False,
        default=ParsingState.PENDING,
        doc="Current state of the parsing pipeline.",
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        backref="uploaded_resumes",
    )
    versions: Mapped[list["ResumeVersion"]] = relationship(
        "ResumeVersion",
        back_populates="resume",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    metadata_entries: Mapped[list["ResumeMetadata"]] = relationship(
        "ResumeMetadata",
        back_populates="resume",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    extraction: Mapped["ResumeExtraction"] = relationship(
        "ResumeExtraction",
        back_populates="resume",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ResumeVersion(Base):
    """Tracks versions of a replaced resume."""

    __tablename__ = "resume_versions"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("uploaded_resumes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        doc="Sequential version number.",
    )
    storage_path: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )
    file_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    resume: Mapped["UploadedResume"] = relationship(
        "UploadedResume",
        back_populates="versions",
    )


class ResumeMetadata(Base):
    """Key-value metadata for a resume."""

    __tablename__ = "resume_metadata"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("uploaded_resumes.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    key: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    value: Mapped[str] = mapped_column(
        String(1024),
        nullable=False,
    )

    resume: Mapped["UploadedResume"] = relationship(
        "UploadedResume",
        back_populates="metadata_entries",
    )


class ResumeExtraction(Base):
    """Structured JSON extraction from the parsed resume."""

    __tablename__ = "resume_extractions"

    resume_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("uploaded_resumes.id", ondelete="CASCADE"),
        index=True,
        unique=True,
        nullable=False,
    )
    structured_data: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        doc="The generated structured JSON representing the resume.",
    )
    raw_text: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
        doc="The raw parsed text (useful for debugging/search).",
    )

    resume: Mapped["UploadedResume"] = relationship(
        "UploadedResume",
        back_populates="extraction",
    )
