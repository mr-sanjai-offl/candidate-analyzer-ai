"""FastAPI application factory.

Creates and configures the FastAPI application instance following
Architecture Bible Section 7 (Dependency Injection, Pydantic Settings)
and Section 12 (Deployment Standards).

The application factory pattern (``create_app()``) enables:
- Testing with different configurations.
- Clean separation of application wiring from business logic.
- SOLID compliance (Single Responsibility, Dependency Inversion).
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import api_v1_router
from app.core.config import Environment, get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan context manager.

    Handles startup and shutdown events:

    **Startup:**
        - Configure structured logging.
        - Initialize async database engine.

    **Shutdown:**
        - Dispose database engine and release connections.
        - Log graceful shutdown completion.

    Args:
        app: The FastAPI application instance.

    Yields:
        Control to the application for the duration of its lifetime.
    """
    settings = get_settings()

    # --- Startup ---
    setup_logging(settings)
    logger.info(
        "Starting %s v%s in %s mode",
        settings.APP_NAME,
        settings.APP_VERSION,
        settings.ENVIRONMENT.value,
    )

    from app.database.session import dispose_engine, init_engine

    init_engine(settings)
    logger.info("Database engine initialized")

    yield

    # --- Shutdown ---
    await dispose_engine()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Assembles middleware, exception handlers, and routers.
    This is the single entry point for application construction.

    Returns:
        A fully configured :class:`FastAPI` application instance.
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=(
            "AI-powered platform for evaluating software engineer "
            "capabilities using public coding platforms and project repositories."
        ),
        docs_url="/docs" if settings.ENVIRONMENT != Environment.PRODUCTION else None,
        redoc_url="/redoc" if settings.ENVIRONMENT != Environment.PRODUCTION else None,
        lifespan=lifespan,
    )

    # CORS middleware — production-safe defaults (Architecture Section 10).
    # Explicit allowed origins; never uses '*' in production.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
    )

    # Register centralized exception handlers
    register_exception_handlers(app)

    # Mount API v1 router
    app.include_router(api_v1_router)

    return app


# Application instance used by uvicorn: `uvicorn app.main:app`
app = create_app()
