from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.sps_controller_system_type.domain.errors import (
    InvalidSpsControllerSystemTypeNameError,
    SpsControllerSystemTypeNameConflictError,
    SpsControllerSystemTypeNotFoundError,
)
from app.shared.errors import DomainError


def map_system_type_error(error: DomainError) -> HTTPException:
    if isinstance(error, SpsControllerSystemTypeNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, SpsControllerSystemTypeNameConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    if isinstance(error, InvalidSpsControllerSystemTypeNameError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the SPS controller system type module",
    )
