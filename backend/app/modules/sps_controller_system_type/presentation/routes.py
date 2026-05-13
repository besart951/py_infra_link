from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.sps_controller_system_type.application.commands import (
    CreateSpsControllerSystemTypeCommand,
    UpdateSpsControllerSystemTypeCommand,
)
from app.modules.sps_controller_system_type.application.queries import (
    GetSpsControllerSystemTypeQuery,
    ListSpsControllerSystemTypesQuery,
)
from app.modules.sps_controller_system_type.application.use_cases import (
    SpsControllerSystemTypeModule,
)
from app.modules.sps_controller_system_type.infrastructure.sqlalchemy_adapter import (
    SqlAlchemySpsControllerSystemTypeAdapter,
)
from app.modules.sps_controller_system_type.presentation.error_mapping import map_system_type_error
from app.modules.sps_controller_system_type.presentation.schemas import (
    SpsControllerSystemTypeCreate,
    SpsControllerSystemTypeRead,
    SpsControllerSystemTypeUpdate,
)
from app.shared.clock import SystemClock
from app.shared.ids import SpsControllerSystemTypeId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(prefix="/sps-controller-system-types", tags=["sps-controller-system-types"])


def _make_module(session: AsyncSession) -> SpsControllerSystemTypeModule:
    return SpsControllerSystemTypeModule(
        repository=SqlAlchemySpsControllerSystemTypeAdapter(session), clock=SystemClock()
    )


@router.post("", response_model=SpsControllerSystemTypeRead, status_code=status.HTTP_201_CREATED)
async def create_system_type(
    request: SpsControllerSystemTypeCreate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> SpsControllerSystemTypeRead:
    module = _make_module(session)
    result = await module.create_system_type(
        CreateSpsControllerSystemTypeCommand(name=request.name, description=request.description)
    )

    if isinstance(result, Ok):
        return SpsControllerSystemTypeRead.model_validate(result.value)

    raise map_system_type_error(result.error)


@router.get("/{system_type_id}", response_model=SpsControllerSystemTypeRead)
async def get_system_type(
    system_type_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> SpsControllerSystemTypeRead:
    module = _make_module(session)
    result = await module.get_system_type(
        GetSpsControllerSystemTypeQuery(system_type_id=SpsControllerSystemTypeId(system_type_id))
    )

    if isinstance(result, Ok):
        return SpsControllerSystemTypeRead.model_validate(result.value)

    raise map_system_type_error(result.error)


@router.get("", response_model=Page[SpsControllerSystemTypeRead])
async def list_system_types(
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Page[SpsControllerSystemTypeRead]:
    module = _make_module(session)
    result = await module.list_system_types(
        ListSpsControllerSystemTypesQuery(page=PageParams(page=page, size=size))
    )

    return Page[SpsControllerSystemTypeRead](
        items=[SpsControllerSystemTypeRead.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.patch("/{system_type_id}", response_model=SpsControllerSystemTypeRead)
async def update_system_type(
    system_type_id: UUID,
    request: SpsControllerSystemTypeUpdate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> SpsControllerSystemTypeRead:
    module = _make_module(session)
    result = await module.update_system_type(
        UpdateSpsControllerSystemTypeCommand(
            system_type_id=SpsControllerSystemTypeId(system_type_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return SpsControllerSystemTypeRead.model_validate(result.value)

    raise map_system_type_error(result.error)


@router.delete("/{system_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_type(
    system_type_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Response:
    module = _make_module(session)
    result = await module.delete_system_type(
        system_type_id=SpsControllerSystemTypeId(system_type_id)
    )

    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise map_system_type_error(result.error)
