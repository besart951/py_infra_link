from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import ProjectId, UserId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class GetProjectQuery:
    owner_id: UserId
    project_id: ProjectId


@dataclass(frozen=True, slots=True)
class ListProjectsQuery:
    owner_id: UserId
    page: PageParams
