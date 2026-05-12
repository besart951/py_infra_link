from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_session
from app.modules.bacnet_object.application.commands import (
    CreateBacnetObjectCommand,
    UpdateBacnetObjectCommand,
)
from app.modules.bacnet_object.application.queries import (
    GetBacnetObjectQuery,
    ListBacnetObjectsQuery,
)
from app.modules.bacnet_object.application.use_cases import BacnetObjectModule
from app.modules.bacnet_object.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyBacnetObjectAdapter,
)
from app.modules.bacnet_object.presentation.error_mapping import map_bacnet_object_error
from app.modules.bacnet_object.presentation.schemas import (
    BacnetObjectCreate,
    BacnetObjectRead,
    BacnetObjectUpdate,
)
from app.modules.field_device.infrastructure.sqlalchemy_adapter import SqlAlchemyFieldDeviceAdapter
from app.shared.clock import SystemClock
from app.shared.ids import BacnetObjectId, FieldDeviceId
from app.shared.pagination import Page, PageParams
from app.shared.result import Ok

router = APIRouter(
    prefix=(
        "/facilities/{facility_id}/buildings/{building_id}"
        "/control-cabinets/{cabinet_id}/sps-controllers/{controller_id}"
        "/field-devices/{device_id}/bacnet-objects"
    ),
    tags=["bacnet-objects"],
)


@router.post("", response_model=BacnetObjectRead, status_code=status.HTTP_201_CREATED)
async def create_object(
    device_id: UUID,
    request: BacnetObjectCreate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> BacnetObjectRead:
    module = BacnetObjectModule(
        object_repository=SqlAlchemyBacnetObjectAdapter(session),
        device_repository=SqlAlchemyFieldDeviceAdapter(session),
        clock=SystemClock(),
    )
    result = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=FieldDeviceId(device_id),
            object_type=request.object_type,
            object_instance=request.object_instance,
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return BacnetObjectRead.model_validate(result.value)

    raise map_bacnet_object_error(result.error)


@router.get("/{object_id}", response_model=BacnetObjectRead)
async def get_object(
    device_id: UUID,
    object_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> BacnetObjectRead:
    module = BacnetObjectModule(
        object_repository=SqlAlchemyBacnetObjectAdapter(session),
        device_repository=SqlAlchemyFieldDeviceAdapter(session),
        clock=SystemClock(),
    )
    result = await module.get_object(
        GetBacnetObjectQuery(
            device_id=FieldDeviceId(device_id),
            object_id=BacnetObjectId(object_id),
        )
    )

    if isinstance(result, Ok):
        return BacnetObjectRead.model_validate(result.value)

    raise map_bacnet_object_error(result.error)


@router.get("", response_model=Page[BacnetObjectRead])
async def list_objects(
    device_id: UUID,
    page: int = 1,
    size: int = 20,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Page[BacnetObjectRead]:
    module = BacnetObjectModule(
        object_repository=SqlAlchemyBacnetObjectAdapter(session),
        device_repository=SqlAlchemyFieldDeviceAdapter(session),
        clock=SystemClock(),
    )
    result = await module.list_objects(
        ListBacnetObjectsQuery(
            device_id=FieldDeviceId(device_id), page=PageParams(page=page, size=size)
        )
    )

    return Page[BacnetObjectRead](
        items=[BacnetObjectRead.model_validate(item) for item in result.items],
        total=result.total,
        page=result.page,
        size=result.size,
    )


@router.patch("/{object_id}", response_model=BacnetObjectRead)
async def update_object(
    device_id: UUID,
    object_id: UUID,
    request: BacnetObjectUpdate,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> BacnetObjectRead:
    module = BacnetObjectModule(
        object_repository=SqlAlchemyBacnetObjectAdapter(session),
        device_repository=SqlAlchemyFieldDeviceAdapter(session),
        clock=SystemClock(),
    )
    result = await module.update_object(
        UpdateBacnetObjectCommand(
            device_id=FieldDeviceId(device_id),
            object_id=BacnetObjectId(object_id),
            object_type=request.object_type,
            object_instance=request.object_instance,
            name=request.name,
            description=request.description,
        )
    )

    if isinstance(result, Ok):
        return BacnetObjectRead.model_validate(result.value)

    raise map_bacnet_object_error(result.error)


@router.delete("/{object_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_object(
    device_id: UUID,
    object_id: UUID,
    session: AsyncSession = Depends(get_session),  # noqa: B008
) -> Response:
    module = BacnetObjectModule(
        object_repository=SqlAlchemyBacnetObjectAdapter(session),
        device_repository=SqlAlchemyFieldDeviceAdapter(session),
        clock=SystemClock(),
    )
    result = await module.delete_object(
        device_id=FieldDeviceId(device_id),
        object_id=BacnetObjectId(object_id),
    )

    if isinstance(result, Ok):
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    raise map_bacnet_object_error(result.error)
