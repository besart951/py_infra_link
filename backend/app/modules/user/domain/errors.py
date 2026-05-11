from __future__ import annotations

from app.shared.errors import ConflictError, NotFoundError, ValidationError


class UserNotFoundError(NotFoundError):
    pass


class UserEmailConflictError(ConflictError):
    pass


class InvalidUserEmailError(ValidationError):
    pass


class InvalidUserDisplayNameError(ValidationError):
    pass
