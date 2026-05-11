from __future__ import annotations

from dataclasses import dataclass

from app.modules.user.domain.errors import InvalidUserDisplayNameError, InvalidUserEmailError


@dataclass(frozen=True, slots=True)
class UserEmail:
    value: str

    @classmethod
    def parse(cls, raw: str) -> UserEmail:
        normalized = raw.strip().lower()
        if not normalized:
            raise InvalidUserEmailError("Email must not be empty")
        if "@" not in normalized:
            raise InvalidUserEmailError("Email must contain '@'")
        local, _, domain = normalized.partition("@")
        if not local or not domain or "." not in domain:
            raise InvalidUserEmailError("Email format is invalid")
        return cls(value=normalized)


@dataclass(frozen=True, slots=True)
class UserDisplayName:
    value: str

    @classmethod
    def parse(cls, raw: str) -> UserDisplayName:
        normalized = raw.strip()
        if not normalized:
            raise InvalidUserDisplayNameError("Display name must not be empty")
        if len(normalized) > 120:
            raise InvalidUserDisplayNameError("Display name must be at most 120 characters")
        return cls(value=normalized)
