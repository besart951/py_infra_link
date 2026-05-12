from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.modules.bacnet_object.domain.value_objects import BacnetObjectType
from app.shared.ids import BacnetObjectId, FieldDeviceId


@dataclass(frozen=True, slots=True)
class BacnetObject:
    id: BacnetObjectId
    device_id: FieldDeviceId
    object_type: BacnetObjectType
    object_instance: int
    name: str
    description: str | None
    created_at: datetime
