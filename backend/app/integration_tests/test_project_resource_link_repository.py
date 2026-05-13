"""Integration tests for SqlAlchemyProjectResourceLinkAdapter against a real PostgreSQL database."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.facility.application.commands import CreateFacilityCommand
from app.modules.facility.application.use_cases import FacilityModule
from app.modules.facility.infrastructure.sqlalchemy_adapter import SqlAlchemyFacilityAdapter
from app.modules.live_update.infrastructure.null_publisher import NullEventPublisher
from app.modules.project.application.commands import CreateProjectCommand
from app.modules.project.application.use_cases import ProjectModule
from app.modules.project.infrastructure.sqlalchemy_adapter import SqlAlchemyProjectAdapter
from app.modules.project_resource_link.application.commands import (
    LinkResourceCommand,
    UnlinkResourceCommand,
)
from app.modules.project_resource_link.application.queries import ListLinksQuery
from app.modules.project_resource_link.application.use_cases import ProjectResourceLinkModule
from app.modules.project_resource_link.domain.errors import (
    ProjectResourceLinkNotFoundError,
    ResourceAlreadyLinkedError,
)
from app.modules.project_resource_link.domain.models import ResourceType
from app.modules.project_resource_link.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyProjectResourceLinkAdapter,
)
from app.modules.project_resource_link.infrastructure.sqlalchemy_hierarchy_reader import (
    SqlAlchemyHierarchyReader,
)
from app.modules.user.application.commands import CreateUserCommand
from app.modules.user.application.use_cases import UserModule
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.shared.clock import FixedClock
from app.shared.ids import FacilityId, ProjectId, UserId
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


async def _create_user_and_project(
    session: AsyncSession, suffix: str = "PRL"
) -> tuple[UserId, ProjectId]:
    user = (
        await UserModule(
            repository=SqlAlchemyUserAdapter(session), clock=FixedClock(_FIXED)
        ).create_user(
            CreateUserCommand(
                email=f"prl_{suffix}@example.com", display_name=f"PRL User {suffix}"
            )
        )
    ).unwrap()

    project = (
        await ProjectModule(
            project_repository=SqlAlchemyProjectAdapter(session),
            user_repository=SqlAlchemyUserAdapter(session),
            clock=FixedClock(_FIXED),
            event_publisher=NullEventPublisher(),
        ).create_project(
            CreateProjectCommand(owner_id=user.id, name=f"PRL Project {suffix}")
        )
    ).unwrap()

    return user.id, project.id


async def _create_facility_id(
    session: AsyncSession, suffix: str = "PRL"
) -> FacilityId:
    facility = (
        await FacilityModule(
            repository=SqlAlchemyFacilityAdapter(session), clock=FixedClock(_FIXED)
        ).create_facility(CreateFacilityCommand(name=f"Facility PRL {suffix}"))
    ).unwrap()
    return facility.id


def _make_module(session: AsyncSession) -> ProjectResourceLinkModule:
    return ProjectResourceLinkModule(
        link_repository=SqlAlchemyProjectResourceLinkAdapter(session),
        project_repository=SqlAlchemyProjectAdapter(session),
        hierarchy_reader=SqlAlchemyHierarchyReader(session),
        clock=FixedClock(_FIXED),
        event_publisher=NullEventPublisher(),
    )


@pytest.mark.asyncio
async def test_link_and_list_resources(session: AsyncSession) -> None:
    owner_id, project_id = await _create_user_and_project(session, "LinkList")
    facility_id = await _create_facility_id(session, "LinkList")
    module = _make_module(session)

    result = await module.link_resource(
        LinkResourceCommand(
            owner_id=owner_id,
            project_id=project_id,
            resource_type=ResourceType.FACILITY,
            resource_id=uuid.UUID(str(facility_id)),
        )
    )
    assert isinstance(result, Ok)
    link = result.value
    assert link.resource_type == ResourceType.FACILITY
    assert link.project_id == project_id

    page = (
        await module.list_links(
            ListLinksQuery(
                owner_id=owner_id,
                project_id=project_id,
                page=PageParams(page=1, size=10),
            )
        )
    ).unwrap()
    assert page.total == 1
    assert page.items[0].id == link.id


@pytest.mark.asyncio
async def test_link_resource_already_linked_raises_conflict(session: AsyncSession) -> None:
    owner_id, project_id = await _create_user_and_project(session, "AlreadyLinked")
    facility_id = await _create_facility_id(session, "AlreadyLinked")
    module = _make_module(session)

    first = await module.link_resource(
        LinkResourceCommand(
            owner_id=owner_id,
            project_id=project_id,
            resource_type=ResourceType.FACILITY,
            resource_id=uuid.UUID(str(facility_id)),
        )
    )
    assert isinstance(first, Ok)

    second = await module.link_resource(
        LinkResourceCommand(
            owner_id=owner_id,
            project_id=project_id,
            resource_type=ResourceType.FACILITY,
            resource_id=uuid.UUID(str(facility_id)),
        )
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, ResourceAlreadyLinkedError)


@pytest.mark.asyncio
async def test_unlink_resource(session: AsyncSession) -> None:
    owner_id, project_id = await _create_user_and_project(session, "Unlink")
    facility_id = await _create_facility_id(session, "Unlink")
    module = _make_module(session)

    link = (
        await module.link_resource(
            LinkResourceCommand(
                owner_id=owner_id,
                project_id=project_id,
                resource_type=ResourceType.FACILITY,
                resource_id=uuid.UUID(str(facility_id)),
            )
        )
    ).unwrap()

    unlink_result = await module.unlink_resource(
        UnlinkResourceCommand(
            owner_id=owner_id,
            project_id=project_id,
            link_id=link.id,
        )
    )
    assert isinstance(unlink_result, Ok)

    page = (
        await module.list_links(
            ListLinksQuery(
                owner_id=owner_id,
                project_id=project_id,
                page=PageParams(page=1, size=10),
            )
        )
    ).unwrap()
    assert page.total == 0


@pytest.mark.asyncio
async def test_unlink_not_found_raises_error(session: AsyncSession) -> None:
    from app.shared.ids import ProjectResourceLinkId, new_id

    owner_id, project_id = await _create_user_and_project(session, "UnlinkNF")
    module = _make_module(session)

    result = await module.unlink_resource(
        UnlinkResourceCommand(
            owner_id=owner_id,
            project_id=project_id,
            link_id=new_id(ProjectResourceLinkId),
        )
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, ProjectResourceLinkNotFoundError)


@pytest.mark.asyncio
async def test_link_multiple_resource_types(session: AsyncSession) -> None:
    owner_id, project_id = await _create_user_and_project(session, "MultiType")
    facility_id = await _create_facility_id(session, "MultiType")
    module = _make_module(session)

    resource_id = uuid.UUID(str(facility_id))

    fac_link = (
        await module.link_resource(
            LinkResourceCommand(
                owner_id=owner_id,
                project_id=project_id,
                resource_type=ResourceType.FACILITY,
                resource_id=resource_id,
            )
        )
    ).unwrap()

    # Same UUID but different ResourceType is allowed (different combination)
    bld_link = (
        await module.link_resource(
            LinkResourceCommand(
                owner_id=owner_id,
                project_id=project_id,
                resource_type=ResourceType.BUILDING,
                resource_id=resource_id,
            )
        )
    ).unwrap()

    page = (
        await module.list_links(
            ListLinksQuery(
                owner_id=owner_id,
                project_id=project_id,
                page=PageParams(page=1, size=10),
            )
        )
    ).unwrap()
    assert page.total == 2
    ids = {link.id for link in page.items}
    assert fac_link.id in ids
    assert bld_link.id in ids


@pytest.mark.asyncio
async def test_list_links_scoped_to_project(session: AsyncSession) -> None:
    owner_id, p1 = await _create_user_and_project(session, "ScopeP1")
    _, _p2 = await _create_user_and_project(session, "ScopeP2")
    module = _make_module(session)

    for i in range(3):
        facility_id = await _create_facility_id(session, f"ScopeList{i}")
        await module.link_resource(
            LinkResourceCommand(
                owner_id=owner_id,
                project_id=p1,
                resource_type=ResourceType.FACILITY,
                resource_id=uuid.UUID(str(facility_id)),
            )
        )

    page = (
        await module.list_links(
            ListLinksQuery(
                owner_id=owner_id,
                project_id=p1,
                page=PageParams(page=1, size=10),
            )
        )
    ).unwrap()
    assert page.total == 3
    assert all(link.project_id == p1 for link in page.items)
