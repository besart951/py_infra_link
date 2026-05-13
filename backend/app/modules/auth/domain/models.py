from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import UserId


@dataclass(frozen=True, slots=True)
class UserCredential:
    """Stores the hashed password for a user.

    Deliberately kept separate from the ``User`` aggregate so that the user
    identity domain never handles raw passwords or hashing concerns.
    """

    user_id: UserId
    password_hash: str


@dataclass(frozen=True, slots=True)
class IssuedToken:
    """A successfully issued JWT access token together with the owner's id."""

    access_token: str
    user_id: UserId
    token_type: str = "bearer"
