from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import FieldDeviceId, SpsControllerId


@dataclass(frozen=True, slots=True)
class CreateFieldDeviceCommand:
    controller_id: SpsControllerId
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateFieldDeviceCommand:
    controller_id: SpsControllerId
    device_id: FieldDeviceId
    name: str | None = None
    description: str | None = None
