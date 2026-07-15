"""Background job repository layer.

Provides database access operations for background jobs.
"""

from typing import Type

from app.database.models.background_job import BackgroundJob
from app.database.repositories.base import BaseRepository


class BackgroundJobRepository(
    BaseRepository[BackgroundJob, Type[dict], Type[dict]]
):
    """Repository for BackgroundJob model."""

    def __init__(self) -> None:
        super().__init__(model=BackgroundJob)

