from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.project.domain.errors import (
    InvalidProjectNameError,
    ProjectNameConflictError,
    ProjectNotFoundError,
    UserDoesNotExistError,
)
from app.shared.errors import DomainError


def map_project_error(error: DomainError) -> HTTPException:
    if isinstance(error, (ProjectNotFoundError, UserDoesNotExistError)):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, ProjectNameConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    if isinstance(error, InvalidProjectNameError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the project module",
    )
