"""Alembic migration environment for {{ cookiecutter.project_name }}.

Runs migrations against the async engine defined in
``{{ cookiecutter.project_slug }}.core.database`` and reads the connection URL
from application settings rather than from ``alembic.ini``.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection

from {{ cookiecutter.project_slug }}.core.config import settings
from {{ cookiecutter.project_slug }}.core.database import Base, get_engine

# Alembic Config object, providing access to values within alembic.ini.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Inject the application's database URL and model metadata.
config.set_main_option("sqlalchemy.url", settings.database_url)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode, emitting SQL without a DB connection."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Configure the Alembic context for a live connection and run migrations.

    Args:
        connection (Connection): An active Alembic-managed database connection.
    """
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using the application's async engine."""
    connectable = get_engine()
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
