"""Application configuration management using Pydantic Settings.

All configuration is loaded from environment variables, following the
Architecture Bible Section 7 (Pydantic Settings only) and Section 10
(secrets via environment variables only).

No hard-coded secrets are permitted anywhere in the application.
"""

from enum import StrEnum
from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Application deployment environment.

    Controls behavior such as debug mode, documentation visibility,
    and logging verbosity.
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Application settings loaded exclusively from environment variables.

    Implements the single configuration source as mandated by
    Architecture Bible Section 7: 'Configuration — Pydantic Settings only'.
    All secrets are read from environment variables or a .env file;
    no hard-coded values are permitted (Section 10).

    Attributes:
        APP_NAME: Display name of the application.
        APP_VERSION: Semantic version string.
        ENVIRONMENT: Deployment environment (development/staging/production).
        DEBUG: Enable debug mode. Automatically disabled in production.
        HOST: Server bind address.
        PORT: Server bind port.
        DATABASE_URL: Async PostgreSQL connection string (asyncpg driver).
        DATABASE_ECHO: Enable SQLAlchemy query logging.
        DATABASE_POOL_SIZE: Connection pool size.
        DATABASE_MAX_OVERFLOW: Maximum overflow connections beyond pool size.
        REDIS_URL: Redis connection string for caching and job queue.
        CORS_ORIGINS: List of allowed CORS origins. Never use '*' in production.
        LOG_LEVEL: Python logging level.
        SENTRY_DSN: Sentry error tracking DSN. Empty string disables Sentry.
    """

    # Application
    APP_NAME: str = "ApexGuidance AI"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database — Supabase PostgreSQL (Architecture Section 4)
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/apexguidance"
    )
    DATABASE_ECHO: bool = False
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10

    # Redis (Architecture Section 4)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Supabase Storage (Architecture Section 4)
    SUPABASE_URL: str = "http://localhost:8000" # Local mock default
    SUPABASE_KEY: str = "dev_anon_key"

    # CORS — Production-safe defaults (Architecture Section 10)
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Sentry (Architecture Section 4)
    SENTRY_DSN: str = ""

    # Security / JWT (Architecture Section 10)
    JWT_SECRET_KEY: str = "dev_secret_key_change_me_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Platform Collector Settings (Phase 6/7/8)
    GITHUB_API_TOKEN: str = ""
    GITHUB_API_URL: str = "https://api.github.com"
    LEETCODE_API_URL: str = "https://leetcode.com"
    CODEFORCES_API_URL: str = "https://codeforces.com/api"
    COLLECTOR_TIMEOUT: int = 30
    COLLECTOR_MAX_RETRIES: int = 3
    COLLECTOR_CACHE_TTL: int = 3600

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    @field_validator("JWT_SECRET_KEY", mode="before")
    @classmethod
    def validate_jwt_secret(cls, value: str, info: object) -> str:
        """Validate that a secure JWT secret is set in staging/production."""
        data = getattr(info, "data", {})
        env = data.get("ENVIRONMENT")
        if env in (Environment.PRODUCTION, Environment.STAGING) and (
            not value or value == "dev_secret_key_change_me_in_production"
        ):
            raise ValueError(
                "JWT_SECRET_KEY must be set to a secure secret in "
                "production or staging environments"
            )
        return value

    @field_validator("DEBUG", mode="before")
    @classmethod
    def disable_debug_in_production(
        cls, value: bool, info: object  # noqa: ANN401
    ) -> bool:
        """Ensure debug mode is disabled in production.

        Architecture Bible Section 10: 'Debug mode enabled in production'
        is listed under security rules as a critical violation.

        Args:
            value: The provided debug flag.
            info: Pydantic validation info containing other field values.

        Returns:
            False if environment is production, otherwise the original value.
        """
        # Access already-validated data if available
        data = getattr(info, "data", {})
        env = data.get("ENVIRONMENT")
        if env == Environment.PRODUCTION and value:
            return False
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached application settings instance.

    Uses ``lru_cache`` to ensure settings are loaded only once,
    providing a singleton-like pattern suitable for FastAPI's
    dependency injection via ``Depends(get_settings)``.

    Returns:
        The application :class:`Settings` instance.
    """
    return Settings()
