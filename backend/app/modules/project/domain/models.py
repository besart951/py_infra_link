from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.shared.ids import ProjectId, UserId


@dataclass(frozen=True, slots=True)
class Project:
    id: ProjectId
    owner_id: UserId
    name: str
    description: str | None
    created_at: datetime
