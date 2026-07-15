"""Alembic async migration environment.

Configures Alembic to use an async SQLAlchemy engine for running
database migrations. The database URL is read from Pydantic Settings
(Architecture Bible Section 7) rather than being hard-coded in
``alembic.ini`` (Architecture Section 10: no secrets in code).
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.core.config import get_settings
from app.database.base import Base

# Alembic Config object — provides access to alembic.ini values.
config = context.config

# Set up Python logging from the config file.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the SQLAlchemy URL from Pydantic Settings.
# This ensures the connection string is never stored in alembic.ini.
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Target metadata for autogenerate support.
# Import all models here so that Base.metadata contains them.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Generates SQL scripts without connecting to the database.
    Useful for reviewing migration SQL before applying.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: object) -> None:
    """Execute migrations within a database connection context.

    Args:
        connection: A synchronous database connection provided
            by the async engine's ``run_sync`` method.
    """
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations using an async engine.

    Creates a temporary async engine with ``NullPool`` (no connection
    pooling) since migrations are a one-shot operation.
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async engine."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
