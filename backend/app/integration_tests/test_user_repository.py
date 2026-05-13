"""Integration tests for SqlAlchemyUserAdapter against a real PostgreSQL database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.user.application.commands import CreateUserCommand, UpdateUserCommand
from app.modules.user.application.queries import GetUserQuery, ListUsersQuery
from app.modules.user.application.use_cases import UserModule
from app.modules.user.domain.errors import UserEmailConflictError, UserNotFoundError
from app.modules.user.domain.value_objects import UserEmail
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.shared.clock import FixedClock
from app.shared.ids import UserId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def _make_module(session: AsyncSession) -> UserModule:
    return UserModule(
        repository=SqlAlchemyUserAdapter(session),
        clock=FixedClock(_FIXED),
    )


@pytest.mark.asyncio
async def test_create_and_get_user(session: AsyncSession) -> None:
    module = _make_module(session)

    result = await module.create_user(
        CreateUserCommand(email="alice@example.com", display_name="Alice")
    )
    assert isinstance(result, Ok)
    user = result.value

    fetched = await module.get_user(GetUserQuery(user_id=user.id))
    assert isinstance(fetched, Ok)
    assert fetched.value.email == "alice@example.com"
    assert fetched.value.display_name == "Alice"
    assert fetched.value.created_at == _FIXED


@pytest.mark.asyncio
async def test_get_user_not_found(session: AsyncSession) -> None:
    module = _make_module(session)

    result = await module.get_user(GetUserQuery(user_id=new_id(UserId)))
    assert isinstance(result, Err)
    assert isinstance(result.error, UserNotFoundError)


@pytest.mark.asyncio
async def test_create_user_duplicate_email_raises_conflict(session: AsyncSession) -> None:
    module = _make_module(session)

    first = await module.create_user(
        CreateUserCommand(email="dup@example.com", display_name="First")
    )
    assert isinstance(first, Ok)

    second = await module.create_user(
        CreateUserCommand(email="DUP@EXAMPLE.COM", display_name="Second")
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, UserEmailConflictError)


@pytest.mark.asyncio
async def test_update_user_display_name(session: AsyncSession) -> None:
    module = _make_module(session)

    created = (
        await module.create_user(CreateUserCommand(email="bob@example.com", display_name="Bob"))
    ).unwrap()

    updated_result = await module.update_user(
        UpdateUserCommand(user_id=created.id, display_name="Robert")
    )
    assert isinstance(updated_result, Ok)
    assert updated_result.value.display_name == "Robert"
    assert updated_result.value.email == "bob@example.com"


@pytest.mark.asyncio
async def test_delete_user(session: AsyncSession) -> None:
    module = _make_module(session)

    created = (
        await module.create_user(CreateUserCommand(email="del@example.com", display_name="Del"))
    ).unwrap()

    delete_result = await module.delete_user(created.id)
    assert isinstance(delete_result, Ok)

    get_result = await module.get_user(GetUserQuery(user_id=created.id))
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, UserNotFoundError)


@pytest.mark.asyncio
async def test_get_by_email(session: AsyncSession) -> None:
    module = _make_module(session)
    adapter = SqlAlchemyUserAdapter(session)

    await module.create_user(
        CreateUserCommand(email="findme@example.com", display_name="FindMe")
    )

    user = await adapter.get_by_email(UserEmail.parse("findme@example.com"))
    assert user is not None
    assert user.email == "findme@example.com"


@pytest.mark.asyncio
async def test_list_users_pagination(session: AsyncSession) -> None:
    module = _make_module(session)

    for i in range(3):
        r = await module.create_user(
            CreateUserCommand(email=f"pg{i}@example.com", display_name=f"PgUser {i}")
        )
        assert isinstance(r, Ok)

    page1 = await module.list_users(ListUsersQuery(page=PageParams(page=1, size=2)))
    assert page1.total >= 3
    assert len(page1.items) == 2

    page2 = await module.list_users(ListUsersQuery(page=PageParams(page=2, size=2)))
    assert page2.total >= 3
