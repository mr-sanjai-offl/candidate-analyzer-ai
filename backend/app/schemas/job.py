"""Background job schemas.

Defines Pydantic models for BackgroundJobs.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.database.models.enums import JobStatus


class BackgroundJobResponse(BaseModel):
    id: uuid.UUID
    task_name: str
    celery_task_id: Optional[str] = None
    status: JobStatus
    worker_id: Optional[str] = None
    retry_count: int
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    duration_ms: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
