from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field

from app.modules.notification.domain.models import Notification
from app.shared.ids import NotificationId, UserId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class InMemoryNotificationAdapter:
    _notifications: dict[NotificationId, Notification] = field(
        default_factory=dict
    )

    async def create(self, notification: Notification) -> Notification:
        self._notifications[notification.id] = notification
        return notification

    async def get_by_id(
        self, notification_id: NotificationId
    ) -> Notification | None:
        return self._notifications.get(notification_id)

    async def mark_as_read(
        self, notification_id: NotificationId
    ) -> Notification | None:
        existing = self._notifications.get(notification_id)
        if existing is None:
            return None
        updated = dataclasses.replace(existing, is_read=True)
        self._notifications[notification_id] = updated
        return updated

    async def mark_all_as_read(self, user_id: UserId) -> int:
        count = 0
        for nid, n in list(self._notifications.items()):
            if n.user_id == user_id and not n.is_read:
                self._notifications[nid] = dataclasses.replace(n, is_read=True)
                count += 1
        return count

    async def list_page(
        self,
        user_id: UserId,
        params: PageParams,
        *,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]:
        all_items = sorted(
            [
                n
                for n in self._notifications.values()
                if n.user_id == user_id and (not unread_only or not n.is_read)
            ],
            key=lambda n: n.created_at,
            reverse=True,
        )
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total

    async def delete(self, notification_id: NotificationId) -> None:
        self._notifications.pop(notification_id, None)
