"""Async SQLAlchemy session factory and FastAPI dependency.

``AsyncSessionFactory`` wraps ``async_sessionmaker`` and is bound to the
shared engine.  Use ``get_session()`` as a FastAPI dependency to obtain a
per-request ``AsyncSession``.

The session is yielded inside an ``async with`` block so it is always closed,
even if the route handler raises.  Transaction control is handled separately
by ``transaction.py`` — the session itself does not auto-commit.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.database.engine import get_engine

_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the shared session factory, creating it on first call."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields an ``AsyncSession`` for the request lifetime.

    Usage in a route::

        @router.get("/buildings/{id}")
        async def get_building(
            id: UUID,
            session: AsyncSession = Depends(get_session),
        ) -> BuildingResponse:
            ...
    """
    factory = get_session_factory()
    async with factory() as session:
        yield session
