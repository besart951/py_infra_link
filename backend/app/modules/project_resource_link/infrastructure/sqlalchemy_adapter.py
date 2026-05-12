from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.project_resource_link.domain.models import (
    ProjectResourceLink,
    ResourceType,
)
from app.modules.project_resource_link.infrastructure.sqlalchemy_models import (
    ProjectResourceLinkOrm,
)
from app.shared.ids import ProjectId, ProjectResourceLinkId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class SqlAlchemyProjectResourceLinkAdapter:
    _session: AsyncSession

    async def get_by_id(
        self, link_id: ProjectResourceLinkId
    ) -> ProjectResourceLink | None:
        stmt = select(ProjectResourceLinkOrm).where(
            ProjectResourceLinkOrm.id == link_id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_project_and_resource(
        self,
        project_id: ProjectId,
        resource_type: ResourceType,
        resource_id: uuid.UUID,
    ) -> ProjectResourceLink | None:
        stmt = select(ProjectResourceLinkOrm).where(
            ProjectResourceLinkOrm.project_id == project_id,
            ProjectResourceLinkOrm.resource_type == str(resource_type),
            ProjectResourceLinkOrm.resource_id == resource_id,
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def create(self, link: ProjectResourceLink) -> ProjectResourceLink:
        orm = ProjectResourceLinkOrm(
            id=link.id,
            project_id=link.project_id,
            resource_type=str(link.resource_type),
            resource_id=link.resource_id,
            linked_at=link.linked_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return link

    async def create_many(
        self, links: list[ProjectResourceLink]
    ) -> list[ProjectResourceLink]:
        for link in links:
            orm = ProjectResourceLinkOrm(
                id=link.id,
                project_id=link.project_id,
                resource_type=str(link.resource_type),
                resource_id=link.resource_id,
                linked_at=link.linked_at,
            )
            self._session.add(orm)
        await self._session.flush()
        return links

    async def delete(self, link_id: ProjectResourceLinkId) -> None:
        stmt = delete(ProjectResourceLinkOrm).where(
            ProjectResourceLinkOrm.id == link_id
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(
        self, project_id: ProjectId, params: PageParams
    ) -> tuple[list[ProjectResourceLink], int]:
        count_stmt = (
            select(func.count())
            .select_from(ProjectResourceLinkOrm)
            .where(ProjectResourceLinkOrm.project_id == project_id)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(ProjectResourceLinkOrm)
            .where(ProjectResourceLinkOrm.project_id == project_id)
            .order_by(ProjectResourceLinkOrm.linked_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    def _to_domain(self, orm: ProjectResourceLinkOrm) -> ProjectResourceLink:
        return ProjectResourceLink(
            id=ProjectResourceLinkId(orm.id),
            project_id=ProjectId(orm.project_id),
            resource_type=ResourceType(orm.resource_type),
            resource_id=uuid.UUID(str(orm.resource_id)),
            linked_at=orm.linked_at,
        )
