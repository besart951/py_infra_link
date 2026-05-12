from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import NotificationId, UserId


@dataclass(frozen=True, slots=True)
class MarkAsReadCommand:
    user_id: UserId
    notification_id: NotificationId


@dataclass(frozen=True, slots=True)
class MarkAllReadCommand:
    user_id: UserId


@dataclass(frozen=True, slots=True)
class DeleteNotificationCommand:
    user_id: UserId
    notification_id: NotificationId
