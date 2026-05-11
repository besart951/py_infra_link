"""Result type — explicit success/failure without exceptions crossing module boundaries.

Usage::

    def find_building(id: BuildingId) -> Result[Building, NotFoundError]:
        ...

    result = find_building(id)
    match result:
        case Ok(value):
            return value
        case Err(error):
            raise error

The ``Result`` type is a discriminated union of ``Ok[T]`` and ``Err[E]``.
Callers must handle both branches — there is no implicit unwrap.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Never


@dataclass(frozen=True, slots=True)
class Ok[T]:
    """Represents a successful result containing a value of type ``T``."""

    value: T

    def unwrap(self) -> T:
        return self.value

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False


@dataclass(frozen=True, slots=True)
class Err[E: Exception]:
    """Represents a failed result containing an error of type ``E``."""

    error: E

    def unwrap(self) -> Never:
        raise self.error

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True


type Result[T, E: Exception] = Ok[T] | Err[E]
