from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.facility.domain.errors import (
    FacilityNameConflictError,
    FacilityNotFoundError,
    InvalidFacilityNameError,
)
from app.shared.errors import DomainError


def map_facility_error(error: DomainError) -> HTTPException:
    if isinstance(error, FacilityNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, FacilityNameConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    if isinstance(error, InvalidFacilityNameError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the facility module",
    )
