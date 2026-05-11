from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.ids import UserId


@dataclass(frozen=True, slots=True)
class User:
    id: UserId
    email: str
    display_name: str
    created_at: datetime
