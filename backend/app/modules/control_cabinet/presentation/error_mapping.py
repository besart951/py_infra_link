from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.control_cabinet.domain.errors import (
    BuildingDoesNotExistError,
    ControlCabinetNameConflictError,
    ControlCabinetNotFoundError,
    InvalidControlCabinetNameError,
)
from app.shared.errors import DomainError


def map_cabinet_error(error: DomainError) -> HTTPException:
    if isinstance(error, (ControlCabinetNotFoundError, BuildingDoesNotExistError)):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, ControlCabinetNameConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    if isinstance(error, InvalidControlCabinetNameError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the control cabinet module",
    )
