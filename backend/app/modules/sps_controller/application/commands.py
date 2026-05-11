from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import ControlCabinetId, SpsControllerId, SpsControllerSystemTypeId


@dataclass(frozen=True, slots=True)
class CreateSpsControllerCommand:
    cabinet_id: ControlCabinetId
    system_type_id: SpsControllerSystemTypeId
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateSpsControllerCommand:
    cabinet_id: ControlCabinetId
    controller_id: SpsControllerId
    system_type_id: SpsControllerSystemTypeId | None = None
    name: str | None = None
    description: str | None = None
