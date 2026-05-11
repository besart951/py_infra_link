from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.user.domain.errors import (
    InvalidUserDisplayNameError,
    InvalidUserEmailError,
    UserEmailConflictError,
    UserNotFoundError,
)
from app.shared.errors import DomainError


def map_user_error(error: DomainError) -> HTTPException:
    if isinstance(error, UserNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    if isinstance(error, UserEmailConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=error.message)
    if isinstance(error, (InvalidUserEmailError, InvalidUserDisplayNameError)):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=error.message)
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.message)
