from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.facility.domain.errors import (
    FacilityNameConflictError,
    FacilityNotFoundError,
    InvalidFacilityNameError,
)


def map_facility_error(error: Exception) -> HTTPException:
    if isinstance(error, FacilityNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, (FacilityNameConflictError, InvalidFacilityNameError)):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the facility module",
    )
