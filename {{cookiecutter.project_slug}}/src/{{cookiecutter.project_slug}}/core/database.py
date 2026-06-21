"""Async SQLAlchemy engine and session management for {{ cookiecutter.project_name }}.

Provides the database plumbing shared by all ORM models: a declarative ``Base``,
a lazily-connecting async engine built from ``settings.database_url``, and a
``get_session`` factory returning an
:class:`~sqlalchemy.ext.asyncio.AsyncSession`.

The engine is created at import time but does not open a connection until a
session is first used, so importing this module is side-effect free for tests
and tooling.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from {{ cookiecutter.project_slug }}.core.config import settings


class Base(DeclarativeBase):
    """Declarative base class for all ORM models."""


_engine: AsyncEngine = create_async_engine(
    settings.database_url,
    pool_pre_ping=True,
)
_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    _engine,
    expire_on_commit=False,
)


def get_engine() -> AsyncEngine:
    """Return the shared async engine.

    Returns:
        AsyncEngine: The process-wide async SQLAlchemy engine, useful for
            health checks and Alembic migrations.
    """
    return _engine


def get_session() -> AsyncSession:
    """Return a new async session for use as an async context manager.

    Returns:
        AsyncSession: A new session bound to the shared engine. Use it as
            ``async with get_session() as session: ...``.
    """
    return _session_factory()
