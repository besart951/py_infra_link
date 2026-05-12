from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.live_update.domain.interface import EventPublisher
from app.modules.live_update.presentation.routes import get_event_publisher
from app.modules.project.infrastructure.sqlalchemy_adapter import SqlAlchemyProjectAdapter
from app.modules.project_resource_link.application.commands import (
    ImportBuildingCommand,
    LinkResourceCommand,
    UnlinkResourceCommand,
)
from app.modules.project_resource_link.application.queries import ListLinksQuery
from app.modules.project_resource_link.application.use_cases import (
    ProjectResourceLinkModule,
)
from app.modules.project_resource_link.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyProjectResourceLinkAdapter,
)
from app.modules.project_resource_link.infrastructure.sqlalchemy_hierarchy_reader import (
    SqlAlchemyHierarchyReader,
)
from app.modules.project_resource_link.presentation.error_mapping import map_link_error
from app.modules.project_resource_link.presentation.schemas import (
    ImportBuildingResponse,
    LinkResourceRequest,
    ProjectResourceLinkRead,
)
from app.shared.clock import SystemClock
from app.shared.ids import BuildingId, ProjectId, ProjectResourceLinkId, UserId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(
    prefix="/users/{owner_id}/projects/{project_id}/links",
    tags=["project-resource-links"],
)

import_router = APIRouter(
    prefix="/users/{owner_id}/projects/{project_id}/import",
    tags=["project-resource-links"],
)


def _make_module(
    session: AsyncSession, event_publisher: EventPublisher
) -> ProjectResourceLinkModule:
    return ProjectResourceLinkModule(
        link_repository=SqlAlchemyProjectResourceLinkAdapter(session),
        project_repository=SqlAlchemyProjectAdapter(session),
        hierarchy_reader=SqlAlchemyHierarchyReader(session),
        clock=SystemClock(),
        event_publisher=event_publisher,
    )


@router.post("", response_model=ProjectResourceLinkRead, status_code=status.HTTP_201_CREATED)
async def link_resource(
    owner_id: UUID,
    project_id: UUID,
    request: LinkResourceRequest,
    session: AsyncSession = Depends(get_session),  # noqa: B008
    event_publisher: EventPublisher = Depends(get_event_publisher),  # noqa: B008
) -> ProjectResourceLinkRead:
    module = _make_module(session, event_publisher)
    result = await module.link_resource(
        LinkResourceCommand(
            owner_id=UserId(owner_id),
            project_id=ProjectId(project_id),
            resource_type=request.resource_type,
            resource_id=request.resource_id,
        )
    )

    if isinstance(result, Ok):
        return ProjectResourceLinkRead.model_validate(result.value)

    raise map_link_error(result.error)


@router.get("", response_model=Page[ProjectResourceLinkRead])
async def list_links(
    owner_id: UUID,
    project_id: UUID,
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
    event_publisher: EventPublisher = Depends(get_event_publisher),  # noqa: B008
) -> Page[ProjectResourceLinkRead]:
    module = _make_module(session, event_publisher)
    result = await module.list_links(
        ListLinksQuery(
            owner_id=UserId(owner_id),
            project_id=ProjectId(project_id),
            page=PageParams(page=page, size=size),
        )
    )

    if isinstance(result, Ok):
        links_page = result.value
        return Page[ProjectResourceLinkRead](
            items=[
                ProjectResourceLinkRead.model_validate(item)
                for item in links_page.items
            ],
            total=links_page.total,
            page=links_page.page,
            size=links_page.size,
        )

    raise map_link_error(result.error)


@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_resource(
    owner_id: UUID,
    project_id: UUID,
    link_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
    event_publisher: EventPublisher = Depends(get_event_publisher),  # noqa: B008
) -> Response:
    module = _make_module(session, event_publisher)
    result = await module.unlink_resource(
        UnlinkResourceCommand(
            owner_id=UserId(owner_id),
            project_id=ProjectId(project_id),
            link_id=ProjectResourceLinkId(link_id),
        )
    )

    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise map_link_error(result.error)


@import_router.post(
    "/building/{building_id}",
    response_model=ImportBuildingResponse,
    status_code=status.HTTP_200_OK,
)
async def import_building(
    owner_id: UUID,
    project_id: UUID,
    building_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
    event_publisher: EventPublisher = Depends(get_event_publisher),  # noqa: B008
) -> ImportBuildingResponse:
    module = _make_module(session, event_publisher)
    result = await module.import_building(
        ImportBuildingCommand(
            owner_id=UserId(owner_id),
            project_id=ProjectId(project_id),
            building_id=BuildingId(building_id),
        )
    )

    if isinstance(result, Ok):
        return ImportBuildingResponse(
            linked=result.value.linked,
            skipped=result.value.skipped,
        )

    raise map_link_error(result.error)
