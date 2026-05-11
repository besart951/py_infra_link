from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sps_controller_system_type.domain.models import SpsControllerSystemType
from app.modules.sps_controller_system_type.domain.value_objects import SpsControllerSystemTypeName
from app.modules.sps_controller_system_type.infrastructure.sqlalchemy_models import (
    SpsControllerSystemTypeOrm,
)
from app.shared.ids import SpsControllerSystemTypeId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class SqlAlchemySpsControllerSystemTypeAdapter:
    _session: AsyncSession

    async def get_by_id(
        self, system_type_id: SpsControllerSystemTypeId
    ) -> SpsControllerSystemType | None:
        stmt = select(SpsControllerSystemTypeOrm).where(
            SpsControllerSystemTypeOrm.id == system_type_id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_name(
        self, name: SpsControllerSystemTypeName
    ) -> SpsControllerSystemType | None:
        stmt = select(SpsControllerSystemTypeOrm).where(
            SpsControllerSystemTypeOrm.name == name.value
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def create(self, system_type: SpsControllerSystemType) -> SpsControllerSystemType:
        orm = SpsControllerSystemTypeOrm(
            id=system_type.id,
            name=system_type.name,
            description=system_type.description,
            created_at=system_type.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return system_type

    async def update(self, system_type: SpsControllerSystemType) -> SpsControllerSystemType:
        stmt = select(SpsControllerSystemTypeOrm).where(
            SpsControllerSystemTypeOrm.id == system_type.id
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        orm.name = system_type.name
        orm.description = system_type.description
        await self._session.flush()
        return system_type

    async def delete(self, system_type_id: SpsControllerSystemTypeId) -> None:
        stmt = delete(SpsControllerSystemTypeOrm).where(
            SpsControllerSystemTypeOrm.id == system_type_id
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(self, params: PageParams) -> tuple[list[SpsControllerSystemType], int]:
        # Count
        count_stmt = select(func.count()).select_from(SpsControllerSystemTypeOrm)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Items
        stmt = (
            select(SpsControllerSystemTypeOrm)
            .order_by(SpsControllerSystemTypeOrm.created_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    def _to_domain(self, orm: SpsControllerSystemTypeOrm) -> SpsControllerSystemType:
        return SpsControllerSystemType(
            id=SpsControllerSystemTypeId(orm.id),
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
        )
