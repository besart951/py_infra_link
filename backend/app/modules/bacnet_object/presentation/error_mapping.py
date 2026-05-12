from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.bacnet_object.domain.errors import (
    BacnetObjectInstanceConflictError,
    BacnetObjectNameConflictError,
    BacnetObjectNotFoundError,
    FieldDeviceDoesNotExistError,
    InvalidBacnetObjectInstanceError,
    InvalidBacnetObjectNameError,
)


def map_bacnet_object_error(error: Exception) -> HTTPException:
    if isinstance(error, (BacnetObjectNotFoundError, FieldDeviceDoesNotExistError)):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    if isinstance(
        error,
        (
            BacnetObjectInstanceConflictError,
            BacnetObjectNameConflictError,
            InvalidBacnetObjectNameError,
            InvalidBacnetObjectInstanceError,
        ),
    ):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the BACnet object module",
    )
