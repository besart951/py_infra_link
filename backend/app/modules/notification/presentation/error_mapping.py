from __future__ import annotations

from fastapi import HTTPException, status

from app.modules.notification.domain.errors import NotificationNotFoundError


def map_notification_error(error: Exception) -> HTTPException:
    if isinstance(error, NotificationNotFoundError):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="An unexpected error occurred in the notification module",
    )
