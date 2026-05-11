from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.ids import FacilityId


@dataclass(frozen=True, slots=True)
class Facility:
    id: FacilityId
    name: str
    description: str | None
    created_at: datetime
