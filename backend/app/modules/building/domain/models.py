from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.ids import BuildingId, FacilityId


@dataclass(frozen=True, slots=True)
class Building:
    id: BuildingId
    facility_id: FacilityId
    name: str
    description: str | None
    created_at: datetime
