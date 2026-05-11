from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import UserId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class GetUserQuery:
    user_id: UserId


@dataclass(frozen=True, slots=True)
class ListUsersQuery:
    page: PageParams
