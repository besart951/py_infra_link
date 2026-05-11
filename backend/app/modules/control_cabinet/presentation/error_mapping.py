from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.control_cabinet.domain.errors import (
    BuildingDoesNotExistError,
    ControlCabinetNameConflictError,
    ControlCabinetNotFoundError,
    InvalidControlCabinetNameError,
)


def map_cabinet_error(error: Exception) -> HTTPException:
    if isinstance(error, (ControlCabinetNotFoundError, BuildingDoesNotExistError)):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, (ControlCabinetNameConflictError, InvalidControlCabinetNameError)):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the control cabinet module",
    )
