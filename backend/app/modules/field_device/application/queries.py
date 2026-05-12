from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import FieldDeviceId, SpsControllerId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class GetFieldDeviceQuery:
    controller_id: SpsControllerId
    device_id: FieldDeviceId


@dataclass(frozen=True, slots=True)
class ListFieldDevicesQuery:
    controller_id: SpsControllerId
    page: PageParams
