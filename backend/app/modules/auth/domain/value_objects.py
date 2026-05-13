from __future__ import annotations

from dataclasses import dataclass

from app.modules.auth.domain.errors import WeakPasswordError

_MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True, slots=True)
class RawPassword:
    """Value object representing a validated (but not yet hashed) password."""

    value: str

    @classmethod
    def parse(cls, raw: str) -> RawPassword:
        if len(raw) < _MIN_PASSWORD_LENGTH:
            raise WeakPasswordError(
                f"Password must be at least {_MIN_PASSWORD_LENGTH} characters long"
            )
        return cls(value=raw)
