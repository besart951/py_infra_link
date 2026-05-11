"""Explicit transaction helpers.

``atomic`` is an async context manager that wraps a unit of work in a database
transaction.  Multi-step writes that must succeed or fail together should always
use ``atomic`` — never rely on implicit session behaviour.

Design principle (from INSTRUCTION.md):
- Multi-step writes must be atomic.
- Avoid compensating deletes when transactions solve the problem.
- ``atomic`` commits on success and rolls back on any exception, re-raising it.

Usage::

    async with atomic(session):
        await session.add(building)
        await session.flush()          # assigns PK without committing
        await session.add(cabinet)     # inside the same transaction

``atomic`` is intentionally not a decorator so that callers can choose exactly
which statements are included in the transaction boundary.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def atomic(session: AsyncSession) -> AsyncGenerator[AsyncSession, None]:
    """Yield ``session`` inside an explicit transaction.

    Commits if the body completes without exception.
    Rolls back and re-raises on any exception.
    """
    async with session.begin():
        yield session
