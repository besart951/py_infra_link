from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.sps_controller.domain.errors import (
    ControlCabinetDoesNotExistError,
    InvalidSpsControllerNameError,
    SpsControllerNameConflictError,
    SpsControllerNotFoundError,
    SpsControllerSystemTypeDoesNotExistError,
)
from app.shared.errors import DomainError


def map_controller_error(error: DomainError) -> HTTPException:
    if isinstance(
        error,
        (
            SpsControllerNotFoundError,
            ControlCabinetDoesNotExistError,
            SpsControllerSystemTypeDoesNotExistError,
        ),
    ):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, SpsControllerNameConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    if isinstance(error, InvalidSpsControllerNameError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the SPS controller module",
    )
