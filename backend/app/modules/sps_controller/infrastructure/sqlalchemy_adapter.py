from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.sps_controller.domain.models import SpsController
from app.modules.sps_controller.domain.value_objects import SpsControllerName
from app.modules.sps_controller.infrastructure.sqlalchemy_models import SpsControllerOrm
from app.shared.ids import ControlCabinetId, SpsControllerId, SpsControllerSystemTypeId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class SqlAlchemySpsControllerAdapter:
    _session: AsyncSession

    async def get_by_id(self, controller_id: SpsControllerId) -> SpsController | None:
        stmt = select(SpsControllerOrm).where(SpsControllerOrm.id == controller_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_cabinet_and_name(
        self, cabinet_id: ControlCabinetId, name: SpsControllerName
    ) -> SpsController | None:
        stmt = select(SpsControllerOrm).where(
            SpsControllerOrm.cabinet_id == cabinet_id, SpsControllerOrm.name == name.value
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def create(self, controller: SpsController) -> SpsController:
        orm = SpsControllerOrm(
            id=controller.id,
            cabinet_id=controller.cabinet_id,
            system_type_id=controller.system_type_id,
            name=controller.name,
            description=controller.description,
            created_at=controller.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return controller

    async def update(self, controller: SpsController) -> SpsController:
        stmt = select(SpsControllerOrm).where(SpsControllerOrm.id == controller.id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        orm.name = controller.name
        orm.description = controller.description
        orm.system_type_id = controller.system_type_id
        await self._session.flush()
        return controller

    async def delete(self, controller_id: SpsControllerId) -> None:
        stmt = delete(SpsControllerOrm).where(SpsControllerOrm.id == controller_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(
        self, cabinet_id: ControlCabinetId, params: PageParams
    ) -> tuple[list[SpsController], int]:
        # Count
        count_stmt = (
            select(func.count())
            .select_from(SpsControllerOrm)
            .where(SpsControllerOrm.cabinet_id == cabinet_id)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Items
        stmt = (
            select(SpsControllerOrm)
            .where(SpsControllerOrm.cabinet_id == cabinet_id)
            .order_by(SpsControllerOrm.created_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    def _to_domain(self, orm: SpsControllerOrm) -> SpsController:
        return SpsController(
            id=SpsControllerId(orm.id),
            cabinet_id=ControlCabinetId(orm.cabinet_id),
            system_type_id=SpsControllerSystemTypeId(orm.system_type_id),
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
        )
