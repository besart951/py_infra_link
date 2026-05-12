from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bacnet_object.domain.models import BacnetObject
from app.modules.bacnet_object.domain.value_objects import BacnetObjectName, BacnetObjectType
from app.modules.bacnet_object.infrastructure.sqlalchemy_models import BacnetObjectOrm
from app.shared.ids import BacnetObjectId, FieldDeviceId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class SqlAlchemyBacnetObjectAdapter:
    _session: AsyncSession

    async def get_by_id(self, object_id: BacnetObjectId) -> BacnetObject | None:
        stmt = select(BacnetObjectOrm).where(BacnetObjectOrm.id == object_id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_device_type_instance(
        self, device_id: FieldDeviceId, object_type: BacnetObjectType, object_instance: int
    ) -> BacnetObject | None:
        stmt = select(BacnetObjectOrm).where(
            BacnetObjectOrm.device_id == device_id,
            BacnetObjectOrm.object_type == object_type.value,
            BacnetObjectOrm.object_instance == object_instance,
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def get_by_device_and_name(
        self, device_id: FieldDeviceId, name: BacnetObjectName
    ) -> BacnetObject | None:
        stmt = select(BacnetObjectOrm).where(
            BacnetObjectOrm.device_id == device_id,
            BacnetObjectOrm.name == name.value,
        )
        result = await self._session.execute(stmt)
        orm = result.scalar_one_or_none()
        return self._to_domain(orm) if orm else None

    async def create(self, obj: BacnetObject) -> BacnetObject:
        orm = BacnetObjectOrm(
            id=obj.id,
            device_id=obj.device_id,
            object_type=obj.object_type.value,
            object_instance=obj.object_instance,
            name=obj.name,
            description=obj.description,
            created_at=obj.created_at,
        )
        self._session.add(orm)
        await self._session.flush()
        return obj

    async def update(self, obj: BacnetObject) -> BacnetObject:
        stmt = select(BacnetObjectOrm).where(BacnetObjectOrm.id == obj.id)
        result = await self._session.execute(stmt)
        orm = result.scalar_one()
        orm.object_type = obj.object_type.value
        orm.object_instance = obj.object_instance
        orm.name = obj.name
        orm.description = obj.description
        await self._session.flush()
        return obj

    async def delete(self, object_id: BacnetObjectId) -> None:
        stmt = delete(BacnetObjectOrm).where(BacnetObjectOrm.id == object_id)
        await self._session.execute(stmt)
        await self._session.flush()

    async def list_page(
        self, device_id: FieldDeviceId, params: PageParams
    ) -> tuple[list[BacnetObject], int]:
        count_stmt = (
            select(func.count())
            .select_from(BacnetObjectOrm)
            .where(BacnetObjectOrm.device_id == device_id)
        )
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(BacnetObjectOrm)
            .where(BacnetObjectOrm.device_id == device_id)
            .order_by(BacnetObjectOrm.created_at.desc())
            .offset(params.offset)
            .limit(params.size)
        )
        result = await self._session.execute(stmt)
        orms = result.scalars().all()
        return [self._to_domain(orm) for orm in orms], total

    def _to_domain(self, orm: BacnetObjectOrm) -> BacnetObject:
        return BacnetObject(
            id=BacnetObjectId(orm.id),
            device_id=FieldDeviceId(orm.device_id),
            object_type=BacnetObjectType(orm.object_type),
            object_instance=orm.object_instance,
            name=orm.name,
            description=orm.description,
            created_at=orm.created_at,
        )
