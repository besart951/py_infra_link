from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.ids import ControlCabinetId, SpsControllerId, SpsControllerSystemTypeId


@dataclass(frozen=True, slots=True)
class SpsController:
    id: SpsControllerId
    cabinet_id: ControlCabinetId
    system_type_id: SpsControllerSystemTypeId
    name: str
    description: str | None
    created_at: datetime
