from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.control_cabinet.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyControlCabinetAdapter,
)
from app.modules.sps_controller.application.commands import (
    CreateSpsControllerCommand,
    UpdateSpsControllerCommand,
)
from app.modules.sps_controller.application.queries import (
    GetSpsControllerQuery,
    ListSpsControllersQuery,
)
from app.modules.sps_controller.application.use_cases import SpsControllerModule
from app.modules.sps_controller.infrastructure.sqlalchemy_adapter import (
    SqlAlchemySpsControllerAdapter,
)
from app.modules.sps_controller.presentation.error_mapping import map_controller_error
from app.modules.sps_controller.presentation.schemas import (
    SpsControllerCreate,
    SpsControllerRead,
    SpsControllerUpdate,
)
from app.modules.sps_controller_system_type.infrastructure.sqlalchemy_adapter import (
    SqlAlchemySpsControllerSystemTypeAdapter,
)
from app.shared.clock import SystemClock
from app.shared.ids import ControlCabinetId, SpsControllerId, SpsControllerSystemTypeId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(
    prefix="/facilities/{facility_id}/buildings/{building_id}/control-cabinets/{cabinet_id}/sps-controllers",
    tags=["sps-controllers"],
)


def _make_module(session: AsyncSession) -> SpsControllerModule:
    return SpsControllerModule(
        controller_repository=SqlAlchemySpsControllerAdapter(session),
        cabinet_repository=SqlAlchemyControlCabinetAdapter(session),
        system_type_repository=SqlAlchemySpsControllerSystemTypeAdapter(session),
        clock=SystemClock(),
    )


@router.post("", response_model=SpsControllerRead, status_code=status.HTTP_201_CREATED)
async def create_controller(
    cabinet_id: UUID,
    request: SpsControllerCreate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> SpsControllerRead:
    module = _make_module(session)
    result = await module.create_controller(
        CreateSpsControllerCommand(
            cabinet_id=ControlCabinetId(cabinet_id),
            system_type_id=SpsControllerSystemTypeId(request.system_type_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return SpsControllerRead.model_validate(result.value)

    raise map_controller_error(result.error)


@router.get("/{controller_id}", response_model=SpsControllerRead)
async def get_controller(
    cabinet_id: UUID,
    controller_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> SpsControllerRead:
    module = _make_module(session)
    result = await module.get_controller(
        GetSpsControllerQuery(
            cabinet_id=ControlCabinetId(cabinet_id),
            controller_id=SpsControllerId(controller_id),
        )
    )

    if isinstance(result, Ok):
        return SpsControllerRead.model_validate(result.value)

    raise map_controller_error(result.error)


@router.get("", response_model=Page[SpsControllerRead])
async def list_controllers(
    cabinet_id: UUID,
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Page[SpsControllerRead]:
    module = _make_module(session)
    result = await module.list_controllers(
        ListSpsControllersQuery(
            cabinet_id=ControlCabinetId(cabinet_id), page=PageParams(page=page, size=size)
        )
    )

    return Page[SpsControllerRead](
        items=[SpsControllerRead.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.patch("/{controller_id}", response_model=SpsControllerRead)
async def update_controller(
    cabinet_id: UUID,
    controller_id: UUID,
    request: SpsControllerUpdate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> SpsControllerRead:
    module = _make_module(session)
    result = await module.update_controller(
        UpdateSpsControllerCommand(
            cabinet_id=ControlCabinetId(cabinet_id),
            controller_id=SpsControllerId(controller_id),
            system_type_id=SpsControllerSystemTypeId(request.system_type_id)
            if request.system_type_id
            else None,
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return SpsControllerRead.model_validate(result.value)

    raise map_controller_error(result.error)


@router.delete("/{controller_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_controller(
    cabinet_id: UUID,
    controller_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Response:
    module = _make_module(session)
    result = await module.delete_controller(
        cabinet_id=ControlCabinetId(cabinet_id),
        controller_id=SpsControllerId(controller_id),
    )

    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise map_controller_error(result.error)
