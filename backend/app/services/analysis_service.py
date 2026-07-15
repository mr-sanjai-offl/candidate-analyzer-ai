"""Analysis service.

Handles triggering and retrieving capability analysis reports.
"""

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.database.models.enums import AnalysisState
from app.database.repositories.analysis import AnalysisHistoryRepository, AnalysisRepository
from app.schemas.analysis import AnalysisCreate

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service layer for candidate analysis."""

    def __init__(
        self,
        analysis_repo: AnalysisRepository,
        history_repo: AnalysisHistoryRepository,
    ):
        self.analysis_repo = analysis_repo
        self.history_repo = history_repo

    async def start_analysis(
        self, db: AsyncSession, candidate_profile_id: uuid.UUID
    ) -> Any:
        """Initialize an analysis and start the pipeline."""
        # 1. Create Analysis record
        obj_in = AnalysisCreate(candidate_profile_id=candidate_profile_id)
        analysis = await self.analysis_repo.create(db=db, obj_in=obj_in)

        # 2. Add history entry
        await self.history_repo.create(
            db=db,
            obj_in={
                "analysis_id": analysis.id,
                "state": AnalysisState.PENDING,
                "message": "Analysis initiated.",
            },
        )
        logger.info(f"Started analysis {analysis.id} for candidate {candidate_profile_id}")
        return analysis

    async def get_analysis(self, db: AsyncSession, analysis_id: uuid.UUID) -> Any:
        """Get an analysis by ID."""
        analysis = await self.analysis_repo.get_by_id(db=db, id=analysis_id)
        if not analysis:
            raise NotFoundException("Analysis not found.")
        return analysis

    async def update_state(
        self, db: AsyncSession, analysis_id: uuid.UUID, state: AnalysisState, message: str = ""
    ) -> None:
        """Update the analysis state and add to history."""
        analysis = await self.get_analysis(db=db, analysis_id=analysis_id)
        await self.analysis_repo.update(db=db, db_obj=analysis, obj_in={"state": state})
        await self.history_repo.create(
            db=db,
            obj_in={"analysis_id": analysis.id, "state": state, "message": message},
        )
