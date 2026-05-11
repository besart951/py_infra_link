from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.ids import BuildingId, ControlCabinetId


@dataclass(frozen=True, slots=True)
class ControlCabinet:
    id: ControlCabinetId
    building_id: BuildingId
    name: str
    description: str | None
    created_at: datetime
