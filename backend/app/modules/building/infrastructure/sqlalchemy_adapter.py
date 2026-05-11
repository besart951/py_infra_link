from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.building.domain.models import Building
from app.modules.building.domain.value_objects import BuildingName
from app.modules.building.infrastructure.sqlalchemy_models import BuildingOrm
from app.shared.ids import BuildingId, FacilityId
from app.shared.pagination import PageParams


class SqlAlchemyBuildingAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, building_id: BuildingId) -> Building | None:
        stmt = select(BuildingOrm).where(BuildingOrm.id == building_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_facility_and_name(
        self, facility_id: FacilityId, name: BuildingName
    ) -> Building | None:
        stmt = select(BuildingOrm).where(
            BuildingOrm.facility_id == facility_id, BuildingOrm.name == name.value
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def create(self, building: Building) -> Building:
        orm = BuildingOrm(
            id=building.id,
            facility_id=building.facility_id,
            name=building.name,
            description=building.description,
            created_at=building.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return building

    async def update(self, building: Building) -> Building:
        stmt = select(BuildingOrm).where(BuildingOrm.id == building.id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        orm.name = building.name
        orm.description = building.description
        await self._session.flush()
        return building

    async def delete(self, building_id: BuildingId) -> None:
        stmt = delete(BuildingOrm).where(BuildingOrm.id == building_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(
        self, facility_id: FacilityId, params: PageParams
    ) -> tuple[list[Building], int]:
        # Count
        count_stmt = (
            select(func.count())
            .select_from(BuildingOrm)
            .where(BuildingOrm.facility_id == facility_id)
        )

        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Items
        stmt = (
            select(BuildingOrm)
            .where(BuildingOrm.facility_id == facility_id)
            .order_by(BuildingOrm.created_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    def _to_domain(self, orm: BuildingOrm) -> Building:
        return Building(
            id=BuildingId(orm.id),
            facility_id=FacilityId(orm.facility_id),
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
        )
