"""Pytest configuration and shared fixtures.

Provides async test client, database session fixtures, and auto-schema
setup with wait/retry logic for postgres container readiness.
"""

import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings, get_settings
from app.database.base import Base
from app.database.session import get_db_session
from app.main import create_app


def get_test_settings() -> Settings:
    """Override application settings for the test environment.

    Returns:
        Settings configured for testing (debug enabled, test database).
    """
    return Settings(
        ENVIRONMENT="development",
        DEBUG=True,
        DATABASE_URL=(
            "postgresql+asyncpg://postgres:postgres@localhost:5432/apexguidance_test"
        ),
        LOG_LEVEL="DEBUG",
    )


async def create_test_db_if_not_exists(settings: Settings) -> None:
    """Connect to default postgres DB and create the test database if missing.

    Implements a retry loop to await PostgreSQL container startup.
    """
    default_url = "postgresql+asyncpg://postgres:postgres@localhost:5432/postgres"

    # Retry loop to allow Docker container setup
    for _i in range(15):
        try:
            engine = create_async_engine(default_url, isolation_level="AUTOCOMMIT")
            async with engine.connect() as conn:
                await conn.execute(
                    text(f"CREATE DATABASE {settings.DATABASE_URL.split('/')[-1]}"),
                )
            await engine.dispose()
            return
        except Exception as e:
            # Check if database already exists (SQLState 42P04)
            if "duplicate database" in str(e).lower() or "already exists" in str(e).lower():
                await engine.dispose()
                return
            await asyncio.sleep(1.0)

    raise RuntimeError("PostgreSQL database not available after 15 retries")


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database() -> AsyncGenerator[None, None]:
    """Initialize test database tables.

    Runs once for the entire test session. Auto-creates tables using Base.metadata.
    """
    test_settings = get_test_settings()

    # Wait for DB and create the test database if it does not exist
    await create_test_db_if_not_exists(test_settings)

    engine = create_async_engine(test_settings.DATABASE_URL)

    # Initialize tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Clean up schemas
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an isolated async database session for a test.

    Runs each test inside a rollback-isolated transaction.
    """
    test_settings = get_test_settings()
    engine = create_async_engine(test_settings.DATABASE_URL)
    async_session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_factory() as session:
        yield session
        # Transaction is rolled back to clean up changes
        await session.rollback()

    await engine.dispose()


@pytest.fixture
def app(db_session: AsyncSession):
    """Create a FastAPI application instance configured for testing.

    Overrides the settings and database session dependencies.
    """
    test_app = create_app()
    test_app.dependency_overrides[get_settings] = get_test_settings

    # Override get_db_session to yield the test transaction session
    async def _get_db_session_override() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    test_app.dependency_overrides[get_db_session] = _get_db_session_override

    yield test_app
    test_app.dependency_overrides.clear()


@pytest.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """Provide an async HTTP test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac
