from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.auth.presentation.dependencies import get_current_user
from app.modules.notification.application.commands import (
    DeleteNotificationCommand,
    MarkAllReadCommand,
    MarkAsReadCommand,
)
from app.modules.notification.application.queries import ListNotificationsQuery
from app.modules.notification.application.use_cases import NotificationModule
from app.modules.notification.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyNotificationAdapter,
)
from app.modules.notification.presentation.error_mapping import map_notification_error
from app.modules.notification.presentation.schemas import (
    MarkAllReadResponse,
    NotificationRead,
)
from app.modules.user.domain.models import User
from app.shared.ids import NotificationId, UserId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(
    prefix="/users/{user_id}/notifications",
    tags=["notifications"],
)


def _make_module(session: AsyncSession) -> NotificationModule:
    return NotificationModule(
        notification_repository=SqlAlchemyNotificationAdapter(session),
    )


def _require_owner(current_user: User, user_id: UUID) -> None:
    """Raise 403 if the authenticated user is not the target user."""
    if current_user.id != UserId(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this resource",
        )


@router.get("", response_model=Page[NotificationRead])
async def list_notifications(
    user_id: UUID,
    page: int = 1,
    size: int = 20,
    unread_only: bool = False,
    session: AsyncSession = Depends(get_session),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> Page[NotificationRead]:
    _require_owner(current_user, user_id)
    module = _make_module(session)
    result = await module.list_notifications(
        ListNotificationsQuery(
            user_id=UserId(user_id),
            page=PageParams(page=page, size=size),
            unread_only=unread_only,
        )
    )
    return Page[NotificationRead](
        items=[NotificationRead.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.patch(
    "/{notification_id}/read",
    response_model=NotificationRead,
)
async def mark_as_read(
    user_id: UUID,
    notification_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> NotificationRead:
    _require_owner(current_user, user_id)
    module = _make_module(session)
    result = await module.mark_as_read(
        MarkAsReadCommand(
            user_id=UserId(user_id),
            notification_id=NotificationId(notification_id),
        )
    )
    if isinstance(result, Ok):
        return NotificationRead.model_validate(result.value)
    raise map_notification_error(result.error)


@router.post(
    "/read-all",
    response_model=MarkAllReadResponse,
)
async def mark_all_as_read(
    user_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> MarkAllReadResponse:
    _require_owner(current_user, user_id)
    module = _make_module(session)
    marked = await module.mark_all_as_read(MarkAllReadCommand(user_id=UserId(user_id)))
    return MarkAllReadResponse(marked=marked)


@router.delete(
    "/{notification_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_notification(
    user_id: UUID,
    notification_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
) -> Response:
    _require_owner(current_user, user_id)
    module = _make_module(session)
    result = await module.delete_notification(
        DeleteNotificationCommand(
            user_id=UserId(user_id),
            notification_id=NotificationId(notification_id),
        )
    )
    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise map_notification_error(result.error)
