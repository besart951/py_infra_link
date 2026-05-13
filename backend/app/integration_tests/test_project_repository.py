"""Integration tests for SqlAlchemyProjectAdapter against a real PostgreSQL database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.live_update.infrastructure.null_publisher import NullEventPublisher
from app.modules.project.application.commands import CreateProjectCommand, UpdateProjectCommand
from app.modules.project.application.queries import GetProjectQuery, ListProjectsQuery
from app.modules.project.application.use_cases import ProjectModule
from app.modules.project.domain.errors import ProjectNameConflictError, ProjectNotFoundError
from app.modules.project.infrastructure.sqlalchemy_adapter import SqlAlchemyProjectAdapter
from app.modules.user.application.commands import CreateUserCommand
from app.modules.user.application.use_cases import UserModule
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.shared.clock import FixedClock
from app.shared.ids import ProjectId, UserId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


async def _create_user(session: AsyncSession, email: str, display_name: str = "User") -> UserId:
    user_module = UserModule(
        repository=SqlAlchemyUserAdapter(session), clock=FixedClock(_FIXED)
    )
    result = await user_module.create_user(
        CreateUserCommand(email=email, display_name=display_name)
    )
    assert isinstance(result, Ok)
    return result.value.id


def _make_module(session: AsyncSession) -> ProjectModule:
    return ProjectModule(
        project_repository=SqlAlchemyProjectAdapter(session),
        user_repository=SqlAlchemyUserAdapter(session),
        clock=FixedClock(_FIXED),
        event_publisher=NullEventPublisher(),
    )


@pytest.mark.asyncio
async def test_create_and_get_project(session: AsyncSession) -> None:
    owner_id = await _create_user(session, "owner_proj@example.com")
    module = _make_module(session)

    result = await module.create_project(
        CreateProjectCommand(owner_id=owner_id, name="Alpha", description="First project")
    )
    assert isinstance(result, Ok)
    project = result.value

    fetched = await module.get_project(
        GetProjectQuery(owner_id=owner_id, project_id=project.id)
    )
    assert isinstance(fetched, Ok)
    assert fetched.value.name == "Alpha"
    assert fetched.value.description == "First project"
    assert fetched.value.owner_id == owner_id


@pytest.mark.asyncio
async def test_get_project_not_found(session: AsyncSession) -> None:
    owner_id = await _create_user(session, "owner_notfound@example.com")
    module = _make_module(session)

    result = await module.get_project(
        GetProjectQuery(owner_id=owner_id, project_id=new_id(ProjectId))
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, ProjectNotFoundError)


@pytest.mark.asyncio
async def test_duplicate_project_name_per_owner_raises_conflict(session: AsyncSession) -> None:
    owner_id = await _create_user(session, "owner_dup@example.com")
    module = _make_module(session)

    first = await module.create_project(
        CreateProjectCommand(owner_id=owner_id, name="Dup Project")
    )
    assert isinstance(first, Ok)

    second = await module.create_project(
        CreateProjectCommand(owner_id=owner_id, name="Dup Project")
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, ProjectNameConflictError)


@pytest.mark.asyncio
async def test_same_project_name_allowed_for_different_owners(session: AsyncSession) -> None:
    owner1 = await _create_user(session, "owner1_proj@example.com")
    owner2 = await _create_user(session, "owner2_proj@example.com")
    module = _make_module(session)

    r1 = await module.create_project(
        CreateProjectCommand(owner_id=owner1, name="Shared Name")
    )
    r2 = await module.create_project(
        CreateProjectCommand(owner_id=owner2, name="Shared Name")
    )
    assert isinstance(r1, Ok)
    assert isinstance(r2, Ok)


@pytest.mark.asyncio
async def test_update_project(session: AsyncSession) -> None:
    owner_id = await _create_user(session, "owner_upd@example.com")
    module = _make_module(session)

    project = (
        await module.create_project(
            CreateProjectCommand(owner_id=owner_id, name="Before", description="Old")
        )
    ).unwrap()

    updated = (
        await module.update_project(
            UpdateProjectCommand(
                owner_id=owner_id,
                project_id=project.id,
                name="After",
                description="New",
            )
        )
    ).unwrap()

    assert updated.name == "After"
    assert updated.description == "New"


@pytest.mark.asyncio
async def test_list_projects_scoped_to_owner(session: AsyncSession) -> None:
    owner1 = await _create_user(session, "list_owner1@example.com")
    owner2 = await _create_user(session, "list_owner2@example.com")
    module = _make_module(session)

    for i in range(3):
        await module.create_project(
            CreateProjectCommand(owner_id=owner1, name=f"O1 Project {i}")
        )
    await module.create_project(
        CreateProjectCommand(owner_id=owner2, name="O2 Only Project")
    )

    page = await module.list_projects(
        ListProjectsQuery(owner_id=owner1, page=PageParams(page=1, size=10))
    )
    assert page.total == 3
    assert all(p.owner_id == owner1 for p in page.items)


@pytest.mark.asyncio
async def test_delete_project(session: AsyncSession) -> None:
    owner_id = await _create_user(session, "owner_del@example.com")
    module = _make_module(session)

    project = (
        await module.create_project(
            CreateProjectCommand(owner_id=owner_id, name="To Delete")
        )
    ).unwrap()

    delete_result = await module.delete_project(
        owner_id=owner_id, project_id=project.id
    )
    assert isinstance(delete_result, Ok)

    get_result = await module.get_project(
        GetProjectQuery(owner_id=owner_id, project_id=project.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, ProjectNotFoundError)
