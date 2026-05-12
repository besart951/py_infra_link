from __future__ import annotations

from typing import Protocol

from app.modules.field_device.domain.models import FieldDevice
from app.modules.field_device.domain.value_objects import FieldDeviceName
from app.shared.ids import FieldDeviceId, SpsControllerId
from app.shared.pagination import PageParams


class FieldDeviceRepository(Protocol):
    async def get_by_id(self, device_id: FieldDeviceId) -> FieldDevice | None: ...

    async def get_by_controller_and_name(
        self, controller_id: SpsControllerId, name: FieldDeviceName
    ) -> FieldDevice | None: ...

    async def create(self, device: FieldDevice) -> FieldDevice: ...

    async def update(self, device: FieldDevice) -> FieldDevice: ...

    async def delete(self, device_id: FieldDeviceId) -> None: ...

    async def list_page(
        self, controller_id: SpsControllerId, params: PageParams
    ) -> tuple[list[FieldDevice], int]: ...
