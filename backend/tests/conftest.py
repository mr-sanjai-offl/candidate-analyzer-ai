"""Pytest configuration and shared fixtures.

Provides async test client and application fixtures for testing
the FastAPI application without requiring a live database.

Architecture Bible Section 11: Testing Standards.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.main import create_app


def get_test_settings() -> Settings:
    """Override application settings for the test environment.

    Returns:
        Settings configured for testing (debug enabled, test database).
    """
    return Settings(
        ENVIRONMENT="development",
        DEBUG=True,
        DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/apexguidance_test",
        LOG_LEVEL="DEBUG",
    )


@pytest.fixture
def app():
    """Create a FastAPI application instance configured for testing.

    Overrides the settings dependency to use test-specific
    configuration (test database, debug mode, etc.).

    Yields:
        A configured FastAPI application.
    """
    test_app = create_app()
    test_app.dependency_overrides[get_settings] = get_test_settings
    yield test_app
    test_app.dependency_overrides.clear()


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client.

    Uses ``httpx.AsyncClient`` with ``ASGITransport`` to send
    requests directly to the FastAPI application without starting
    a live server or triggering lifespan events.

    Args:
        app: The test FastAPI application fixture.

    Yields:
        An async HTTP client bound to the test application.
    """
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
