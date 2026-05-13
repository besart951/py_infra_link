"""Integration tests for SqlAlchemyFieldDeviceAdapter against a real PostgreSQL database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.modules.field_device.application.commands import (
    CreateFieldDeviceCommand,
    UpdateFieldDeviceCommand,
)
from app.modules.field_device.application.queries import (
    GetFieldDeviceQuery,
    ListFieldDevicesQuery,
)
from app.modules.field_device.application.use_cases import FieldDeviceModule
from app.modules.field_device.domain.errors import (
    FieldDeviceNameConflictError,
    FieldDeviceNotFoundError,
)
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
from app.shared.ids import FieldDeviceId, SpsControllerId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


async def _create_controller(
    session: AsyncSession, suffix: str = "FD"
) -> SpsControllerId:
    """Create a full physical hierarchy up to SpsController."""
    fac = (
        await FacilityModule(
            repository=SqlAlchemyFacilityAdapter(session), clock=FixedClock(_FIXED)
        ).create_facility(CreateFacilityCommand(name=f"Fac FD {suffix}"))
    ).unwrap()

    bld = (
        await BuildingModule(
            building_repository=SqlAlchemyBuildingAdapter(session),
            facility_repository=SqlAlchemyFacilityAdapter(session),
            clock=FixedClock(_FIXED),
        ).create_building(
            CreateBuildingCommand(facility_id=fac.id, name=f"Bld FD {suffix}")
        )
    ).unwrap()

    cab = (
        await ControlCabinetModule(
            cabinet_repository=SqlAlchemyControlCabinetAdapter(session),
            building_repository=SqlAlchemyBuildingAdapter(session),
            clock=FixedClock(_FIXED),
        ).create_cabinet(
            CreateControlCabinetCommand(building_id=bld.id, name=f"Cab FD {suffix}")
        )
    ).unwrap()

    st = (
        await SpsControllerSystemTypeModule(
            repository=SqlAlchemySpsControllerSystemTypeAdapter(session),
            clock=FixedClock(_FIXED),
        ).create_system_type(
            CreateSpsControllerSystemTypeCommand(name=f"Type FD {suffix}")
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
                cabinet_id=cab.id, system_type_id=st.id, name=f"Ctrl FD {suffix}"
            )
        )
    ).unwrap()

    return ctrl.id


def _make_module(session: AsyncSession) -> FieldDeviceModule:
    return FieldDeviceModule(
        device_repository=SqlAlchemyFieldDeviceAdapter(session),
        controller_repository=SqlAlchemySpsControllerAdapter(session),
        clock=FixedClock(_FIXED),
    )


@pytest.mark.asyncio
async def test_create_and_get_field_device(session: AsyncSession) -> None:
    controller_id = await _create_controller(session, "Create")
    module = _make_module(session)

    result = await module.create_device(
        CreateFieldDeviceCommand(
            controller_id=controller_id, name="Device 1", description="Temp sensor"
        )
    )
    assert isinstance(result, Ok)
    device = result.value

    fetched = await module.get_device(
        GetFieldDeviceQuery(controller_id=controller_id, device_id=device.id)
    )
    assert isinstance(fetched, Ok)
    assert fetched.value.name == "Device 1"
    assert fetched.value.controller_id == controller_id


@pytest.mark.asyncio
async def test_get_field_device_not_found(session: AsyncSession) -> None:
    controller_id = await _create_controller(session, "NF")
    module = _make_module(session)

    result = await module.get_device(
        GetFieldDeviceQuery(controller_id=controller_id, device_id=new_id(FieldDeviceId))
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, FieldDeviceNotFoundError)


@pytest.mark.asyncio
async def test_duplicate_device_name_in_same_controller_raises_conflict(
    session: AsyncSession,
) -> None:
    controller_id = await _create_controller(session, "Dup")
    module = _make_module(session)

    first = await module.create_device(
        CreateFieldDeviceCommand(controller_id=controller_id, name="Dup Device")
    )
    assert isinstance(first, Ok)

    second = await module.create_device(
        CreateFieldDeviceCommand(controller_id=controller_id, name=" Dup Device ")
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, FieldDeviceNameConflictError)


@pytest.mark.asyncio
async def test_update_field_device(session: AsyncSession) -> None:
    controller_id = await _create_controller(session, "Upd")
    module = _make_module(session)

    created = (
        await module.create_device(
            CreateFieldDeviceCommand(
                controller_id=controller_id, name="Before Device", description="Old"
            )
        )
    ).unwrap()

    updated = (
        await module.update_device(
            UpdateFieldDeviceCommand(
                controller_id=controller_id,
                device_id=created.id,
                name="After Device",
                description="New",
            )
        )
    ).unwrap()

    assert updated.name == "After Device"
    assert updated.description == "New"


@pytest.mark.asyncio
async def test_delete_field_device(session: AsyncSession) -> None:
    controller_id = await _create_controller(session, "Del")
    module = _make_module(session)

    created = (
        await module.create_device(
            CreateFieldDeviceCommand(
                controller_id=controller_id, name="To Delete Device"
            )
        )
    ).unwrap()

    delete_result = await module.delete_device(
        controller_id=controller_id, device_id=created.id
    )
    assert isinstance(delete_result, Ok)

    get_result = await module.get_device(
        GetFieldDeviceQuery(controller_id=controller_id, device_id=created.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, FieldDeviceNotFoundError)


@pytest.mark.asyncio
async def test_list_devices_scoped_to_controller(session: AsyncSession) -> None:
    c1 = await _create_controller(session, "List1")
    c2 = await _create_controller(session, "List2")
    module = _make_module(session)

    for i in range(3):
        await module.create_device(
            CreateFieldDeviceCommand(controller_id=c1, name=f"C1 Device {i}")
        )
    await module.create_device(
        CreateFieldDeviceCommand(controller_id=c2, name="C2 Only Device")
    )

    page = await module.list_devices(
        ListFieldDevicesQuery(controller_id=c1, page=PageParams(page=1, size=10))
    )
    assert page.total == 3
    assert all(d.controller_id == c1 for d in page.items)
