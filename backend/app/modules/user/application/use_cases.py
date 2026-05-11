from __future__ import annotations

from dataclasses import dataclass

from app.modules.user.application.commands import CreateUserCommand, UpdateUserCommand
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


@dataclass(frozen=True, slots=True)
class UserModule:
    repository: UserRepository
    clock: Clock

    async def create_user(
        self, command: CreateUserCommand
    ) -> Result[User, UserEmailConflictError | InvalidUserEmailError | InvalidUserDisplayNameError]:
        try:
            email = UserEmail.parse(command.email)
            display_name = UserDisplayName.parse(command.display_name)
        except (InvalidUserEmailError, InvalidUserDisplayNameError) as exc:
            return Err(exc)

        existing = await self.repository.get_by_email(email)
        if existing is not None:
            return Err(UserEmailConflictError(f"User with email '{email.value}' already exists"))

        user = User(
            id=new_id(UserId),
            email=email.value,
            display_name=display_name.value,
            created_at=self.clock.now(),
        )
        created = await self.repository.create(user)
        return Ok(created)

    async def get_user(self, query: GetUserQuery) -> Result[User, UserNotFoundError]:
        user = await self.repository.get_by_id(query.user_id)
        if user is None:
            return Err(UserNotFoundError(f"User '{query.user_id}' was not found"))
        return Ok(user)

    async def list_users(self, query: ListUsersQuery) -> Page[User]:
        items, total = await self.repository.list_page(query.page)
        return Page[User](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def update_user(
        self, command: UpdateUserCommand
    ) -> Result[User, UserNotFoundError | UserEmailConflictError | InvalidUserDisplayNameError]:
        user = await self.repository.get_by_id(command.user_id)
        if user is None:
            return Err(UserNotFoundError(f"User '{command.user_id}' was not found"))

        display_name_value = user.display_name
        if command.display_name is not None:
            try:
                display_name = UserDisplayName.parse(command.display_name)
                display_name_value = display_name.value
            except InvalidUserDisplayNameError as exc:
                return Err(exc)

        updated_user = User(
            id=user.id,
            email=user.email,
            display_name=display_name_value,
            created_at=user.created_at,
        )
        updated = await self.repository.update(updated_user)
        return Ok(updated)

    async def delete_user(self, user_id: UserId) -> Result[None, UserNotFoundError]:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            return Err(UserNotFoundError(f"User '{user_id}' was not found"))

        await self.repository.delete(user_id)
        return Ok(None)
