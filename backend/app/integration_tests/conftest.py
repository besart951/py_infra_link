"""Shared fixtures for PostgreSQL integration tests.

Each test file can import the fixtures below by name:

- ``session`` — an ``AsyncSession`` bound to a real PostgreSQL database
  connection.  Every test is wrapped in a transaction that is rolled back on
  teardown, so tests never leave data behind and can run in any order.

The session-scoped ``db_engine`` fixture starts a PostgreSQL container once for
the whole test session and applies all Alembic migrations, giving us confidence
that the migration chain is valid against a live database.
"""

from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from alembic import command as alembic_command
from alembic.config import Config as AlembicConfig
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import NullPool
from testcontainers.postgres import PostgresContainer

_INI = os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini")


# ── PostgreSQL container (one per test session) ───────────────────────────────


@pytest.fixture(scope="session")
def pg_container() -> Generator[PostgresContainer, None, None]:
    """Start a real PostgreSQL 16 container.  Stopped after all tests finish."""
    with PostgresContainer("postgres:16-alpine") as container:
        yield container


@pytest.fixture(scope="session")
def pg_asyncpg_url(pg_container: PostgresContainer) -> str:
    """Return an asyncpg-compatible URL for the test container."""
    return pg_container.get_connection_url().replace(
        "postgresql+psycopg2://", "postgresql+asyncpg://"
    )


# ── Engine + migrations (one per test session) ────────────────────────────────


@pytest.fixture(scope="session")
def db_engine(pg_asyncpg_url: str) -> Generator[AsyncEngine, None, None]:
    """Create the async engine and run Alembic migrations once.

    Alembic is run synchronously via its own ``asyncio.run`` call inside
    ``env.py``; this is safe from a session-scoped sync fixture.
    """
    alembic_cfg = AlembicConfig(_INI)
    # env.py uses async_engine_from_config, so it needs the asyncpg URL
    alembic_cfg.set_main_option("sqlalchemy.url", pg_asyncpg_url)
    alembic_command.upgrade(alembic_cfg, "head")

    eng = create_async_engine(pg_asyncpg_url, echo=False, poolclass=NullPool)
    yield eng
    asyncio.run(eng.dispose())


# ── Per-test transactional session ───────────────────────────────────────────


@pytest_asyncio.fixture()
async def session(db_engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:  # type: ignore[no-untyped-def]
    """Yield an ``AsyncSession`` inside a transaction that is always rolled back.

    This keeps every test fully isolated — no data leaks between tests.

    The session is bound to a single connection so that SAVEPOINTs created by
    ``session.begin_nested()`` (used inside ``SqlAlchemy*Adapter.create`` for
    IntegrityError handling) and plain ``session.flush()`` calls all operate
    within the same outer transaction that is ultimately rolled back.
    """
    async with db_engine.connect() as conn:
        await conn.begin()
        async_session = AsyncSession(bind=conn, expire_on_commit=False)
        try:
            yield async_session
        finally:
            await async_session.close()
            await conn.rollback()
