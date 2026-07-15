"""API v1 router aggregation.

Collects all v1 sub-routers into a single router that is
mounted on the FastAPI application in ``main.py``.
New feature routers (auth, candidates, etc.) are added here
in their respective development phases.
"""

from fastapi import APIRouter

from app.api.v1.analysis import router as analysis_router
from app.api.v1.auth import router as auth_router
from app.api.v1.collect import router as collect_router
from app.api.v1.files import router as files_router
from app.api.v1.health import router as health_router
from app.api.v1.jobs import router as jobs_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(analysis_router, prefix="/analysis")
api_v1_router.include_router(jobs_router, prefix="/jobs")
api_v1_router.include_router(files_router, prefix="/files")
api_v1_router.include_router(collect_router)

