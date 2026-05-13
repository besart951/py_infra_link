from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.field_device.domain.models import FieldDevice
from app.modules.field_device.domain.value_objects import FieldDeviceName
from app.shared.ids import FieldDeviceId, SpsControllerId
from app.shared.pagination import PageParams


def _device_store() -> dict[FieldDeviceId, FieldDevice]:
    return {}


@dataclass(frozen=True, slots=True)
class InMemoryFieldDeviceAdapter:
    _devices: dict[FieldDeviceId, FieldDevice] = field(default_factory=_device_store)

    async def get_by_id(self, device_id: FieldDeviceId) -> FieldDevice | None:
        return self._devices.get(device_id)

    async def get_by_controller_and_name(
        self, controller_id: SpsControllerId, name: FieldDeviceName
    ) -> FieldDevice | None:
        for device in self._devices.values():
            if device.controller_id == controller_id and device.name == name.value:
                return device
        return None

    async def create(self, device: FieldDevice) -> FieldDevice:
        self._devices[device.id] = device
        return device

    async def update(self, device: FieldDevice) -> FieldDevice:
        self._devices[device.id] = device
        return device

    async def delete(self, device_id: FieldDeviceId) -> None:
        self._devices.pop(device_id, None)

    async def list_page(
        self, controller_id: SpsControllerId, params: PageParams
    ) -> tuple[list[FieldDevice], int]:
        all_items = sorted(
            [d for d in self._devices.values() if d.controller_id == controller_id],
            key=lambda d: d.created_at,
            reverse=True,
        )
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total
