"""HTTP-level integration tests for notification and project-resource-link routes."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from uuid import UUID, uuid4

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


async def _create_project(client: AsyncClient, owner_id: UUID, token: str, name: str) -> UUID:
    response = await client.post(
        f"/users/{owner_id}/projects",
        json={"name": name, "description": "HTTP route test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201
    return UUID(response.json()["id"])


async def _create_facility(client: AsyncClient, name: str) -> UUID:
    response = await client.post(
        "/facilities",
        json={"name": name, "description": "HTTP route test"},
    )
    assert response.status_code == 201
    return UUID(response.json()["id"])


@pytest.mark.asyncio
async def test_notification_routes_require_auth_and_enforce_owner(client: AsyncClient) -> None:
    owner_id, owner_token = await _register_user(
        client,
        email="route.notify.owner@example.com",
        display_name="Notify Owner",
    )
    other_id, other_token = await _register_user(
        client,
        email="route.notify.other@example.com",
        display_name="Notify Other",
    )

    await _create_project(client, owner_id, owner_token, "Notify Project")

    unauth = await client.get(f"/users/{owner_id}/notifications")
    assert unauth.status_code == 401

    owner_response = await client.get(
        f"/users/{owner_id}/notifications",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert owner_response.status_code == 200
    owner_page = owner_response.json()
    assert owner_page["total"] >= 1
    assert all(item["user_id"] == str(owner_id) for item in owner_page["items"])

    forbidden = await client.get(
        f"/users/{owner_id}/notifications",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert forbidden.status_code == 403

    other_response = await client.get(
        f"/users/{other_id}/notifications",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert other_response.status_code == 200


@pytest.mark.asyncio
async def test_notification_mark_as_read_and_not_found_error_mode(client: AsyncClient) -> None:
    owner_id, owner_token = await _register_user(
        client,
        email="route.notify.read@example.com",
        display_name="Notify Read",
    )

    await _create_project(client, owner_id, owner_token, "Read Notification Project")

    list_response = await client.get(
        f"/users/{owner_id}/notifications",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert list_response.status_code == 200
    notification_id = UUID(list_response.json()["items"][0]["id"])

    mark_response = await client.patch(
        f"/users/{owner_id}/notifications/{notification_id}/read",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert mark_response.status_code == 200
    marked = mark_response.json()
    assert marked["id"] == str(notification_id)
    assert marked["is_read"] is True

    not_found_response = await client.patch(
        f"/users/{owner_id}/notifications/{uuid4()}/read",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert not_found_response.status_code == 404


@pytest.mark.asyncio
async def test_project_resource_link_routes_require_auth_enforce_owner_and_not_found(
    client: AsyncClient,
) -> None:
    owner_id, owner_token = await _register_user(
        client,
        email="route.prl.owner@example.com",
        display_name="PRL Owner",
    )
    _other_id, other_token = await _register_user(
        client,
        email="route.prl.other@example.com",
        display_name="PRL Other",
    )

    project_id = await _create_project(client, owner_id, owner_token, "PRL Project")
    facility_id = await _create_facility(client, "PRL Facility")

    unauth_link = await client.post(
        f"/users/{owner_id}/projects/{project_id}/links",
        json={"resource_type": "facility", "resource_id": str(facility_id)},
    )
    assert unauth_link.status_code == 401

    owner_link = await client.post(
        f"/users/{owner_id}/projects/{project_id}/links",
        json={"resource_type": "facility", "resource_id": str(facility_id)},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert owner_link.status_code == 201
    link = owner_link.json()
    assert link["project_id"] == str(project_id)
    assert link["resource_type"] == "facility"

    forbidden_list = await client.get(
        f"/users/{owner_id}/projects/{project_id}/links",
        headers={"Authorization": f"Bearer {other_token}"},
    )
    assert forbidden_list.status_code == 403

    owner_list = await client.get(
        f"/users/{owner_id}/projects/{project_id}/links",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert owner_list.status_code == 200
    assert owner_list.json()["total"] == 1

    missing_link = await client.delete(
        f"/users/{owner_id}/projects/{project_id}/links/{uuid4()}",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert missing_link.status_code == 404
