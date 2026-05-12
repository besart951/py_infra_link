from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.field_device.domain.models import FieldDevice
from app.modules.field_device.domain.value_objects import FieldDeviceName
from app.modules.field_device.infrastructure.sqlalchemy_models import FieldDeviceOrm
from app.shared.ids import FieldDeviceId, SpsControllerId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class SqlAlchemyFieldDeviceAdapter:
    _session: AsyncSession

    async def get_by_id(self, device_id: FieldDeviceId) -> FieldDevice | None:
        stmt = select(FieldDeviceOrm).where(FieldDeviceOrm.id == device_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_controller_and_name(
        self, controller_id: SpsControllerId, name: FieldDeviceName
    ) -> FieldDevice | None:
        stmt = select(FieldDeviceOrm).where(
            FieldDeviceOrm.controller_id == controller_id,
            FieldDeviceOrm.name == name.value,
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def create(self, device: FieldDevice) -> FieldDevice:
        orm = FieldDeviceOrm(
            id=device.id,
            controller_id=device.controller_id,
            name=device.name,
            description=device.description,
            created_at=device.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return device

    async def update(self, device: FieldDevice) -> FieldDevice:
        stmt = select(FieldDeviceOrm).where(FieldDeviceOrm.id == device.id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        orm.name = device.name
        orm.description = device.description
        await self._session.flush()
        return device

    async def delete(self, device_id: FieldDeviceId) -> None:
        stmt = delete(FieldDeviceOrm).where(FieldDeviceOrm.id == device_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(
        self, controller_id: SpsControllerId, params: PageParams
    ) -> tuple[list[FieldDevice], int]:
        count_stmt = (
            select(func.count())
            .select_from(FieldDeviceOrm)
            .where(FieldDeviceOrm.controller_id == controller_id)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(FieldDeviceOrm)
            .where(FieldDeviceOrm.controller_id == controller_id)
            .order_by(FieldDeviceOrm.created_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    def _to_domain(self, orm: FieldDeviceOrm) -> FieldDevice:
        return FieldDevice(
            id=FieldDeviceId(orm.id),
            controller_id=SpsControllerId(orm.controller_id),
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
        )
