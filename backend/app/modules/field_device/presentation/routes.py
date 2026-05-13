from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.field_device.application.commands import (
    CreateFieldDeviceCommand,
    UpdateFieldDeviceCommand,
)
from app.modules.field_device.application.queries import (
    GetFieldDeviceQuery,
    ListFieldDevicesQuery,
)
from app.modules.field_device.application.use_cases import FieldDeviceModule
from app.modules.field_device.infrastructure.sqlalchemy_adapter import SqlAlchemyFieldDeviceAdapter
from app.modules.field_device.presentation.error_mapping import map_field_device_error
from app.modules.field_device.presentation.schemas import (
    FieldDeviceCreate,
    FieldDeviceRead,
    FieldDeviceUpdate,
)
from app.modules.sps_controller.infrastructure.sqlalchemy_adapter import (
    SqlAlchemySpsControllerAdapter,
)
from app.shared.clock import SystemClock
from app.shared.ids import FieldDeviceId, SpsControllerId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(
    prefix=(
        "/facilities/{facility_id}/buildings/{building_id}"
        "/control-cabinets/{cabinet_id}/sps-controllers/{controller_id}/field-devices"
    ),
    tags=["field-devices"],
)


def _make_module(session: AsyncSession) -> FieldDeviceModule:
    return FieldDeviceModule(
        device_repository=SqlAlchemyFieldDeviceAdapter(session),
        controller_repository=SqlAlchemySpsControllerAdapter(session),
        clock=SystemClock(),
    )


@router.post("", response_model=FieldDeviceRead, status_code=status.HTTP_201_CREATED)
async def create_device(
    controller_id: UUID,
    request: FieldDeviceCreate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> FieldDeviceRead:
    module = _make_module(session)
    result = await module.create_device(
        CreateFieldDeviceCommand(
            controller_id=SpsControllerId(controller_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return FieldDeviceRead.model_validate(result.value)

    raise map_field_device_error(result.error)


@router.get("/{device_id}", response_model=FieldDeviceRead)
async def get_device(
    controller_id: UUID,
    device_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> FieldDeviceRead:
    module = _make_module(session)
    result = await module.get_device(
        GetFieldDeviceQuery(
            controller_id=SpsControllerId(controller_id),
            device_id=FieldDeviceId(device_id),
        )
    )

    if isinstance(result, Ok):
        return FieldDeviceRead.model_validate(result.value)

    raise map_field_device_error(result.error)


@router.get("", response_model=Page[FieldDeviceRead])
async def list_devices(
    controller_id: UUID,
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Page[FieldDeviceRead]:
    module = _make_module(session)
    result = await module.list_devices(
        ListFieldDevicesQuery(
            controller_id=SpsControllerId(controller_id), page=PageParams(page=page, size=size)
        )
    )

    return Page[FieldDeviceRead](
        items=[FieldDeviceRead.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.patch("/{device_id}", response_model=FieldDeviceRead)
async def update_device(
    controller_id: UUID,
    device_id: UUID,
    request: FieldDeviceUpdate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> FieldDeviceRead:
    module = _make_module(session)
    result = await module.update_device(
        UpdateFieldDeviceCommand(
            controller_id=SpsControllerId(controller_id),
            device_id=FieldDeviceId(device_id),
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return FieldDeviceRead.model_validate(result.value)

    raise map_field_device_error(result.error)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    controller_id: UUID,
    device_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Response:
    module = _make_module(session)
    result = await module.delete_device(
        controller_id=SpsControllerId(controller_id),
        device_id=FieldDeviceId(device_id),
    )

    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise map_field_device_error(result.error)
