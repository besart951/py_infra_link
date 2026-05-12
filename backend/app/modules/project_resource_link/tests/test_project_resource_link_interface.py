from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from app.modules.project.domain.models import Project
from app.modules.project.infrastructure.in_memory_adapter import InMemoryProjectAdapter
from app.modules.project_resource_link.application.commands import (
    ImportBuildingCommand,
    LinkResourceCommand,
    UnlinkResourceCommand,
)
from app.modules.project_resource_link.application.queries import ListLinksQuery
from app.modules.project_resource_link.application.use_cases import (
    ProjectResourceLinkModule,
)
from app.modules.project_resource_link.domain.errors import (
    BuildingDoesNotExistError,
    ProjectDoesNotExistError,
    ProjectResourceLinkNotFoundError,
    ResourceAlreadyLinkedError,
)
from app.modules.project_resource_link.domain.models import ResourceType
from app.modules.project_resource_link.infrastructure.in_memory_adapter import (
    InMemoryProjectResourceLinkAdapter,
)
from app.modules.project_resource_link.infrastructure.in_memory_hierarchy_reader import (
    InMemoryHierarchyReader,
)
from app.shared.clock import FixedClock
from app.shared.ids import (
    BuildingId,
    ControlCabinetId,
    FieldDeviceId,
    ProjectId,
    ProjectResourceLinkId,
    SpsControllerId,
    UserId,
    new_id,
)
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, tzinfo=UTC))


@pytest.fixture
def owner_id() -> UserId:
    return new_id(UserId)


@pytest.fixture
def project_repo() -> InMemoryProjectAdapter:
    return InMemoryProjectAdapter()


@pytest.fixture
def link_repo() -> InMemoryProjectResourceLinkAdapter:
    return InMemoryProjectResourceLinkAdapter()


@pytest.fixture
def hierarchy() -> InMemoryHierarchyReader:
    return InMemoryHierarchyReader()


@pytest.fixture
def module(
    link_repo: InMemoryProjectResourceLinkAdapter,
    project_repo: InMemoryProjectAdapter,
    hierarchy: InMemoryHierarchyReader,
    clock: FixedClock,
) -> ProjectResourceLinkModule:
    return ProjectResourceLinkModule(
        link_repository=link_repo,
        project_repository=project_repo,
        hierarchy_reader=hierarchy,
        clock=clock,
    )


async def _seed_project(
    project_repo: InMemoryProjectAdapter, owner_id: UserId, clock: FixedClock
) -> Project:
    project = Project(
        id=new_id(ProjectId),
        owner_id=owner_id,
        name="Test Project",
        description=None,
        created_at=clock.now(),
    )
    return await project_repo.create(project)


# ── Link resource ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_link_resource_success(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    owner_id: UserId,
    clock: FixedClock,
) -> None:
    project = await _seed_project(project_repo, owner_id, clock)
    resource_id = uuid.uuid4()

    result = await module.link_resource(
        LinkResourceCommand(
            owner_id=owner_id,
            project_id=project.id,
            resource_type=ResourceType.BUILDING,
            resource_id=resource_id,
        )
    )

    assert isinstance(result, Ok)
    link = result.unwrap()
    assert link.project_id == project.id
    assert link.resource_type == ResourceType.BUILDING
    assert link.resource_id == resource_id
    assert link.linked_at == clock.now()


@pytest.mark.asyncio
async def test_link_resource_project_not_found(
    module: ProjectResourceLinkModule,
    owner_id: UserId,
) -> None:
    result = await module.link_resource(
        LinkResourceCommand(
            owner_id=owner_id,
            project_id=new_id(ProjectId),
            resource_type=ResourceType.BUILDING,
            resource_id=uuid.uuid4(),
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ProjectDoesNotExistError)


@pytest.mark.asyncio
async def test_link_resource_wrong_owner_treated_as_not_found(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    clock: FixedClock,
) -> None:
    owner = new_id(UserId)
    project = await _seed_project(project_repo, owner, clock)
    different_owner = new_id(UserId)

    result = await module.link_resource(
        LinkResourceCommand(
            owner_id=different_owner,
            project_id=project.id,
            resource_type=ResourceType.BUILDING,
            resource_id=uuid.uuid4(),
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ProjectDoesNotExistError)


@pytest.mark.asyncio
async def test_link_resource_duplicate_rejected(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    owner_id: UserId,
    clock: FixedClock,
) -> None:
    project = await _seed_project(project_repo, owner_id, clock)
    resource_id = uuid.uuid4()
    cmd = LinkResourceCommand(
        owner_id=owner_id,
        project_id=project.id,
        resource_type=ResourceType.FIELD_DEVICE,
        resource_id=resource_id,
    )

    await module.link_resource(cmd)
    result = await module.link_resource(cmd)

    assert isinstance(result, Err)
    assert isinstance(result.error, ResourceAlreadyLinkedError)


# ── Unlink resource ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_unlink_resource_success(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    owner_id: UserId,
    clock: FixedClock,
) -> None:
    project = await _seed_project(project_repo, owner_id, clock)
    resource_id = uuid.uuid4()
    link = (
        await module.link_resource(
            LinkResourceCommand(
                owner_id=owner_id,
                project_id=project.id,
                resource_type=ResourceType.BUILDING,
                resource_id=resource_id,
            )
        )
    ).unwrap()

    result = await module.unlink_resource(
        UnlinkResourceCommand(
            owner_id=owner_id,
            project_id=project.id,
            link_id=link.id,
        )
    )

    assert isinstance(result, Ok)


@pytest.mark.asyncio
async def test_unlink_resource_not_found(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    owner_id: UserId,
    clock: FixedClock,
) -> None:
    project = await _seed_project(project_repo, owner_id, clock)

    result = await module.unlink_resource(
        UnlinkResourceCommand(
            owner_id=owner_id,
            project_id=project.id,
            link_id=new_id(ProjectResourceLinkId),
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ProjectResourceLinkNotFoundError)


# ── List links ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_links_paged(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    owner_id: UserId,
    clock: FixedClock,
) -> None:
    project = await _seed_project(project_repo, owner_id, clock)

    for _ in range(3):
        await module.link_resource(
            LinkResourceCommand(
                owner_id=owner_id,
                project_id=project.id,
                resource_type=ResourceType.FACILITY,
                resource_id=uuid.uuid4(),
            )
        )

    result = await module.list_links(
        ListLinksQuery(
            owner_id=owner_id,
            project_id=project.id,
            page=PageParams(page=1, size=10),
        )
    )

    assert isinstance(result, Ok)
    page = result.unwrap()
    assert page.total == 3
    assert len(page.items) == 3


# ── Import building ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_import_building_flat(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    hierarchy: InMemoryHierarchyReader,
    owner_id: UserId,
    clock: FixedClock,
) -> None:
    """Building with 1 cabinet → 1 controller → 1 device = 4 links total."""
    project = await _seed_project(project_repo, owner_id, clock)
    building_id = new_id(BuildingId)
    cabinet_id = new_id(ControlCabinetId)
    controller_id = new_id(SpsControllerId)
    device_id = new_id(FieldDeviceId)

    hierarchy.add_building(building_id)
    hierarchy.add_cabinet(building_id, cabinet_id)
    hierarchy.add_controller(cabinet_id, controller_id)
    hierarchy.add_device(controller_id, device_id)

    result = await module.import_building(
        ImportBuildingCommand(
            owner_id=owner_id,
            project_id=project.id,
            building_id=building_id,
        )
    )

    assert isinstance(result, Ok)
    summary = result.unwrap()
    assert summary.linked == 4
    assert summary.skipped == 0


@pytest.mark.asyncio
async def test_import_building_idempotent(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    hierarchy: InMemoryHierarchyReader,
    owner_id: UserId,
    clock: FixedClock,
) -> None:
    """Re-importing the same building skips already-linked resources."""
    project = await _seed_project(project_repo, owner_id, clock)
    building_id = new_id(BuildingId)
    hierarchy.add_building(building_id)

    await module.import_building(
        ImportBuildingCommand(
            owner_id=owner_id, project_id=project.id, building_id=building_id
        )
    )
    result = await module.import_building(
        ImportBuildingCommand(
            owner_id=owner_id, project_id=project.id, building_id=building_id
        )
    )

    assert isinstance(result, Ok)
    summary = result.unwrap()
    assert summary.linked == 0
    assert summary.skipped == 1


@pytest.mark.asyncio
async def test_import_building_not_found(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    owner_id: UserId,
    clock: FixedClock,
) -> None:
    project = await _seed_project(project_repo, owner_id, clock)

    result = await module.import_building(
        ImportBuildingCommand(
            owner_id=owner_id,
            project_id=project.id,
            building_id=new_id(BuildingId),
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, BuildingDoesNotExistError)


@pytest.mark.asyncio
async def test_import_building_empty_hierarchy(
    module: ProjectResourceLinkModule,
    project_repo: InMemoryProjectAdapter,
    hierarchy: InMemoryHierarchyReader,
    owner_id: UserId,
    clock: FixedClock,
) -> None:
    """Building with no cabinets → only the building itself is linked."""
    project = await _seed_project(project_repo, owner_id, clock)
    building_id = new_id(BuildingId)
    hierarchy.add_building(building_id)

    result = await module.import_building(
        ImportBuildingCommand(
            owner_id=owner_id, project_id=project.id, building_id=building_id
        )
    )

    assert isinstance(result, Ok)
    summary = result.unwrap()
    assert summary.linked == 1
    assert summary.skipped == 0
