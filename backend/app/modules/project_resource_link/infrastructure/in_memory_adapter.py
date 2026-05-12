from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from app.modules.project_resource_link.domain.models import (
    ProjectResourceLink,
    ResourceType,
)
from app.shared.ids import ProjectId, ProjectResourceLinkId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class InMemoryProjectResourceLinkAdapter:
    _links: dict[ProjectResourceLinkId, ProjectResourceLink] = field(
        default_factory=dict
    )

    async def get_by_id(
        self, link_id: ProjectResourceLinkId
    ) -> ProjectResourceLink | None:
        return self._links.get(link_id)

    async def get_by_project_and_resource(
        self,
        project_id: ProjectId,
        resource_type: ResourceType,
        resource_id: uuid.UUID,
    ) -> ProjectResourceLink | None:
        for link in self._links.values():
            if (
                link.project_id == project_id
                and link.resource_type == resource_type
                and link.resource_id == resource_id
            ):
                return link
        return None

    async def create(self, link: ProjectResourceLink) -> ProjectResourceLink:
        self._links[link.id] = link
        return link

    async def create_many(
        self, links: list[ProjectResourceLink]
    ) -> list[ProjectResourceLink]:
        for link in links:
            self._links[link.id] = link
        return links

    async def delete(self, link_id: ProjectResourceLinkId) -> None:
        self._links.pop(link_id, None)

    async def list_page(
        self, project_id: ProjectId, params: PageParams
    ) -> tuple[list[ProjectResourceLink], int]:
        all_items = sorted(
            [lnk for lnk in self._links.values() if lnk.project_id == project_id],
            key=lambda lnk: lnk.linked_at,
            reverse=True,
        )
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total
