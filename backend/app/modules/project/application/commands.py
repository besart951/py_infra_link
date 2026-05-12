from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import ProjectId, UserId


@dataclass(frozen=True, slots=True)
class CreateProjectCommand:
    owner_id: UserId
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateProjectCommand:
    owner_id: UserId
    project_id: ProjectId
    name: str | None = None
    description: str | None = None
