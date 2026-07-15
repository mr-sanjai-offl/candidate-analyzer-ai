"""Pydantic schemas for resume file upload and extraction."""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict

from app.database.models.resume import ParsingState


# ── Resume response schemas ──────────────────────────────────────────────────

class ResumeResponse(BaseModel):
    """Response schema for an uploaded resume record."""

    id: uuid.UUID
    owner_id: uuid.UUID
    original_filename: str
    file_size: int
    mime_type: str
    parsing_status: ParsingState
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetailResponse(ResumeResponse):
    """Detailed response including extraction data if available."""

    extraction: Optional["ResumeExtractionResponse"] = None


class ResumeExtractionResponse(BaseModel):
    """Schema for structured resume extraction data."""

    id: uuid.UUID
    resume_id: uuid.UUID
    structured_data: dict[str, Any]
    raw_text: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


ResumeDetailResponse.model_rebuild()


# ── Upload response schemas ───────────────────────────────────────────────────

class ResumeUploadResponse(BaseModel):
    """Returned immediately on upload — before parsing completes."""

    resume_id: uuid.UUID
    original_filename: str
    parsing_status: ParsingState
    message: str = "Resume uploaded. Background processing has started."
