"""Analysis schemas.

Defines Pydantic models for Candidate Analysis reports.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.database.models.enums import AnalysisState


class AnalysisHistorySchema(BaseModel):
    id: uuid.UUID
    state: AnalysisState
    message: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalysisCreate(BaseModel):
    candidate_profile_id: uuid.UUID


class AnalysisResponse(BaseModel):
    id: uuid.UUID
    candidate_profile_id: uuid.UUID
    state: AnalysisState
    overall_score: Optional[float] = None
    report_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    history: List[AnalysisHistorySchema] = []

    model_config = ConfigDict(from_attributes=True)
