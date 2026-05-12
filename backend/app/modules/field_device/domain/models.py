from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.ids import FieldDeviceId, SpsControllerId


@dataclass(frozen=True, slots=True)
class FieldDevice:
    id: FieldDeviceId
    controller_id: SpsControllerId
    name: str
    description: str | None
    created_at: datetime
