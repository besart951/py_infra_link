from __future__ import annotations

import uuid
from dataclasses import dataclass

from app.modules.live_update.domain.events import DomainEvent, DomainEventType
from app.modules.live_update.domain.interface import EventPublisher
from app.modules.project.application.commands import CreateProjectCommand, UpdateProjectCommand
from app.modules.project.application.queries import GetProjectQuery, ListProjectsQuery
from app.modules.project.domain.errors import (
    InvalidProjectNameError,
    ProjectNameConflictError,
    ProjectNotFoundError,
    UserDoesNotExistError,
)
from app.modules.project.domain.interface import ProjectRepository
from app.modules.project.domain.models import Project
from app.modules.project.domain.value_objects import ProjectName
from app.modules.user.domain.interface import UserRepository
from app.shared.clock import Clock
from app.shared.ids import ProjectId, UserId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class ProjectModule:
    project_repository: ProjectRepository
    user_repository: UserRepository
    clock: Clock
    event_publisher: EventPublisher

    async def create_project(
        self, command: CreateProjectCommand
    ) -> Result[
        Project,
        UserDoesNotExistError | ProjectNameConflictError | InvalidProjectNameError,
    ]:
        try:
            name = ProjectName.parse(command.name)
        except InvalidProjectNameError as exc:
            return Err(exc)

        user = await self.user_repository.get_by_id(command.owner_id)
        if user is None:
            return Err(
                UserDoesNotExistError(
                    f"User '{command.owner_id}' does not exist"
                )
            )

        existing = await self.project_repository.get_by_owner_and_name(
            command.owner_id, name
        )
        if existing is not None:
            return Err(
                ProjectNameConflictError(
                    f"Project with name '{name.value}' already exists for this user"
                )
            )

        project = Project(
            id=new_id(ProjectId),
            owner_id=command.owner_id,
            name=name.value,
            description=command.description,
            created_at=self.clock.now(),
        )
        created = await self.project_repository.create(project)
        await self.event_publisher.publish(
            DomainEvent(
                event_type=DomainEventType.PROJECT_CREATED,
                aggregate_id=uuid.UUID(str(created.id)),
                payload={
                    "project_id": str(created.id),
                    "owner_id": str(created.owner_id),
                    "name": created.name,
                },
                occurred_at=self.clock.now(),
            )
        )
        return Ok(created)

    async def get_project(
        self, query: GetProjectQuery
    ) -> Result[Project, ProjectNotFoundError]:
        project = await self.project_repository.get_by_id(query.project_id)
        if project is None or project.owner_id != query.owner_id:
            return Err(
                ProjectNotFoundError(f"Project '{query.project_id}' was not found")
            )
        return Ok(project)

    async def list_projects(self, query: ListProjectsQuery) -> Page[Project]:
        items, total = await self.project_repository.list_page(query.owner_id, query.page)
        return Page[Project](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def update_project(
        self, command: UpdateProjectCommand
    ) -> Result[
        Project,
        ProjectNotFoundError | ProjectNameConflictError | InvalidProjectNameError,
    ]:
        project = await self.project_repository.get_by_id(command.project_id)
        if project is None or project.owner_id != command.owner_id:
            return Err(
                ProjectNotFoundError(f"Project '{command.project_id}' was not found")
            )

        name_value = project.name
        if command.name is not None:
            try:
                name = ProjectName.parse(command.name)
                name_value = name.value
            except InvalidProjectNameError as exc:
                return Err(exc)

            if name_value != project.name:
                existing = await self.project_repository.get_by_owner_and_name(
                    command.owner_id, ProjectName(name_value)
                )
                if existing is not None:
                    return Err(
                        ProjectNameConflictError(
                            f"Project with name '{name_value}' already exists for this user"
                        )
                    )

        description = (
            command.description if command.description is not None else project.description
        )

        updated_project = Project(
            id=project.id,
            owner_id=project.owner_id,
            name=name_value,
            description=description,
            created_at=project.created_at,
        )
        updated = await self.project_repository.update(updated_project)
        await self.event_publisher.publish(
            DomainEvent(
                event_type=DomainEventType.PROJECT_UPDATED,
                aggregate_id=uuid.UUID(str(updated.id)),
                payload={
                    "project_id": str(updated.id),
                    "owner_id": str(updated.owner_id),
                    "name": updated.name,
                },
                occurred_at=self.clock.now(),
            )
        )
        return Ok(updated)

    async def delete_project(
        self, owner_id: UserId, project_id: ProjectId
    ) -> Result[None, ProjectNotFoundError]:
        project = await self.project_repository.get_by_id(project_id)
        if project is None or project.owner_id != owner_id:
            return Err(ProjectNotFoundError(f"Project '{project_id}' was not found"))

        await self.project_repository.delete(project_id)
        await self.event_publisher.publish(
            DomainEvent(
                event_type=DomainEventType.PROJECT_DELETED,
                aggregate_id=uuid.UUID(str(project_id)),
                payload={
                    "project_id": str(project_id),
                    "owner_id": str(owner_id),
                },
                occurred_at=self.clock.now(),
            )
        )
        return Ok(None)
