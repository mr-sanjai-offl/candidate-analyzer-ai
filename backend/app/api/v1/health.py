"""Health check endpoint.

Implements the health check as defined in Architecture Bible Section 12:

    ``GET /api/v1/health``
    Response: ``200 OK``
    ``{"status": "healthy", "version": "1.0.0"}``

This endpoint is required for every deployment and is used by Docker
health checks, load balancers, and orchestration tools.
"""

from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.core.logging import get_logger
from app.schemas.health import HealthResponse

logger = get_logger(__name__)

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check the health status of the API service.",
)
async def health_check(
    settings: Settings = Depends(get_settings),
) -> HealthResponse:
    """Check application health.

    Returns the current service status and version.
    Used by Docker ``HEALTHCHECK``, load balancers, and
    monitoring systems to verify the application is running.

    Args:
        settings: Injected application settings for version info.

    Returns:
        Health status and application version.
    """
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
    )
