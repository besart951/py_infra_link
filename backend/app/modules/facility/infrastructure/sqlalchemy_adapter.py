from __future__ import annotations

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.facility.domain.models import Facility
from app.modules.facility.domain.value_objects import FacilityName
from app.modules.facility.infrastructure.sqlalchemy_models import FacilityOrm
from app.shared.ids import FacilityId
from app.shared.pagination import PageParams


class SqlAlchemyFacilityAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, facility_id: FacilityId) -> Facility | None:
        stmt = select(FacilityOrm).where(FacilityOrm.id == facility_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_name(self, name: FacilityName) -> Facility | None:
        stmt = select(FacilityOrm).where(FacilityOrm.name == name.value)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def create(self, facility: Facility) -> Facility:
        orm = FacilityOrm(
            id=facility.id,
            name=facility.name,
            description=facility.description,
            created_at=facility.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return facility

    async def update(self, facility: Facility) -> Facility:
        stmt = select(FacilityOrm).where(FacilityOrm.id == facility.id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        orm.name = facility.name
        orm.description = facility.description
        await self._session.flush()
        return facility

    async def delete(self, facility_id: FacilityId) -> None:
        stmt = delete(FacilityOrm).where(FacilityOrm.id == facility_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(self, params: PageParams) -> tuple[list[Facility], int]:
        # Count
        count_stmt = select(func.count()).select_from(FacilityOrm)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Items
        stmt = (
            select(FacilityOrm)
            .order_by(FacilityOrm.created_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    def _to_domain(self, orm: FacilityOrm) -> Facility:
        return Facility(
            id=FacilityId(orm.id),
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
        )
