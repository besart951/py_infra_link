from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.building.infrastructure.sqlalchemy_adapter import SqlAlchemyBuildingAdapter
from app.modules.control_cabinet.application.commands import (
    CreateControlCabinetCommand,
    UpdateControlCabinetCommand,
)
from app.modules.control_cabinet.application.queries import (
    GetControlCabinetQuery,
    ListControlCabinetsQuery,
)
from app.modules.control_cabinet.application.use_cases import ControlCabinetModule
from app.modules.control_cabinet.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyControlCabinetAdapter,
)
from app.modules.control_cabinet.presentation.error_mapping import map_cabinet_error
from app.modules.control_cabinet.presentation.schemas import (
    ControlCabinetCreate,
    ControlCabinetRead,
    ControlCabinetUpdate,
)
from app.shared.clock import SystemClock
from app.shared.ids import BuildingId, ControlCabinetId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(
    prefix="/facilities/{facility_id}/buildings/{building_id}/control-cabinets",
    tags=["control-cabinets"],
)


def _make_module(session: AsyncSession) -> ControlCabinetModule:
    return ControlCabinetModule(
        cabinet_repository=SqlAlchemyControlCabinetAdapter(session),
        building_repository=SqlAlchemyBuildingAdapter(session),
        clock=SystemClock(),
    )


@router.post("", response_model=ControlCabinetRead, status_code=status.HTTP_201_CREATED)
async def create_cabinet(
    building_id: UUID,
    request: ControlCabinetCreate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> ControlCabinetRead:
    module = _make_module(session)
    result = await module.create_cabinet(
        CreateControlCabinetCommand(
            building_id=BuildingId(building_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return ControlCabinetRead.model_validate(result.value)

    raise map_cabinet_error(result.error)


@router.get("/{cabinet_id}", response_model=ControlCabinetRead)
async def get_cabinet(
    building_id: UUID,
    cabinet_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> ControlCabinetRead:
    module = _make_module(session)
    result = await module.get_cabinet(
        GetControlCabinetQuery(
            building_id=BuildingId(building_id), cabinet_id=ControlCabinetId(cabinet_id)
        )
    )

    if isinstance(result, Ok):
        return ControlCabinetRead.model_validate(result.value)

    raise map_cabinet_error(result.error)


@router.get("", response_model=Page[ControlCabinetRead])
async def list_cabinets(
    building_id: UUID,
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Page[ControlCabinetRead]:
    module = _make_module(session)
    result = await module.list_cabinets(
        ListControlCabinetsQuery(
            building_id=BuildingId(building_id), page=PageParams(page=page, size=size)
        )
    )

    return Page[ControlCabinetRead](
        items=[ControlCabinetRead.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.patch("/{cabinet_id}", response_model=ControlCabinetRead)
async def update_cabinet(
    building_id: UUID,
    cabinet_id: UUID,
    request: ControlCabinetUpdate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> ControlCabinetRead:
    module = _make_module(session)
    result = await module.update_cabinet(
        UpdateControlCabinetCommand(
            building_id=BuildingId(building_id),
            cabinet_id=ControlCabinetId(cabinet_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return ControlCabinetRead.model_validate(result.value)

    raise map_cabinet_error(result.error)


@router.delete("/{cabinet_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cabinet(
    building_id: UUID,
    cabinet_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Response:
    module = _make_module(session)
    result = await module.delete_cabinet(
        building_id=BuildingId(building_id), cabinet_id=ControlCabinetId(cabinet_id)
    )

    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise map_cabinet_error(result.error)
