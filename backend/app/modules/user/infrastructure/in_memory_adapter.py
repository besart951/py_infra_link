from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.user.domain.models import User
from app.modules.user.domain.value_objects import UserEmail
from app.shared.ids import UserId
from app.shared.pagination import PageParams


def _user_store() -> dict[UserId, User]:
    return {}


@dataclass(frozen=True, slots=True)
class InMemoryUserAdapter:
    _users: dict[UserId, User] = field(default_factory=_user_store)

    async def get_by_id(self, user_id: UserId) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: UserEmail) -> User | None:
        for user in self._users.values():
            if user.email == email.value:
                return user
        return None

    async def create(self, user: User) -> User:
        self._users[user.id] = user
        return user

    async def update(self, user: User) -> User:
        self._users[user.id] = user
        return user

    async def delete(self, user_id: UserId) -> None:
        self._users.pop(user_id, None)

    async def list_page(self, params: PageParams) -> tuple[list[User], int]:
        users = sorted(self._users.values(), key=lambda item: (item.created_at, item.id))
        total = len(users)
        items = users[params.offset : params.offset + params.limit]
        return (items, total)
