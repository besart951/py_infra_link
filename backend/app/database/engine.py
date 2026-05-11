"""SQLAlchemy async engine — created once, shared across the process.

The engine is configured from ``Settings`` and is the single entry-point for
all database connectivity.  No module should create its own engine.

``get_engine()`` is idempotent — repeated calls return the same instance.
``dispose_engine()`` is provided for clean shutdown (e.g. in tests or CLI).
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config.settings import get_settings

_engine: AsyncEngine | None = None


def get_engine() -> AsyncEngine:
    """Return the shared async engine, creating it on first call."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_async_engine(
            str(settings.database_url),
            echo=settings.echo_sql,
            pool_pre_ping=True,
        )
    return _engine


async def dispose_engine() -> None:
    """Dispose the engine — intended for graceful shutdown or test teardown."""
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
