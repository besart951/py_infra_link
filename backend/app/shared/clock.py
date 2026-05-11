"""Clock abstraction — isolates ``datetime.now()`` calls for testability.

The ``Clock`` protocol expresses a real seam: production code uses
``SystemClock`` (which calls ``datetime.now(UTC)``), while tests can inject a
``FixedClock`` that returns a deterministic value.

This is a valid two-Adapter seam as defined in ADR-0002.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol


class Clock(Protocol):
    """Interface for retrieving the current UTC time."""

    def now(self) -> datetime:
        """Return the current UTC-aware datetime."""
        ...


class SystemClock:
    """Production implementation — delegates to ``datetime.now(UTC)``."""

    def now(self) -> datetime:
        return datetime.now(UTC)


class FixedClock:
    """Test implementation — always returns the value supplied at construction.

    Example::

        clock = FixedClock(datetime(2024, 1, 1, tzinfo=UTC))
        assert clock.now() == datetime(2024, 1, 1, tzinfo=UTC)
    """

    def __init__(self, fixed: datetime) -> None:
        self._fixed = fixed

    def now(self) -> datetime:
        return self._fixed
