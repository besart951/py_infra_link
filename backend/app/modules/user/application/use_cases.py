from __future__ import annotations

from app.modules.user.application.commands import CreateUserCommand
from app.modules.user.application.queries import GetUserQuery, ListUsersQuery
from app.modules.user.domain.errors import (
    InvalidUserDisplayNameError,
    InvalidUserEmailError,
    UserEmailConflictError,
    UserNotFoundError,
)
from app.modules.user.domain.interface import UserRepository
from app.modules.user.domain.models import User
from app.modules.user.domain.value_objects import UserDisplayName, UserEmail
from app.shared.clock import Clock
from app.shared.ids import UserId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


class UserModule:
    def __init__(self, repository: UserRepository, clock: Clock) -> None:
        self._repository = repository
        self._clock = clock

    async def create_user(
        self, command: CreateUserCommand
    ) -> Result[User, UserEmailConflictError | InvalidUserEmailError | InvalidUserDisplayNameError]:
        try:
            email = UserEmail.parse(command.email)
            display_name = UserDisplayName.parse(command.display_name)
        except (InvalidUserEmailError, InvalidUserDisplayNameError) as exc:
            return Err(exc)

        existing = await self._repository.get_by_email(email)
        if existing is not None:
            return Err(UserEmailConflictError(f"User with email '{email.value}' already exists"))

        user = User(
            id=new_id(UserId),
            email=email.value,
            display_name=display_name.value,
            created_at=self._clock.now(),
        )
        try:
            created = await self._repository.create(user)
        except UserEmailConflictError as exc:
            return Err(exc)
        return Ok(created)

    async def get_user(self, query: GetUserQuery) -> Result[User, UserNotFoundError]:
        user = await self._repository.get_by_id(query.user_id)
        if user is None:
            return Err(UserNotFoundError(f"User '{query.user_id}' was not found"))
        return Ok(user)

    async def list_users(self, query: ListUsersQuery) -> Page[User]:
        items, total = await self._repository.list_page(query.page)
        return Page[User](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )
