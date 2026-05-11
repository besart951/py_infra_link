from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import BuildingId, ControlCabinetId


@dataclass(frozen=True, slots=True)
class CreateControlCabinetCommand:
    building_id: BuildingId
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateControlCabinetCommand:
    building_id: BuildingId
    cabinet_id: ControlCabinetId
    name: str | None = None
    description: str | None = None
