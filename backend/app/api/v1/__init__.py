"""API v1 router aggregation.

Collects all v1 sub-routers into a single router that is
mounted on the FastAPI application in ``main.py``.
New feature routers (auth, candidates, etc.) are added here
in their respective development phases.
"""

from fastapi import APIRouter

from app.api.v1.health import router as health_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(health_router)
