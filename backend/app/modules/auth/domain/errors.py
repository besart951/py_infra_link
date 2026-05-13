from __future__ import annotations

from app.shared.errors import AuthorizationError, ValidationError


class InvalidCredentialsError(AuthorizationError):
    """Raised when email/password pair does not match any stored credential."""


class WeakPasswordError(ValidationError):
    """Raised when a supplied password does not meet strength requirements."""
