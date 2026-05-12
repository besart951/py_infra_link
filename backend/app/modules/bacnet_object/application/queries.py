from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import BacnetObjectId, FieldDeviceId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class GetBacnetObjectQuery:
    device_id: FieldDeviceId
    object_id: BacnetObjectId


@dataclass(frozen=True, slots=True)
class ListBacnetObjectsQuery:
    device_id: FieldDeviceId
    page: PageParams
