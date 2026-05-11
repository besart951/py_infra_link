from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.control_cabinet.domain.models import ControlCabinet
from app.modules.control_cabinet.domain.value_objects import ControlCabinetName
from app.modules.control_cabinet.infrastructure.sqlalchemy_models import ControlCabinetOrm
from app.shared.ids import BuildingId, ControlCabinetId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class SqlAlchemyControlCabinetAdapter:
    _session: AsyncSession

    async def get_by_id(self, cabinet_id: ControlCabinetId) -> ControlCabinet | None:
        stmt = select(ControlCabinetOrm).where(ControlCabinetOrm.id == cabinet_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_building_and_name(
        self, building_id: BuildingId, name: ControlCabinetName
    ) -> ControlCabinet | None:
        stmt = select(ControlCabinetOrm).where(
            ControlCabinetOrm.building_id == building_id, ControlCabinetOrm.name == name.value
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def create(self, cabinet: ControlCabinet) -> ControlCabinet:
        orm = ControlCabinetOrm(
            id=cabinet.id,
            building_id=cabinet.building_id,
            name=cabinet.name,
            description=cabinet.description,
            created_at=cabinet.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return cabinet

    async def update(self, cabinet: ControlCabinet) -> ControlCabinet:
        stmt = select(ControlCabinetOrm).where(ControlCabinetOrm.id == cabinet.id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        orm.name = cabinet.name
        orm.description = cabinet.description
        await self._session.flush()
        return cabinet

    async def delete(self, cabinet_id: ControlCabinetId) -> None:
        stmt = delete(ControlCabinetOrm).where(ControlCabinetOrm.id == cabinet_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(
        self, building_id: BuildingId, params: PageParams
    ) -> tuple[list[ControlCabinet], int]:
        # Count
        count_stmt = (
            select(func.count())
            .select_from(ControlCabinetOrm)
            .where(ControlCabinetOrm.building_id == building_id)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Items
        stmt = (
            select(ControlCabinetOrm)
            .where(ControlCabinetOrm.building_id == building_id)
            .order_by(ControlCabinetOrm.created_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    def _to_domain(self, orm: ControlCabinetOrm) -> ControlCabinet:
        return ControlCabinet(
            id=ControlCabinetId(orm.id),
            building_id=BuildingId(orm.building_id),
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
        )
