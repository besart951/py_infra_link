from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.project.domain.models import Project
from app.modules.project.domain.value_objects import ProjectName
from app.modules.project.infrastructure.sqlalchemy_models import ProjectOrm
from app.shared.ids import ProjectId, UserId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class SqlAlchemyProjectAdapter:
    _session: AsyncSession

    async def get_by_id(self, project_id: ProjectId) -> Project | None:
        stmt = select(ProjectOrm).where(ProjectOrm.id == project_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_owner_and_name(
        self, owner_id: UserId, name: ProjectName
    ) -> Project | None:
        stmt = select(ProjectOrm).where(
            ProjectOrm.owner_id == owner_id,
            ProjectOrm.name == name.value,
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def create(self, project: Project) -> Project:
        orm = ProjectOrm(
            id=project.id,
            owner_id=project.owner_id,
            name=project.name,
            description=project.description,
            created_at=project.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return project

    async def update(self, project: Project) -> Project:
        stmt = select(ProjectOrm).where(ProjectOrm.id == project.id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        orm.name = project.name
        orm.description = project.description
        await self._session.flush()
        return project

    async def delete(self, project_id: ProjectId) -> None:
        stmt = delete(ProjectOrm).where(ProjectOrm.id == project_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(
        self, owner_id: UserId, params: PageParams
    ) -> tuple[list[Project], int]:
        count_stmt = (
            select(func.count())
            .select_from(ProjectOrm)
            .where(ProjectOrm.owner_id == owner_id)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(ProjectOrm)
            .where(ProjectOrm.owner_id == owner_id)
            .order_by(ProjectOrm.created_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    def _to_domain(self, orm: ProjectOrm) -> Project:
        return Project(
            id=ProjectId(orm.id),
            owner_id=UserId(orm.owner_id),
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
        )
