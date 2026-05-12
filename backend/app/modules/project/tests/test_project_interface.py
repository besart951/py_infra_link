from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.project.application.commands import CreateProjectCommand, UpdateProjectCommand
from app.modules.project.application.queries import GetProjectQuery, ListProjectsQuery
from app.modules.project.application.use_cases import ProjectModule
from app.modules.project.domain.errors import (
    InvalidProjectNameError,
    ProjectNameConflictError,
    ProjectNotFoundError,
    UserDoesNotExistError,
)
from app.modules.project.infrastructure.in_memory_adapter import InMemoryProjectAdapter
from app.modules.user.domain.models import User
from app.modules.user.infrastructure.in_memory_adapter import InMemoryUserAdapter
from app.shared.clock import FixedClock
from app.shared.ids import ProjectId, UserId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, tzinfo=UTC))


@pytest.fixture
def user_repo() -> InMemoryUserAdapter:
    return InMemoryUserAdapter()


@pytest.fixture
def project_repo() -> InMemoryProjectAdapter:
    return InMemoryProjectAdapter()


@pytest.fixture
def module(
    project_repo: InMemoryProjectAdapter,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> ProjectModule:
    return ProjectModule(
        project_repository=project_repo,
        user_repository=user_repo,
        clock=clock,
    )


async def _seed_user(user_repo: InMemoryUserAdapter, clock: FixedClock) -> User:
    user = User(
        id=new_id(UserId),
        email=f"user_{new_id(UserId)}@example.com",
        display_name="Test User",
        created_at=clock.now(),
    )
    await user_repo.create(user)
    return user


@pytest.mark.asyncio
async def test_create_project_success(
    module: ProjectModule,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> None:
    user = await _seed_user(user_repo, clock)

    result = await module.create_project(
        CreateProjectCommand(
            owner_id=user.id,
            name=" My Project ",
            description="A test project",
        )
    )

    assert isinstance(result, Ok)
    project = result.unwrap()
    assert project.name == "My Project"
    assert project.owner_id == user.id
    assert project.description == "A test project"
    assert project.created_at == clock.now()


@pytest.mark.asyncio
async def test_create_project_owner_missing(
    module: ProjectModule,
) -> None:
    result = await module.create_project(
        CreateProjectCommand(
            owner_id=new_id(UserId),
            name="Project 1",
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, UserDoesNotExistError)


@pytest.mark.asyncio
async def test_create_project_duplicate_name_for_same_owner(
    module: ProjectModule,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> None:
    user = await _seed_user(user_repo, clock)

    await module.create_project(
        CreateProjectCommand(owner_id=user.id, name="My Project")
    )
    result = await module.create_project(
        CreateProjectCommand(owner_id=user.id, name="My Project")
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ProjectNameConflictError)


@pytest.mark.asyncio
async def test_create_project_same_name_different_owners(
    module: ProjectModule,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> None:
    user_a = await _seed_user(user_repo, clock)
    user_b = await _seed_user(user_repo, clock)

    result_a = await module.create_project(
        CreateProjectCommand(owner_id=user_a.id, name="My Project")
    )
    result_b = await module.create_project(
        CreateProjectCommand(owner_id=user_b.id, name="My Project")
    )

    assert isinstance(result_a, Ok)
    assert isinstance(result_b, Ok)


@pytest.mark.asyncio
async def test_create_project_empty_name(
    module: ProjectModule,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> None:
    user = await _seed_user(user_repo, clock)

    result = await module.create_project(
        CreateProjectCommand(owner_id=user.id, name="   ")
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidProjectNameError)


@pytest.mark.asyncio
async def test_get_project_success(
    module: ProjectModule,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> None:
    user = await _seed_user(user_repo, clock)
    created = (
        await module.create_project(
            CreateProjectCommand(owner_id=user.id, name="Project 1")
        )
    ).unwrap()

    result = await module.get_project(
        GetProjectQuery(owner_id=user.id, project_id=created.id)
    )

    assert isinstance(result, Ok)
    assert result.unwrap().id == created.id


@pytest.mark.asyncio
async def test_get_project_not_found(
    module: ProjectModule,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> None:
    user = await _seed_user(user_repo, clock)

    result = await module.get_project(
        GetProjectQuery(owner_id=user.id, project_id=new_id(ProjectId))
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ProjectNotFoundError)


@pytest.mark.asyncio
async def test_list_projects(
    module: ProjectModule,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> None:
    user = await _seed_user(user_repo, clock)

    await module.create_project(CreateProjectCommand(owner_id=user.id, name="Project A"))
    await module.create_project(CreateProjectCommand(owner_id=user.id, name="Project B"))

    page = await module.list_projects(
        ListProjectsQuery(owner_id=user.id, page=PageParams(page=1, size=10))
    )
    assert page.total == 2
    assert len(page.items) == 2


@pytest.mark.asyncio
async def test_update_project_success(
    module: ProjectModule,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> None:
    user = await _seed_user(user_repo, clock)
    created = (
        await module.create_project(
            CreateProjectCommand(owner_id=user.id, name="Old Name", description="Old desc")
        )
    ).unwrap()

    result = await module.update_project(
        UpdateProjectCommand(
            owner_id=user.id,
            project_id=created.id,
            name="New Name",
            description="New desc",
        )
    )

    assert isinstance(result, Ok)
    updated = result.unwrap()
    assert updated.name == "New Name"
    assert updated.description == "New desc"


@pytest.mark.asyncio
async def test_delete_project_success(
    module: ProjectModule,
    user_repo: InMemoryUserAdapter,
    clock: FixedClock,
) -> None:
    user = await _seed_user(user_repo, clock)
    created = (
        await module.create_project(
            CreateProjectCommand(owner_id=user.id, name="To Delete")
        )
    ).unwrap()

    result = await module.delete_project(owner_id=user.id, project_id=created.id)
    assert isinstance(result, Ok)

    get_result = await module.get_project(
        GetProjectQuery(owner_id=user.id, project_id=created.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, ProjectNotFoundError)
