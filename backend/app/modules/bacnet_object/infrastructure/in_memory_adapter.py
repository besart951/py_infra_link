from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.bacnet_object.domain.models import BacnetObject
from app.modules.bacnet_object.domain.value_objects import BacnetObjectName, BacnetObjectType
from app.shared.ids import BacnetObjectId, FieldDeviceId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class InMemoryBacnetObjectAdapter:
    _objects: dict[BacnetObjectId, BacnetObject] = field(default_factory=dict)

    async def get_by_id(self, object_id: BacnetObjectId) -> BacnetObject | None:
        return self._objects.get(object_id)

    async def get_by_device_type_instance(
        self, device_id: FieldDeviceId, object_type: BacnetObjectType, object_instance: int
    ) -> BacnetObject | None:
        for obj in self._objects.values():
            if (
                obj.device_id == device_id
                and obj.object_type == object_type
                and obj.object_instance == object_instance
            ):
                return obj
        return None

    async def get_by_device_and_name(
        self, device_id: FieldDeviceId, name: BacnetObjectName
    ) -> BacnetObject | None:
        for obj in self._objects.values():
            if obj.device_id == device_id and obj.name == name.value:
                return obj
        return None

    async def create(self, obj: BacnetObject) -> BacnetObject:
        self._objects[obj.id] = obj
        return obj

    async def update(self, obj: BacnetObject) -> BacnetObject:
        self._objects[obj.id] = obj
        return obj

    async def delete(self, object_id: BacnetObjectId) -> None:
        self._objects.pop(object_id, None)

    async def list_page(
        self, device_id: FieldDeviceId, params: PageParams
    ) -> tuple[list[BacnetObject], int]:
        all_items = sorted(
            [o for o in self._objects.values() if o.device_id == device_id],
            key=lambda o: o.created_at,
            reverse=True,
        )
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total
