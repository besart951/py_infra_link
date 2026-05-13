from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.modules.auth.application.commands import LoginCommand, RegisterCommand
from app.modules.auth.application.use_cases import AuthModule, JwtSettings
from app.modules.auth.domain.errors import InvalidCredentialsError, WeakPasswordError
from app.modules.auth.infrastructure.in_memory_adapter import InMemoryCredentialAdapter
from app.modules.auth.infrastructure.jwt_codec import jwt_decode
from app.modules.auth.infrastructure.password_hasher import PlainPasswordHasher
from app.modules.user.application.use_cases import UserModule
from app.modules.user.domain.errors import UserEmailConflictError
from app.modules.user.infrastructure.in_memory_adapter import InMemoryUserAdapter
from app.shared.clock import FixedClock
from app.shared.result import Err, Ok

_FIXED = datetime(2099, 1, 1, tzinfo=UTC)
_JWT_SETTINGS = JwtSettings(
    secret_key="test-secret-key-that-is-long-enough-for-hs256",
    algorithm="HS256",
    expire_minutes=60,
)


def _make_module() -> tuple[AuthModule, InMemoryUserAdapter]:
    user_adapter = InMemoryUserAdapter()
    clock = FixedClock(_FIXED)
    module = AuthModule(
        user_module=UserModule(repository=user_adapter, clock=clock),
        user_repository=user_adapter,
        credential_repository=InMemoryCredentialAdapter(),
        hasher=PlainPasswordHasher(),
        jwt_settings=_JWT_SETTINGS,
        clock=clock,
    )
    return module, user_adapter


@pytest.mark.asyncio
async def test_register_success() -> None:
    module, _ = _make_module()
    result = await module.register(
        RegisterCommand(email="Alice@example.com", password="securepass", display_name=" Alice ")
    )

    assert isinstance(result, Ok)
    token_obj = result.value
    assert token_obj.token_type == "bearer"
    assert token_obj.access_token

    payload = jwt_decode(
        token_obj.access_token,
        _JWT_SETTINGS.secret_key,
        algorithms=[_JWT_SETTINGS.algorithm],
    )
    assert payload["sub"] == str(token_obj.user_id)


@pytest.mark.asyncio
async def test_register_normalises_email() -> None:
    module, user_adapter = _make_module()
    result = await module.register(
        RegisterCommand(email="UPPER@Example.com", password="securepass", display_name="Upper")
    )
    assert isinstance(result, Ok)
    user = await user_adapter.get_by_id(result.value.user_id)
    assert user is not None
    assert user.email == "upper@example.com"


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_conflict() -> None:
    module, _ = _make_module()
    await module.register(
        RegisterCommand(email="a@b.com", password="securepass", display_name="A")
    )
    result = await module.register(
        RegisterCommand(email="A@B.com", password="securepass", display_name="A2")
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, UserEmailConflictError)


@pytest.mark.asyncio
async def test_register_weak_password_returns_error() -> None:
    module, _ = _make_module()
    result = await module.register(
        RegisterCommand(email="a@b.com", password="short", display_name="A")
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, WeakPasswordError)


@pytest.mark.asyncio
async def test_login_success() -> None:
    module, _ = _make_module()
    await module.register(
        RegisterCommand(email="user@example.com", password="mypassword", display_name="User")
    )

    result = await module.login(LoginCommand(email="user@example.com", password="mypassword"))

    assert isinstance(result, Ok)
    assert result.value.access_token


@pytest.mark.asyncio
async def test_login_wrong_password_returns_invalid_credentials() -> None:
    module, _ = _make_module()
    await module.register(
        RegisterCommand(email="user@example.com", password="correct_pass", display_name="User")
    )

    result = await module.login(
        LoginCommand(email="user@example.com", password="wrong_pass")
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidCredentialsError)


@pytest.mark.asyncio
async def test_login_unknown_email_returns_invalid_credentials() -> None:
    module, _ = _make_module()
    result = await module.login(
        LoginCommand(email="nobody@example.com", password="anything")
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidCredentialsError)


@pytest.mark.asyncio
async def test_login_token_sub_matches_user_id() -> None:
    module, _ = _make_module()
    reg = await module.register(
        RegisterCommand(email="user@example.com", password="mypassword", display_name="User")
    )
    assert isinstance(reg, Ok)

    login_result = await module.login(
        LoginCommand(email="user@example.com", password="mypassword")
    )
    assert isinstance(login_result, Ok)

    payload = jwt_decode(
        login_result.value.access_token,
        _JWT_SETTINGS.secret_key,
        algorithms=[_JWT_SETTINGS.algorithm],
    )
    assert UUID(payload["sub"]) == reg.value.user_id


@pytest.mark.asyncio
async def test_login_email_case_insensitive() -> None:
    module, _ = _make_module()
    await module.register(
        RegisterCommand(email="user@example.com", password="mypassword", display_name="User")
    )
    result = await module.login(
        LoginCommand(email="USER@EXAMPLE.COM", password="mypassword")
    )
    assert isinstance(result, Ok)
