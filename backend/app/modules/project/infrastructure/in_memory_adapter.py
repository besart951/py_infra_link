from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.project.domain.models import Project
from app.modules.project.domain.value_objects import ProjectName
from app.shared.ids import ProjectId, UserId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class InMemoryProjectAdapter:
    _projects: dict[ProjectId, Project] = field(default_factory=dict)

    async def get_by_id(self, project_id: ProjectId) -> Project | None:
        return self._projects.get(project_id)

    async def get_by_owner_and_name(
        self, owner_id: UserId, name: ProjectName
    ) -> Project | None:
        for project in self._projects.values():
            if project.owner_id == owner_id and project.name == name.value:
                return project
        return None

    async def create(self, project: Project) -> Project:
        self._projects[project.id] = project
        return project

    async def update(self, project: Project) -> Project:
        self._projects[project.id] = project
        return project

    async def delete(self, project_id: ProjectId) -> None:
        self._projects.pop(project_id, None)

    async def list_page(
        self, owner_id: UserId, params: PageParams
    ) -> tuple[list[Project], int]:
        all_items = sorted(
            [p for p in self._projects.values() if p.owner_id == owner_id],
            key=lambda p: p.created_at,
            reverse=True,
        )
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total
