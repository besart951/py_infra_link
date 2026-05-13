from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.auth.domain.errors import InvalidCredentialsError, WeakPasswordError
from app.modules.user.domain.errors import (
    InvalidUserDisplayNameError,
    InvalidUserEmailError,
    UserEmailConflictError,
)
from app.shared.errors import DomainError


def map_auth_error(error: DomainError) -> HTTPException:
    if isinstance(error, InvalidCredentialsError):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
            headers={"WWW-Authenticate": "Bearer"},
        )
    if isinstance(error, UserEmailConflictError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error))
    if isinstance(
        error,
        (
            WeakPasswordError,
            InvalidUserEmailError,
            InvalidUserDisplayNameError,
        ),
    ):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(error)
        )
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
