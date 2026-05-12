from __future__ import annotations

from typing import Protocol

from app.modules.bacnet_object.domain.models import BacnetObject
from app.modules.bacnet_object.domain.value_objects import BacnetObjectName, BacnetObjectType
from app.shared.ids import BacnetObjectId, FieldDeviceId
from app.shared.pagination import PageParams


class BacnetObjectRepository(Protocol):
    async def get_by_id(self, object_id: BacnetObjectId) -> BacnetObject | None: ...

    async def get_by_device_type_instance(
        self, device_id: FieldDeviceId, object_type: BacnetObjectType, object_instance: int
    ) -> BacnetObject | None: ...

    async def get_by_device_and_name(
        self, device_id: FieldDeviceId, name: BacnetObjectName
    ) -> BacnetObject | None: ...

    async def create(self, obj: BacnetObject) -> BacnetObject: ...

    async def update(self, obj: BacnetObject) -> BacnetObject: ...

    async def delete(self, object_id: BacnetObjectId) -> None: ...

    async def list_page(
        self, device_id: FieldDeviceId, params: PageParams
    ) -> tuple[list[BacnetObject], int]: ...
