"""HTTP-level integration tests for auth and protected project routes."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from uuid import UUID

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.database.session import get_session
from app.main import app
from app.modules.auth.infrastructure.jwt_codec import jwt_decode
from app.modules.live_update.infrastructure.connection_manager import ConnectionManager

pytestmark = pytest.mark.integration


@pytest_asyncio.fixture()
async def client(session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def _get_test_session() -> AsyncGenerator[AsyncSession, None]:
        yield session

    app.state.connection_manager = ConnectionManager()
    app.dependency_overrides[get_session] = _get_test_session

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as test_client:
        yield test_client

    app.dependency_overrides.clear()


async def _register_user(
    client: AsyncClient,
    email: str,
    display_name: str,
    password: str = "top-secret",
) -> tuple[UUID, str]:
    response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
            "display_name": display_name,
        },
    )

    assert response.status_code == 201
    payload = response.json()
    token = payload["access_token"]

    settings = get_settings()
    claims = jwt_decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    return UUID(claims["sub"]), token


@pytest.mark.asyncio
async def test_register_returns_bearer_token_with_subject_claim(client: AsyncClient) -> None:
    user_id, token = await _register_user(
        client,
        email="route.register@example.com",
        display_name="Route Register",
    )

    assert isinstance(token, str)
    assert token
    assert isinstance(user_id, UUID)


@pytest.mark.asyncio
async def test_login_returns_new_token_for_existing_credentials(client: AsyncClient) -> None:
    user_id, _registration_token = await _register_user(
        client,
        email="route.login@example.com",
        display_name="Route Login",
        password="correct-horse",
    )

    login_response = await client.post(
        "/auth/login",
        json={
            "email": "route.login@example.com",
            "password": "correct-horse",
        },
    )

    assert login_response.status_code == 200
    login_payload = login_response.json()
    assert login_payload["token_type"] == "bearer"
    assert isinstance(login_payload["access_token"], str)
    assert login_payload["access_token"]
    settings = get_settings()
    claims = jwt_decode(
        login_payload["access_token"],
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
    )
    assert claims["sub"] == str(user_id)


@pytest.mark.asyncio
async def test_create_project_requires_bearer_token(client: AsyncClient) -> None:
    owner_id, _ = await _register_user(
        client,
        email="route.noauth@example.com",
        display_name="No Auth",
    )

    response = await client.post(
        f"/users/{owner_id}/projects",
        json={"name": "Missing Auth", "description": "Denied"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_project_routes_allow_owner_and_forbid_different_user(client: AsyncClient) -> None:
    owner_id, owner_token = await _register_user(
        client,
        email="route.owner@example.com",
        display_name="Owner",
    )
    other_id, other_token = await _register_user(
        client,
        email="route.other@example.com",
        display_name="Other",
    )

    create_response = await client.post(
        f"/users/{owner_id}/projects",
        json={"name": "Owner Project", "description": "Created via route"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["owner_id"] == str(owner_id)
    assert created["name"] == "Owner Project"

    owner_list_response = await client.get(
        f"/users/{owner_id}/projects",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert owner_list_response.status_code == 200
    owner_page = owner_list_response.json()
    assert owner_page["total"] == 1
    assert owner_page["items"][0]["id"] == created["id"]

    forbidden_response = await client.get(
        f"/users/{owner_id}/projects",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert forbidden_response.status_code == 403

    other_list_response = await client.get(
        f"/users/{other_id}/projects",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert other_list_response.status_code == 200
    other_page = other_list_response.json()
    assert other_page["total"] == 0
