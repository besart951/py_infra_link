from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.building.domain.errors import (
    BuildingNameConflictError,
    BuildingNotFoundError,
    FacilityDoesNotExistError,
    InvalidBuildingNameError,
)


def map_building_error(error: Exception) -> HTTPException:
    if isinstance(error, (BuildingNotFoundError, FacilityDoesNotExistError)):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, (BuildingNameConflictError, InvalidBuildingNameError)):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the building module",
    )
