from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.modules.live_update.domain.events import DomainEvent, DomainEventType
from app.modules.live_update.domain.interface import EventPublisher
from app.modules.project.domain.interface import ProjectRepository
from app.modules.project_resource_link.application.commands import (
    ImportBuildingCommand,
    LinkResourceCommand,
    UnlinkResourceCommand,
)
from app.modules.project_resource_link.application.queries import ListLinksQuery
from app.modules.project_resource_link.domain.errors import (
    BuildingDoesNotExistError,
    ProjectDoesNotExistError,
    ProjectResourceLinkNotFoundError,
    ResourceAlreadyLinkedError,
)
from app.modules.project_resource_link.domain.interface import (
    HierarchyReader,
    ProjectResourceLinkRepository,
)
from app.modules.project_resource_link.domain.models import (
    ImportBuildingResult,
    ProjectResourceLink,
    ResourceType,
)
from app.shared.clock import Clock
from app.shared.ids import ProjectResourceLinkId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class ProjectResourceLinkModule:
    link_repository: ProjectResourceLinkRepository
    project_repository: ProjectRepository
    hierarchy_reader: HierarchyReader
    clock: Clock
    event_publisher: EventPublisher

    async def link_resource(
        self, command: LinkResourceCommand
    ) -> Result[
        ProjectResourceLink,
        ProjectDoesNotExistError | ResourceAlreadyLinkedError,
    ]:
        project = await self.project_repository.get_by_id(command.project_id)
        if project is None or project.owner_id != command.owner_id:
            return Err(
                ProjectDoesNotExistError(
                    f"Project '{command.project_id}' does not exist"
                )
            )

        existing = await self.link_repository.get_by_project_and_resource(
            command.project_id, command.resource_type, command.resource_id
        )
        if existing is not None:
            return Err(
                ResourceAlreadyLinkedError(
                    f"Resource '{command.resource_id}' of type "
                    f"'{command.resource_type}' is already linked to this project"
                )
            )

        link = ProjectResourceLink(
            id=new_id(ProjectResourceLinkId),
            project_id=command.project_id,
            resource_type=command.resource_type,
            resource_id=command.resource_id,
            linked_at=self.clock.now(),
        )
        created = await self.link_repository.create(link)
        await self.event_publisher.publish(
            DomainEvent(
                event_type=DomainEventType.PROJECT_RESOURCE_LINKED,
                aggregate_id=uuid.UUID(str(created.id)),
                payload={
                    "link_id": str(created.id),
                    "project_id": str(created.project_id),
                    "resource_type": str(created.resource_type),
                    "resource_id": str(created.resource_id),
                    "owner_id": str(command.owner_id),
                },
                occurred_at=self.clock.now(),
            )
        )
        return Ok(created)

    async def import_building(
        self, command: ImportBuildingCommand
    ) -> Result[
        ImportBuildingResult,
        ProjectDoesNotExistError | BuildingDoesNotExistError,
    ]:
        project = await self.project_repository.get_by_id(command.project_id)
        if project is None or project.owner_id != command.owner_id:
            return Err(
                ProjectDoesNotExistError(
                    f"Project '{command.project_id}' does not exist"
                )
            )

        if not await self.hierarchy_reader.building_exists(command.building_id):
            return Err(
                BuildingDoesNotExistError(
                    f"Building '{command.building_id}' does not exist"
                )
            )

        # Collect all resource (type, id) pairs in hierarchy order
        to_link: list[tuple[ResourceType, uuid.UUID]] = [
            (ResourceType.BUILDING, uuid.UUID(str(command.building_id)))
        ]

        cabinet_ids = await self.hierarchy_reader.list_cabinet_ids_for_building(
            command.building_id
        )
        for cabinet_id in cabinet_ids:
            to_link.append((ResourceType.CONTROL_CABINET, uuid.UUID(str(cabinet_id))))
            controller_ids = await self.hierarchy_reader.list_controller_ids_for_cabinet(
                cabinet_id
            )
            for controller_id in controller_ids:
                to_link.append(
                    (ResourceType.SPS_CONTROLLER, uuid.UUID(str(controller_id)))
                )
                device_ids = await self.hierarchy_reader.list_device_ids_for_controller(
                    controller_id
                )
                for device_id in device_ids:
                    to_link.append(
                        (ResourceType.FIELD_DEVICE, uuid.UUID(str(device_id)))
                    )

        now = self.clock.now()
        new_links: list[ProjectResourceLink] = []
        skipped = 0

        for resource_type, resource_id in to_link:
            existing = await self.link_repository.get_by_project_and_resource(
                command.project_id, resource_type, resource_id
            )
            if existing is not None:
                skipped += 1
            else:
                new_links.append(
                    ProjectResourceLink(
                        id=new_id(ProjectResourceLinkId),
                        project_id=command.project_id,
                        resource_type=resource_type,
                        resource_id=resource_id,
                        linked_at=now,
                    )
                )

        if new_links:
            await self.link_repository.create_many(new_links)

        result = ImportBuildingResult(linked=len(new_links), skipped=skipped)
        await self.event_publisher.publish(
            DomainEvent(
                event_type=DomainEventType.PROJECT_BUILDING_IMPORTED,
                aggregate_id=uuid.UUID(str(command.project_id)),
                payload={
                    "project_id": str(command.project_id),
                    "building_id": str(command.building_id),
                    "linked": str(result.linked),
                    "skipped": str(result.skipped),
                    "owner_id": str(command.owner_id),
                },
                occurred_at=self.clock.now(),
            )
        )
        return Ok(result)

    async def unlink_resource(
        self, command: UnlinkResourceCommand
    ) -> Result[None, ProjectDoesNotExistError | ProjectResourceLinkNotFoundError]:
        project = await self.project_repository.get_by_id(command.project_id)
        if project is None or project.owner_id != command.owner_id:
            return Err(
                ProjectDoesNotExistError(
                    f"Project '{command.project_id}' does not exist"
                )
            )

        link = await self.link_repository.get_by_id(command.link_id)
        if link is None or link.project_id != command.project_id:
            return Err(
                ProjectResourceLinkNotFoundError(
                    f"Project Resource Link '{command.link_id}' was not found"
                )
            )

        await self.link_repository.delete(command.link_id)
        await self.event_publisher.publish(
            DomainEvent(
                event_type=DomainEventType.PROJECT_RESOURCE_UNLINKED,
                aggregate_id=uuid.UUID(str(command.link_id)),
                payload={
                    "link_id": str(command.link_id),
                    "project_id": str(command.project_id),
                    "owner_id": str(command.owner_id),
                },
                occurred_at=self.clock.now(),
            )
        )
        return Ok(None)

    async def list_links(
        self, query: ListLinksQuery
    ) -> Result[Page[ProjectResourceLink], ProjectDoesNotExistError]:
        project = await self.project_repository.get_by_id(query.project_id)
        if project is None or project.owner_id != query.owner_id:
            return Err(
                ProjectDoesNotExistError(
                    f"Project '{query.project_id}' does not exist"
                )
            )

        items, total = await self.link_repository.list_page(query.project_id, query.page)
        return Ok(
            Page[ProjectResourceLink](
                items=items,
                total=total,
                page=query.page.page,
                size=query.page.size,
            )
        )
