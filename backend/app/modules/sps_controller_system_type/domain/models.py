from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.ids import SpsControllerSystemTypeId


@dataclass(frozen=True, slots=True)
class SpsControllerSystemType:
    id: SpsControllerSystemTypeId
    name: str
    description: str | None
    created_at: datetime
