"""Search API Router.

Exposes REST endpoints for querying and ranking candidates based on technical profile criteria.
"""

import logging
from typing import Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.database.models.user import User, UserRole
from app.database.session import get_db_session
from app.services.search_engine import SearchEngineService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Candidate Search"])


@router.get(
    "/search",
    summary="Search and rank candidates profiles",
)
async def search_candidates(
    skills: List[str] = Query(None, description="Filter skills tags keywords."),
    min_readiness: float = Query(None, description="Minimum role readiness index threshold."),
    role: str = Query(None, description="Target role name (e.g. backend, frontend)."),
    min_capability_score: float = Query(None, description="Minimum average capabilities threshold."),
    db: AsyncSession = Depends(get_db_session),
    current_user: User = Depends(RoleChecker([UserRole.ADMIN, UserRole.RECRUITER])),
) -> Any:
    """Evaluate and rank candidates profiles matching the search filter criteria."""
    service = SearchEngineService()
    results = await service.search_candidates(
        db=db,
        skills=skills,
        min_readiness=min_readiness,
        role=role,
        min_capability_score=min_capability_score,
    )
    return {"results": results}
