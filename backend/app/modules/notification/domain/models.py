from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.ids import NotificationId, UserId


@dataclass(frozen=True, slots=True)
class Notification:
    id: NotificationId
    user_id: UserId
    title: str
    body: str
    is_read: bool
    created_at: datetime
