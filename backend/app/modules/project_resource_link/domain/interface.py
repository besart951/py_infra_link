from __future__ import annotations

import uuid
from typing import Protocol

from app.modules.project_resource_link.domain.models import ProjectResourceLink, ResourceType
from app.shared.ids import (
    BuildingId,
    ControlCabinetId,
    FieldDeviceId,
    ProjectId,
    ProjectResourceLinkId,
    SpsControllerId,
)
from app.shared.pagination import PageParams


class ProjectResourceLinkRepository(Protocol):
    async def get_by_id(
        self, link_id: ProjectResourceLinkId
    ) -> ProjectResourceLink | None: ...

    async def get_by_project_and_resource(
        self,
        project_id: ProjectId,
        resource_type: ResourceType,
        resource_id: uuid.UUID,
    ) -> ProjectResourceLink | None: ...

    async def create(self, link: ProjectResourceLink) -> ProjectResourceLink: ...

    async def create_many(
        self, links: list[ProjectResourceLink]
    ) -> list[ProjectResourceLink]: ...

    async def delete(self, link_id: ProjectResourceLinkId) -> None: ...

    async def list_page(
        self, project_id: ProjectId, params: PageParams
    ) -> tuple[list[ProjectResourceLink], int]: ...


class HierarchyReader(Protocol):
    """Read-only port for traversing the infrastructure hierarchy during import."""

    async def building_exists(self, building_id: BuildingId) -> bool: ...

    async def list_cabinet_ids_for_building(
        self, building_id: BuildingId
    ) -> list[ControlCabinetId]: ...

    async def list_controller_ids_for_cabinet(
        self, cabinet_id: ControlCabinetId
    ) -> list[SpsControllerId]: ...

    async def list_device_ids_for_controller(
        self, controller_id: SpsControllerId
    ) -> list[FieldDeviceId]: ...
