from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import UserId


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    email: str
    display_name: str


@dataclass(frozen=True, slots=True)
class UpdateUserCommand:
    user_id: UserId
    display_name: str | None = None
