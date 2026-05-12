from __future__ import annotations

from typing import Protocol

from app.modules.notification.domain.models import Notification
from app.shared.ids import NotificationId, UserId
from app.shared.pagination import PageParams


class NotificationRepository(Protocol):
    async def create(self, notification: Notification) -> Notification: ...

    async def get_by_id(
        self, notification_id: NotificationId
    ) -> Notification | None: ...

    async def mark_as_read(
        self, notification_id: NotificationId
    ) -> Notification | None: ...

    async def mark_all_as_read(self, user_id: UserId) -> int: ...

    async def list_page(
        self,
        user_id: UserId,
        params: PageParams,
        *,
        unread_only: bool = False,
    ) -> tuple[list[Notification], int]: ...

    async def delete(self, notification_id: NotificationId) -> None: ...
