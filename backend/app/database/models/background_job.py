"""Background job database model.

Tracks Celery tasks execution details in the database.
"""

from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.models.enums import JobStatus


class BackgroundJob(Base):
    """Execution record for an asynchronous background job."""

    __tablename__ = "background_jobs"

    task_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        doc="The fully qualified name of the Celery task.",
    )
    celery_task_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
        doc="The Celery-assigned task ID.",
    )
    status: Mapped[JobStatus] = mapped_column(
        Enum(JobStatus, name="job_status", native_enum=True),
        nullable=False,
        default=JobStatus.PENDING,
        index=True,
        doc="Current execution status.",
    )
    worker_id: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Identifier of the Celery worker processing this job.",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        doc="Number of times this job has been retried.",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Error message if the job failed.",
    )
    stack_trace: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="Stack trace if the job failed.",
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when the job started executing.",
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        doc="Timestamp when the job finished (success or fail).",
    )
    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Execution duration in milliseconds.",
    )
