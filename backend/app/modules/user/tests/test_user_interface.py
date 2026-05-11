from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.modules.user.application.commands import CreateUserCommand
from app.modules.user.application.queries import GetUserQuery, ListUsersQuery
from app.modules.user.application.use_cases import UserModule
from app.modules.user.domain.errors import (
    InvalidUserDisplayNameError,
    InvalidUserEmailError,
    UserEmailConflictError,
    UserNotFoundError,
)
from app.modules.user.infrastructure.in_memory_adapter import InMemoryUserAdapter
from app.shared.clock import FixedClock
from app.shared.ids import UserId
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok


@pytest.mark.asyncio
async def test_create_user_success() -> None:
    fixed = datetime(2026, 1, 1, tzinfo=UTC)
    module = UserModule(repository=InMemoryUserAdapter(), clock=FixedClock(fixed))

    result = await module.create_user(
        CreateUserCommand(email="Alice@example.com", display_name=" Alice ")
    )

    assert isinstance(result, Ok)
    user = result.unwrap()
    assert user.email == "alice@example.com"
    assert user.display_name == "Alice"
    assert user.created_at == fixed


@pytest.mark.asyncio
async def test_create_user_duplicate_email_conflict() -> None:
    module = UserModule(
        repository=InMemoryUserAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    first = await module.create_user(CreateUserCommand(email="a@b.com", display_name="A"))
    assert isinstance(first, Ok)

    second = await module.create_user(CreateUserCommand(email="A@B.com", display_name="Another"))
    assert isinstance(second, Err)
    assert isinstance(second.error, UserEmailConflictError)


@pytest.mark.asyncio
async def test_create_user_invalid_email() -> None:
    module = UserModule(
        repository=InMemoryUserAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    result = await module.create_user(CreateUserCommand(email="invalid", display_name="A"))
    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidUserEmailError)


@pytest.mark.asyncio
async def test_create_user_invalid_display_name() -> None:
    module = UserModule(
        repository=InMemoryUserAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    result = await module.create_user(CreateUserCommand(email="a@b.com", display_name="   "))
    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidUserDisplayNameError)


@pytest.mark.asyncio
async def test_get_user_missing() -> None:
    module = UserModule(
        repository=InMemoryUserAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    result = await module.get_user(GetUserQuery(user_id=UserId(uuid4())))
    assert isinstance(result, Err)
    assert isinstance(result.error, UserNotFoundError)


@pytest.mark.asyncio
async def test_list_users_pagination() -> None:
    module = UserModule(
        repository=InMemoryUserAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    for i in range(3):
        created = await module.create_user(
            CreateUserCommand(email=f"u{i}@example.com", display_name=f"User {i}")
        )
        assert isinstance(created, Ok)

    page1 = await module.list_users(ListUsersQuery(page=PageParams(page=1, size=2)))
    assert page1.total == 3
    assert page1.pages == 2
    assert page1.has_next
    assert not page1.has_prev
    assert len(page1.items) == 2

    page2 = await module.list_users(ListUsersQuery(page=PageParams(page=2, size=2)))
    assert page2.total == 3
    assert page2.pages == 2
    assert not page2.has_next
    assert page2.has_prev
    assert len(page2.items) == 1
