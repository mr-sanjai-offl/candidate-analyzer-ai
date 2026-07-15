"""Health check response schemas.

Pydantic models for the health endpoint as required by
Architecture Bible Section 7: 'Pydantic Models for all
request/response bodies'.

The response format matches Architecture Bible Section 12:
``{"status": "healthy", "version": "1.0.0"}``
"""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response model for the health check endpoint.

    Matches the exact response format defined in
    Architecture Bible Section 12.

    Attributes:
        status: Health status of the service (``"healthy"`` or ``"unhealthy"``).
        version: Application semantic version string.
    """

    status: str = Field(
        ...,
        description="Health status of the service.",
        examples=["healthy"],
    )
    version: str = Field(
        ...,
        description="Application semantic version.",
        examples=["1.0.0"],
    )
