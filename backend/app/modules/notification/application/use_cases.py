from __future__ import annotations

from dataclasses import dataclass

from app.modules.notification.application.commands import (
    DeleteNotificationCommand,
    MarkAllReadCommand,
    MarkAsReadCommand,
)
from app.modules.notification.application.queries import ListNotificationsQuery
from app.modules.notification.domain.errors import NotificationNotFoundError
from app.modules.notification.domain.interface import NotificationRepository
from app.modules.notification.domain.models import Notification
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class NotificationModule:
    notification_repository: NotificationRepository

    async def list_notifications(
        self, query: ListNotificationsQuery
    ) -> Page[Notification]:
        items, total = await self.notification_repository.list_page(
            query.user_id,
            query.page,
            unread_only=query.unread_only,
        )
        return Page[Notification](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def mark_as_read(
        self, command: MarkAsReadCommand
    ) -> Result[Notification, NotificationNotFoundError]:
        notification = await self.notification_repository.get_by_id(
            command.notification_id
        )
        if notification is None or notification.user_id != command.user_id:
            return Err(
                NotificationNotFoundError(
                    f"Notification '{command.notification_id}' was not found"
                )
            )
        updated = await self.notification_repository.mark_as_read(
            command.notification_id
        )
        if updated is None:
            return Err(
                NotificationNotFoundError(
                    f"Notification '{command.notification_id}' was not found"
                )
            )
        return Ok(updated)

    async def mark_all_as_read(self, command: MarkAllReadCommand) -> int:
        return await self.notification_repository.mark_all_as_read(command.user_id)

    async def delete_notification(
        self, command: DeleteNotificationCommand
    ) -> Result[None, NotificationNotFoundError]:
        notification = await self.notification_repository.get_by_id(
            command.notification_id
        )
        if notification is None or notification.user_id != command.user_id:
            return Err(
                NotificationNotFoundError(
                    f"Notification '{command.notification_id}' was not found"
                )
            )
        await self.notification_repository.delete(command.notification_id)
        return Ok(None)
