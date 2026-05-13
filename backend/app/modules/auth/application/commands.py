from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegisterCommand:
    email: str
    password: str
    display_name: str


@dataclass(frozen=True, slots=True)
class LoginCommand:
    email: str
    password: str
