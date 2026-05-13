"""Integration tests for SqlAlchemyBacnetObjectAdapter against a real PostgreSQL database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.bacnet_object.application.commands import (
    CreateBacnetObjectCommand,
    UpdateBacnetObjectCommand,
)
from app.modules.bacnet_object.application.queries import (
    GetBacnetObjectQuery,
    ListBacnetObjectsQuery,
)
from app.modules.bacnet_object.application.use_cases import BacnetObjectModule
from app.modules.bacnet_object.domain.errors import (
    BacnetObjectInstanceConflictError,
    BacnetObjectNameConflictError,
    BacnetObjectNotFoundError,
)
from app.modules.bacnet_object.domain.value_objects import BacnetObjectType
from app.modules.bacnet_object.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyBacnetObjectAdapter,
)
from app.modules.building.application.commands import CreateBuildingCommand
from app.modules.building.application.use_cases import BuildingModule
from app.modules.building.infrastructure.sqlalchemy_adapter import SqlAlchemyBuildingAdapter
from app.modules.control_cabinet.application.commands import CreateControlCabinetCommand
from app.modules.control_cabinet.application.use_cases import ControlCabinetModule
from app.modules.control_cabinet.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyControlCabinetAdapter,
)
from app.modules.facility.application.commands import CreateFacilityCommand
from app.modules.facility.application.use_cases import FacilityModule
from app.modules.facility.infrastructure.sqlalchemy_adapter import SqlAlchemyFacilityAdapter
from app.modules.field_device.application.commands import CreateFieldDeviceCommand
from app.modules.field_device.application.use_cases import FieldDeviceModule
from app.modules.field_device.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyFieldDeviceAdapter,
)
from app.modules.sps_controller.application.commands import CreateSpsControllerCommand
from app.modules.sps_controller.application.use_cases import SpsControllerModule
from app.modules.sps_controller.infrastructure.sqlalchemy_adapter import (
    SqlAlchemySpsControllerAdapter,
)
from app.modules.sps_controller_system_type.application.commands import (
    CreateSpsControllerSystemTypeCommand,
)
from app.modules.sps_controller_system_type.application.use_cases import (
    SpsControllerSystemTypeModule,
)
from app.modules.sps_controller_system_type.infrastructure.sqlalchemy_adapter import (
    SqlAlchemySpsControllerSystemTypeAdapter,
)
from app.shared.clock import FixedClock
from app.shared.ids import BacnetObjectId, FieldDeviceId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


async def _create_device(session: AsyncSession, suffix: str = "BO") -> FieldDeviceId:
    """Build the full physical hierarchy up to FieldDevice."""
    fac = (
        await FacilityModule(
            repository=SqlAlchemyFacilityAdapter(session), clock=FixedClock(_FIXED)
        ).create_facility(CreateFacilityCommand(name=f"Fac BO {suffix}"))
    ).unwrap()

    bld = (
        await BuildingModule(
            building_repository=SqlAlchemyBuildingAdapter(session),
            facility_repository=SqlAlchemyFacilityAdapter(session),
            clock=FixedClock(_FIXED),
        ).create_building(CreateBuildingCommand(facility_id=fac.id, name=f"Bld BO {suffix}"))
    ).unwrap()

    cab = (
        await ControlCabinetModule(
            cabinet_repository=SqlAlchemyControlCabinetAdapter(session),
            building_repository=SqlAlchemyBuildingAdapter(session),
            clock=FixedClock(_FIXED),
        ).create_cabinet(
            CreateControlCabinetCommand(building_id=bld.id, name=f"Cab BO {suffix}")
        )
    ).unwrap()

    st = (
        await SpsControllerSystemTypeModule(
            repository=SqlAlchemySpsControllerSystemTypeAdapter(session),
            clock=FixedClock(_FIXED),
        ).create_system_type(
            CreateSpsControllerSystemTypeCommand(name=f"Type BO {suffix}")
        )
    ).unwrap()

    ctrl = (
        await SpsControllerModule(
            controller_repository=SqlAlchemySpsControllerAdapter(session),
            cabinet_repository=SqlAlchemyControlCabinetAdapter(session),
            system_type_repository=SqlAlchemySpsControllerSystemTypeAdapter(session),
            clock=FixedClock(_FIXED),
        ).create_controller(
            CreateSpsControllerCommand(
                cabinet_id=cab.id, system_type_id=st.id, name=f"Ctrl BO {suffix}"
            )
        )
    ).unwrap()

    device = (
        await FieldDeviceModule(
            device_repository=SqlAlchemyFieldDeviceAdapter(session),
            controller_repository=SqlAlchemySpsControllerAdapter(session),
            clock=FixedClock(_FIXED),
        ).create_device(
            CreateFieldDeviceCommand(
                controller_id=ctrl.id, name=f"Dev BO {suffix}"
            )
        )
    ).unwrap()

    return device.id


def _make_module(session: AsyncSession) -> BacnetObjectModule:
    return BacnetObjectModule(
        object_repository=SqlAlchemyBacnetObjectAdapter(session),
        device_repository=SqlAlchemyFieldDeviceAdapter(session),
        clock=FixedClock(_FIXED),
    )


@pytest.mark.asyncio
async def test_create_and_get_bacnet_object(session: AsyncSession) -> None:
    device_id = await _create_device(session, "Create")
    module = _make_module(session)

    result = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device_id,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=1,
            name="Temp Sensor 1",
            description="Zone temperature",
        )
    )
    assert isinstance(result, Ok)
    obj = result.value

    fetched = await module.get_object(
        GetBacnetObjectQuery(device_id=device_id, object_id=obj.id)
    )
    assert isinstance(fetched, Ok)
    assert fetched.value.name == "Temp Sensor 1"
    assert fetched.value.object_type == BacnetObjectType.ANALOG_INPUT
    assert fetched.value.object_instance == 1
    assert fetched.value.device_id == device_id


@pytest.mark.asyncio
async def test_get_bacnet_object_not_found(session: AsyncSession) -> None:
    device_id = await _create_device(session, "NF")
    module = _make_module(session)

    result = await module.get_object(
        GetBacnetObjectQuery(device_id=device_id, object_id=new_id(BacnetObjectId))
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, BacnetObjectNotFoundError)


@pytest.mark.asyncio
async def test_duplicate_instance_raises_conflict(session: AsyncSession) -> None:
    device_id = await _create_device(session, "DupInst")
    module = _make_module(session)

    first = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device_id,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=10,
            name="Sensor A",
        )
    )
    assert isinstance(first, Ok)

    second = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device_id,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=10,
            name="Sensor B",
        )
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, BacnetObjectInstanceConflictError)


@pytest.mark.asyncio
async def test_duplicate_name_raises_conflict(session: AsyncSession) -> None:
    device_id = await _create_device(session, "DupName")
    module = _make_module(session)

    first = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device_id,
            object_type=BacnetObjectType.BINARY_INPUT,
            object_instance=1,
            name="Dup BACnet Name",
        )
    )
    assert isinstance(first, Ok)

    second = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device_id,
            object_type=BacnetObjectType.BINARY_INPUT,
            object_instance=2,
            name=" Dup BACnet Name ",
        )
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, BacnetObjectNameConflictError)


@pytest.mark.asyncio
async def test_update_bacnet_object(session: AsyncSession) -> None:
    device_id = await _create_device(session, "Upd")
    module = _make_module(session)

    created = (
        await module.create_object(
            CreateBacnetObjectCommand(
                device_id=device_id,
                object_type=BacnetObjectType.ANALOG_VALUE,
                object_instance=5,
                name="Before BO",
                description="Old",
            )
        )
    ).unwrap()

    updated = (
        await module.update_object(
            UpdateBacnetObjectCommand(
                device_id=device_id,
                object_id=created.id,
                name="After BO",
                description="New",
            )
        )
    ).unwrap()

    assert updated.name == "After BO"
    assert updated.description == "New"


@pytest.mark.asyncio
async def test_delete_bacnet_object(session: AsyncSession) -> None:
    device_id = await _create_device(session, "Del")
    module = _make_module(session)

    created = (
        await module.create_object(
            CreateBacnetObjectCommand(
                device_id=device_id,
                object_type=BacnetObjectType.BINARY_OUTPUT,
                object_instance=3,
                name="To Delete BO",
            )
        )
    ).unwrap()

    delete_result = await module.delete_object(
        device_id=device_id, object_id=created.id
    )
    assert isinstance(delete_result, Ok)

    get_result = await module.get_object(
        GetBacnetObjectQuery(device_id=device_id, object_id=created.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, BacnetObjectNotFoundError)


@pytest.mark.asyncio
async def test_list_bacnet_objects_scoped_to_device(session: AsyncSession) -> None:
    d1 = await _create_device(session, "List1")
    d2 = await _create_device(session, "List2")
    module = _make_module(session)

    for i in range(3):
        await module.create_object(
            CreateBacnetObjectCommand(
                device_id=d1,
                object_type=BacnetObjectType.ANALOG_INPUT,
                object_instance=i,
                name=f"D1 BO {i}",
            )
        )
    await module.create_object(
        CreateBacnetObjectCommand(
            device_id=d2,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=0,
            name="D2 Only BO",
        )
    )

    page = await module.list_objects(
        ListBacnetObjectsQuery(device_id=d1, page=PageParams(page=1, size=10))
    )
    assert page.total == 3
    assert all(o.device_id == d1 for o in page.items)
