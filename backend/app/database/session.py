"""Async database session management.

Provides async SQLAlchemy 2.0 engine and session factory using the
``asyncpg`` driver as specified in Architecture Bible Section 4.
Database access is always through the service layer via dependency
injection (Architecture Section 7).
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Module-level engine and session factory.
# Initialized during application lifespan startup.
_engine: AsyncEngine | None = None
_async_session_factory: async_sessionmaker[AsyncSession] | None = None


def init_engine(settings: Settings) -> None:
    """Initialize the async SQLAlchemy engine and session factory.

    Called once during application startup via the lifespan context
    manager. Configures connection pooling with ``pool_pre_ping``
    for reliability (Architecture Section 3: Reliability).

    Args:
        settings: Application settings containing database configuration.
    """
    global _engine, _async_session_factory  # noqa: PLW0603

    _engine = create_async_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_size=settings.DATABASE_POOL_SIZE,
        max_overflow=settings.DATABASE_MAX_OVERFLOW,
        pool_pre_ping=True,
    )

    _async_session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    logger.info(
        "Database engine created: pool_size=%d, max_overflow=%d",
        settings.DATABASE_POOL_SIZE,
        settings.DATABASE_MAX_OVERFLOW,
    )


async def dispose_engine() -> None:
    """Dispose of the async engine during application shutdown.

    Closes all pooled connections and releases resources.
    Called during the lifespan shutdown phase.
    """
    global _engine  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        logger.info("Database engine disposed")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session via dependency injection.

    Intended for use with FastAPI's ``Depends()`` mechanism.
    The session is automatically closed when the request completes.
    Rollback is triggered on unhandled exceptions to maintain
    data integrity.

    Yields:
        An async SQLAlchemy session for database operations.

    Raises:
        RuntimeError: If the session factory has not been initialized
            (i.e., ``init_engine()`` was not called during startup).
    """
    if _async_session_factory is None:
        raise RuntimeError(
            "Database session factory not initialized. "
            "Ensure init_engine() is called during application startup."
        )

    async with _async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


@asynccontextmanager
async def get_db_session_ctx() -> AsyncGenerator[AsyncSession, None]:
    """Provide an async database session context manager.

    Useful for background tasks (e.g., Celery) that run outside
    FastAPI dependency injection context.
    """
    global _async_session_factory
    if _async_session_factory is None:
        from app.core.config import get_settings
        init_engine(get_settings())

    async with _async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise

