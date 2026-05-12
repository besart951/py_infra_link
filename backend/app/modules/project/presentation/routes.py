from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.project.application.commands import CreateProjectCommand, UpdateProjectCommand
from app.modules.project.application.queries import GetProjectQuery, ListProjectsQuery
from app.modules.project.application.use_cases import ProjectModule
from app.modules.project.infrastructure.sqlalchemy_adapter import SqlAlchemyProjectAdapter
from app.modules.project.presentation.error_mapping import map_project_error
from app.modules.project.presentation.schemas import ProjectCreate, ProjectRead, ProjectUpdate
from app.modules.user.infrastructure.sqlalchemy_adapter import SqlAlchemyUserAdapter
from app.shared.clock import SystemClock
from app.shared.ids import ProjectId, UserId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(
    prefix="/users/{owner_id}/projects",
    tags=["projects"],
)


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    owner_id: UUID,
    request: ProjectCreate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> ProjectRead:
    module = ProjectModule(
        project_repository=SqlAlchemyProjectAdapter(session),
        user_repository=SqlAlchemyUserAdapter(session),
        clock=SystemClock(),
    )
    result = await module.create_project(
        CreateProjectCommand(
            owner_id=UserId(owner_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return ProjectRead.model_validate(result.value)

    raise map_project_error(result.error)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    owner_id: UUID,
    project_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> ProjectRead:
    module = ProjectModule(
        project_repository=SqlAlchemyProjectAdapter(session),
        user_repository=SqlAlchemyUserAdapter(session),
        clock=SystemClock(),
    )
    result = await module.get_project(
        GetProjectQuery(
            owner_id=UserId(owner_id),
            project_id=ProjectId(project_id),
        )
    )

    if isinstance(result, Ok):
        return ProjectRead.model_validate(result.value)

    raise map_project_error(result.error)


@router.get("", response_model=Page[ProjectRead])
async def list_projects(
    owner_id: UUID,
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Page[ProjectRead]:
    module = ProjectModule(
        project_repository=SqlAlchemyProjectAdapter(session),
        user_repository=SqlAlchemyUserAdapter(session),
        clock=SystemClock(),
    )
    result = await module.list_projects(
        ListProjectsQuery(
            owner_id=UserId(owner_id), page=PageParams(page=page, size=size)
        )
    )

    return Page[ProjectRead](
        items=[ProjectRead.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    owner_id: UUID,
    project_id: UUID,
    request: ProjectUpdate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> ProjectRead:
    module = ProjectModule(
        project_repository=SqlAlchemyProjectAdapter(session),
        user_repository=SqlAlchemyUserAdapter(session),
        clock=SystemClock(),
    )
    result = await module.update_project(
        UpdateProjectCommand(
            owner_id=UserId(owner_id),
            project_id=ProjectId(project_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return ProjectRead.model_validate(result.value)

    raise map_project_error(result.error)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    owner_id: UUID,
    project_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Response:
    module = ProjectModule(
        project_repository=SqlAlchemyProjectAdapter(session),
        user_repository=SqlAlchemyUserAdapter(session),
        clock=SystemClock(),
    )
    result = await module.delete_project(
        owner_id=UserId(owner_id),
        project_id=ProjectId(project_id),
    )

    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise map_project_error(result.error)
