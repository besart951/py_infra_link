from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.sps_controller_system_type.domain.errors import (
    InvalidSpsControllerSystemTypeNameError,
    SpsControllerSystemTypeNameConflictError,
    SpsControllerSystemTypeNotFoundError,
)


def map_system_type_error(error: Exception) -> HTTPException:
    if isinstance(error, SpsControllerSystemTypeNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(
        error,
        (
            SpsControllerSystemTypeNameConflictError,
            InvalidSpsControllerSystemTypeNameError,
        ),
    ):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the SPS controller system type module",
    )
