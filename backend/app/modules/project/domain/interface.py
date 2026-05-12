from __future__ import annotations

from typing import Protocol

from app.modules.project.domain.models import Project
from app.modules.project.domain.value_objects import ProjectName
from app.shared.ids import ProjectId, UserId
from app.shared.pagination import PageParams


class ProjectRepository(Protocol):
    async def get_by_id(self, project_id: ProjectId) -> Project | None: ...

    async def get_by_owner_and_name(
        self, owner_id: UserId, name: ProjectName
    ) -> Project | None: ...

    async def create(self, project: Project) -> Project: ...

    async def update(self, project: Project) -> Project: ...

    async def delete(self, project_id: ProjectId) -> None: ...

    async def list_page(
        self, owner_id: UserId, params: PageParams
    ) -> tuple[list[Project], int]: ...
