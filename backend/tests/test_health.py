"""Tests for the health check endpoint.

Verifies the health endpoint matches Architecture Bible Section 12:

    ``GET /api/v1/health`` → ``200 OK``
    ``{"status": "healthy", "version": "1.0.0"}``

Architecture Bible Section 11: Testing Standards.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check_returns_200(client: AsyncClient) -> None:
    """Health endpoint must return HTTP 200."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_check_response_has_required_fields(
    client: AsyncClient,
) -> None:
    """Health response must contain 'status' and 'version' fields."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert "status" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check_status_is_healthy(client: AsyncClient) -> None:
    """Health status must be 'healthy' when the service is running."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_version_is_semver(client: AsyncClient) -> None:
    """Version string must follow semantic versioning (X.Y.Z)."""
    response = await client.get("/api/v1/health")
    data = response.json()
    parts = data["version"].split(".")
    assert len(parts) == 3, "Version must have exactly 3 parts (major.minor.patch)"
    assert all(
        part.isdigit() for part in parts
    ), "All version parts must be numeric"
