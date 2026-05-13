from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.building.domain.errors import (
    BuildingNameConflictError,
    BuildingNotFoundError,
    FacilityDoesNotExistError,
    InvalidBuildingNameError,
)
from app.shared.errors import DomainError


def map_building_error(error: DomainError) -> HTTPException:
    if isinstance(error, (BuildingNotFoundError, FacilityDoesNotExistError)):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, BuildingNameConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    if isinstance(error, InvalidBuildingNameError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the building module",
    )
