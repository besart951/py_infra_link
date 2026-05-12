from __future__ import annotations

from dataclasses import dataclass

from app.modules.bacnet_object.domain.value_objects import BacnetObjectType
from app.shared.ids import BacnetObjectId, FieldDeviceId


@dataclass(frozen=True, slots=True)
class CreateBacnetObjectCommand:
    device_id: FieldDeviceId
    object_type: BacnetObjectType
    object_instance: int
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateBacnetObjectCommand:
    device_id: FieldDeviceId
    object_id: BacnetObjectId
    object_type: BacnetObjectType | None = None
    object_instance: int | None = None
    name: str | None = None
    description: str | None = None
