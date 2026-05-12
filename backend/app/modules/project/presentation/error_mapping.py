from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.project.domain.errors import (
    InvalidProjectNameError,
    ProjectNameConflictError,
    ProjectNotFoundError,
    UserDoesNotExistError,
)


def map_project_error(error: Exception) -> HTTPException:
    if isinstance(error, (ProjectNotFoundError, UserDoesNotExistError)):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(
        error,
        (
            ProjectNameConflictError,
            InvalidProjectNameError,
        ),
    ):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the project module",
    )
