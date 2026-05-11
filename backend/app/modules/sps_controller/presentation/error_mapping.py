from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.sps_controller.domain.errors import (
    ControlCabinetDoesNotExistError,
    InvalidSpsControllerNameError,
    SpsControllerNameConflictError,
    SpsControllerNotFoundError,
    SpsControllerSystemTypeDoesNotExistError,
)


def map_controller_error(error: Exception) -> HTTPException:
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
    if isinstance(error, (SpsControllerNameConflictError, InvalidSpsControllerNameError)):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the SPS controller module",
    )
