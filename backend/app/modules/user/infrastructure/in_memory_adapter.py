from __future__ import annotations

from app.modules.user.domain.models import User
from app.modules.user.domain.value_objects import UserEmail
from app.shared.ids import UserId
from app.shared.pagination import PageParams


class InMemoryUserAdapter:
    def __init__(self) -> None:
        self._items_by_id: dict[UserId, User] = {}

    async def get_by_id(self, user_id: UserId) -> User | None:
        return self._items_by_id.get(user_id)

    async def get_by_email(self, email: UserEmail) -> User | None:
        for user in self._items_by_id.values():
            if user.email == email.value:
                return user
        return None

    async def create(self, user: User) -> User:
        self._items_by_id[user.id] = user
        return user

    async def list_page(self, params: PageParams) -> tuple[list[User], int]:
        users = sorted(self._items_by_id.values(), key=lambda item: (item.created_at, item.id))
        total = len(users)
        items = users[params.offset : params.offset + params.limit]
        return (items, total)
