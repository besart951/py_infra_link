"""Integration tests for SqlAlchemyCredentialAdapter against a real PostgreSQL database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.application.commands import LoginCommand, RegisterCommand
from app.modules.auth.application.use_cases import AuthModule, JwtSettings
from app.modules.auth.infrastructure.password_hasher import PlainPasswordHasher
from app.modules.auth.infrastructure.sqlalchemy_adapter import SqlAlchemyCredentialAdapter
from app.modules.user.application.use_cases import UserModule
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.shared.clock import FixedClock
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2099, 1, 1, 12, 0, tzinfo=UTC)
_JWT = JwtSettings(
    secret_key="integration-test-secret-key-long-enough-for-hs256",
    algorithm="HS256",
    expire_minutes=60,
)


def _make_module(session: AsyncSession) -> AuthModule:
    user_adapter = SqlAlchemyUserAdapter(session)
    return AuthModule(
        user_module=UserModule(repository=user_adapter, clock=FixedClock(_FIXED)),
        user_repository=user_adapter,
        credential_repository=SqlAlchemyCredentialAdapter(session),
        hasher=PlainPasswordHasher(),
        jwt_settings=_JWT,
        clock=FixedClock(_FIXED),
    )


@pytest.mark.asyncio
async def test_register_stores_credential(session: AsyncSession) -> None:
    module = _make_module(session)
    cred_adapter = SqlAlchemyCredentialAdapter(session)

    result = await module.register(
        RegisterCommand(email="cred@example.com", password="securepass", display_name="Cred")
    )
    assert isinstance(result, Ok)

    credential = await cred_adapter.get_by_user_id(result.value.user_id)
    assert credential is not None
    assert credential.user_id == result.value.user_id
    assert credential.password_hash == "plain:securepass"


@pytest.mark.asyncio
async def test_login_success_with_db_adapter(session: AsyncSession) -> None:
    module = _make_module(session)

    reg = await module.register(
        RegisterCommand(email="login@example.com", password="mypassword", display_name="Login")
    )
    assert isinstance(reg, Ok)

    result = await module.login(LoginCommand(email="login@example.com", password="mypassword"))
    assert isinstance(result, Ok)
    assert result.value.access_token


@pytest.mark.asyncio
async def test_login_wrong_password_fails(session: AsyncSession) -> None:
    module = _make_module(session)

    await module.register(
        RegisterCommand(email="wrong@example.com", password="correct", display_name="Wrong")
    )
    result = await module.login(LoginCommand(email="wrong@example.com", password="bad"))
    assert isinstance(result, Err)


@pytest.mark.asyncio
async def test_credential_not_found_for_unknown_user(session: AsyncSession) -> None:
    from app.shared.ids import UserId, new_id

    cred_adapter = SqlAlchemyCredentialAdapter(session)
    cred = await cred_adapter.get_by_user_id(new_id(UserId))
    assert cred is None
