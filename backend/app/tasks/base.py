"""Base Celery task classes.

Provides abstract tasks for tracking progress, supporting idempotency,
and enabling retries and cancellation.
"""

import logging
from typing import Any

from celery import Task
from celery.exceptions import Ignore

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


class BaseTask(Task):
    """Abstract base task providing progress tracking and structured logging."""

    abstract = True
    track_started = True

    def log_progress(self, percentage: int, message: str) -> None:
        """Log progress and update task state."""
        logger.info(f"Task {self.name} [{self.request.id}]: {percentage}% - {message}")
        self.update_state(
            state="PROGRESS",
            meta={"percentage": percentage, "message": message},
        )

    def check_cancellation(self) -> None:
        """Check if task was marked for cancellation and abort if so.
        
        This can be implemented by checking a Redis key or database flag.
        For now, it acts as a hook.
        """
        # In a real implementation, you'd check redis for f"cancel:{self.request.id}"
        pass

    def on_failure(self, exc: Exception, task_id: str, args: Any, kwargs: Any, einfo: Any) -> None:
        """Handle task failure."""
        logger.error(f"Task {self.name} [{task_id}] failed: {exc}", exc_info=einfo)
        super().on_failure(exc, task_id, args, kwargs, einfo)


class RetryableTask(BaseTask):
    """Abstract task that supports automatic retries."""

    abstract = True
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": 3, "countdown": 5}
    retry_backoff = True
    retry_backoff_max = 600
    retry_jitter = True


class CollectorTask(RetryableTask):
    """Base class for data collection tasks (e.g., GitHub, LeetCode)."""

    abstract = True
    
    def run(self, *args: Any, **kwargs: Any) -> Any:
        self.log_progress(0, "Starting collector task...")
        # Idempotency check hook could be here
        return super().run(*args, **kwargs)


class AIAnalysisTask(RetryableTask):
    """Base class for AI capability analysis tasks."""

    abstract = True
    retry_kwargs = {"max_retries": 2, "countdown": 10} # Heavier tasks, fewer retries

    def run(self, *args: Any, **kwargs: Any) -> Any:
        self.log_progress(0, "Starting AI analysis task...")
        return super().run(*args, **kwargs)


class ReportTask(BaseTask):
    """Base class for report generation tasks."""

    abstract = True

    def run(self, *args: Any, **kwargs: Any) -> Any:
        self.log_progress(0, "Starting report generation task...")
        return super().run(*args, **kwargs)
