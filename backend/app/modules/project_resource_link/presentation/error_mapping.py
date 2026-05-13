from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.project_resource_link.domain.errors import (
    BuildingDoesNotExistError,
    ProjectDoesNotExistError,
    ProjectResourceLinkNotFoundError,
    ResourceAlreadyLinkedError,
)
from app.shared.errors import DomainError


def map_link_error(error: DomainError) -> HTTPException:
    if isinstance(
        error,
        (ProjectDoesNotExistError, ProjectResourceLinkNotFoundError, BuildingDoesNotExistError),
    ):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, ResourceAlreadyLinkedError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the project resource link module",
    )
