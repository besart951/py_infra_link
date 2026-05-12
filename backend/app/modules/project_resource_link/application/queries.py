from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import ProjectId, UserId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class ListLinksQuery:
    owner_id: UserId
    project_id: ProjectId
    page: PageParams
