from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.field_device.domain.errors import (
    FieldDeviceNameConflictError,
    FieldDeviceNotFoundError,
    InvalidFieldDeviceNameError,
    SpsControllerDoesNotExistError,
)
from app.shared.errors import DomainError


def map_field_device_error(error: DomainError) -> HTTPException:
    if isinstance(error, (FieldDeviceNotFoundError, SpsControllerDoesNotExistError)):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(error, FieldDeviceNameConflictError):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(error),
        )
    if isinstance(error, InvalidFieldDeviceNameError):
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the field device module",
    )
