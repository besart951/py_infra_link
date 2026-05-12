from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import UserId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class ListNotificationsQuery:
    user_id: UserId
    page: PageParams
    unread_only: bool = False
