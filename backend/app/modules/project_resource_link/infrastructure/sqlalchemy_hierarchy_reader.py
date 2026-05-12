from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.building.infrastructure.sqlalchemy_models import BuildingOrm
from app.modules.control_cabinet.infrastructure.sqlalchemy_models import ControlCabinetOrm
from app.modules.field_device.infrastructure.sqlalchemy_models import FieldDeviceOrm
from app.modules.sps_controller.infrastructure.sqlalchemy_models import SpsControllerOrm
from app.shared.ids import (
    BuildingId,
    ControlCabinetId,
    FieldDeviceId,
    SpsControllerId,
)


@dataclass(frozen=True, slots=True)
class SqlAlchemyHierarchyReader:
    _session: AsyncSession

    async def building_exists(self, building_id: BuildingId) -> bool:
        stmt = select(BuildingOrm.id).where(BuildingOrm.id == building_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def list_cabinet_ids_for_building(
        self, building_id: BuildingId
    ) -> list[ControlCabinetId]:
        stmt = select(ControlCabinetOrm.id).where(
            ControlCabinetOrm.building_id == building_id
        )
        result = await self._session.execute(stmt)
        return [ControlCabinetId(row) for row in result.scalars().all()]

    async def list_controller_ids_for_cabinet(
        self, cabinet_id: ControlCabinetId
    ) -> list[SpsControllerId]:
        stmt = select(SpsControllerOrm.id).where(
            SpsControllerOrm.cabinet_id == cabinet_id
        )
        result = await self._session.execute(stmt)
        return [SpsControllerId(row) for row in result.scalars().all()]

    async def list_device_ids_for_controller(
        self, controller_id: SpsControllerId
    ) -> list[FieldDeviceId]:
        stmt = select(FieldDeviceOrm.id).where(
            FieldDeviceOrm.controller_id == controller_id
        )
        result = await self._session.execute(stmt)
        return [FieldDeviceId(row) for row in result.scalars().all()]
