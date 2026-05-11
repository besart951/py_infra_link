from __future__ import annotations

from typing import Protocol

from app.modules.user.domain.models import User
from app.modules.user.domain.value_objects import UserEmail
from app.shared.ids import UserId
from app.shared.pagination import PageParams


class UserRepository(Protocol):
    async def get_by_id(self, user_id: UserId) -> User | None: ...

    async def get_by_email(self, email: UserEmail) -> User | None: ...

    async def create(self, user: User) -> User: ...

    async def list_page(self, params: PageParams) -> tuple[list[User], int]: ...
