"""Analysis repository layer.

Provides database access operations for analysis and analysis history.
"""

from typing import Type

from app.database.models.analysis import Analysis, AnalysisHistory
from app.database.repositories.base import BaseRepository
from app.schemas.analysis import AnalysisCreate


class AnalysisRepository(
    BaseRepository[Analysis, AnalysisCreate, Type[dict]]
):
    """Repository for Analysis model."""
    pass


class AnalysisHistoryRepository(
    BaseRepository[AnalysisHistory, Type[dict], Type[dict]]
):
    """Repository for AnalysisHistory model."""
    pass
