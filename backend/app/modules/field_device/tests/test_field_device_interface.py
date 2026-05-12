from __future__ import annotations

from datetime import UTC, datetime

import pytest

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
    SpsControllerDoesNotExistError,
)
from app.modules.field_device.infrastructure.in_memory_adapter import InMemoryFieldDeviceAdapter
from app.modules.sps_controller.domain.models import SpsController
from app.modules.sps_controller.infrastructure.in_memory_adapter import (
    InMemorySpsControllerAdapter,
)
from app.shared.clock import FixedClock
from app.shared.ids import (
    ControlCabinetId,
    SpsControllerId,
    SpsControllerSystemTypeId,
    new_id,
)
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, tzinfo=UTC))


@pytest.fixture
def controller_repo() -> InMemorySpsControllerAdapter:
    return InMemorySpsControllerAdapter()


@pytest.fixture
def device_repo() -> InMemoryFieldDeviceAdapter:
    return InMemoryFieldDeviceAdapter()


@pytest.fixture
def module(
    device_repo: InMemoryFieldDeviceAdapter,
    controller_repo: InMemorySpsControllerAdapter,
    clock: FixedClock,
) -> FieldDeviceModule:
    return FieldDeviceModule(
        device_repository=device_repo,
        controller_repository=controller_repo,
        clock=clock,
    )


async def _seed_controller(
    controller_repo: InMemorySpsControllerAdapter, clock: FixedClock
) -> SpsController:
    cid = new_id(SpsControllerId)
    controller = SpsController(
        id=cid,
        cabinet_id=new_id(ControlCabinetId),
        system_type_id=new_id(SpsControllerSystemTypeId),
        name="Controller 1",
        description=None,
        created_at=clock.now(),
    )
    await controller_repo.create(controller)
    return controller


@pytest.mark.asyncio
async def test_create_device_success(
    module: FieldDeviceModule,
    controller_repo: InMemorySpsControllerAdapter,
    clock: FixedClock,
) -> None:
    controller = await _seed_controller(controller_repo, clock)

    result = await module.create_device(
        CreateFieldDeviceCommand(
            controller_id=controller.id,
            name=" Temp Sensor 1 ",
            description="Main floor temperature sensor",
        )
    )

    assert isinstance(result, Ok)
    device = result.unwrap()
    assert device.name == "Temp Sensor 1"
    assert device.controller_id == controller.id
    assert device.description == "Main floor temperature sensor"
    assert device.created_at == clock.now()


@pytest.mark.asyncio
async def test_create_device_controller_missing(
    module: FieldDeviceModule,
) -> None:
    result = await module.create_device(
        CreateFieldDeviceCommand(
            controller_id=new_id(SpsControllerId),
            name="Sensor 1",
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, SpsControllerDoesNotExistError)


@pytest.mark.asyncio
async def test_create_device_duplicate_name_under_controller(
    module: FieldDeviceModule,
    controller_repo: InMemorySpsControllerAdapter,
    clock: FixedClock,
) -> None:
    controller = await _seed_controller(controller_repo, clock)

    await module.create_device(
        CreateFieldDeviceCommand(controller_id=controller.id, name="Sensor 1")
    )
    result = await module.create_device(
        CreateFieldDeviceCommand(controller_id=controller.id, name="Sensor 1")
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, FieldDeviceNameConflictError)


@pytest.mark.asyncio
async def test_create_device_same_name_different_controllers(
    module: FieldDeviceModule,
    controller_repo: InMemorySpsControllerAdapter,
    clock: FixedClock,
) -> None:
    controller_a = await _seed_controller(controller_repo, clock)
    controller_b = await _seed_controller(controller_repo, clock)

    result_a = await module.create_device(
        CreateFieldDeviceCommand(controller_id=controller_a.id, name="Sensor 1")
    )
    result_b = await module.create_device(
        CreateFieldDeviceCommand(controller_id=controller_b.id, name="Sensor 1")
    )

    assert isinstance(result_a, Ok)
    assert isinstance(result_b, Ok)


@pytest.mark.asyncio
async def test_get_device_success(
    module: FieldDeviceModule,
    controller_repo: InMemorySpsControllerAdapter,
    clock: FixedClock,
) -> None:
    controller = await _seed_controller(controller_repo, clock)
    created = (
        await module.create_device(
            CreateFieldDeviceCommand(controller_id=controller.id, name="Sensor 1")
        )
    ).unwrap()

    result = await module.get_device(
        GetFieldDeviceQuery(controller_id=controller.id, device_id=created.id)
    )

    assert isinstance(result, Ok)
    assert result.unwrap().id == created.id


@pytest.mark.asyncio
async def test_get_device_not_found(
    module: FieldDeviceModule,
    controller_repo: InMemorySpsControllerAdapter,
    clock: FixedClock,
) -> None:
    controller = await _seed_controller(controller_repo, clock)
    from app.shared.ids import FieldDeviceId

    result = await module.get_device(
        GetFieldDeviceQuery(
            controller_id=controller.id,
            device_id=new_id(FieldDeviceId),
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, FieldDeviceNotFoundError)


@pytest.mark.asyncio
async def test_list_devices(
    module: FieldDeviceModule,
    controller_repo: InMemorySpsControllerAdapter,
    clock: FixedClock,
) -> None:
    controller = await _seed_controller(controller_repo, clock)

    await module.create_device(
        CreateFieldDeviceCommand(controller_id=controller.id, name="Sensor 1")
    )
    await module.create_device(
        CreateFieldDeviceCommand(controller_id=controller.id, name="Sensor 2")
    )

    page = await module.list_devices(
        ListFieldDevicesQuery(controller_id=controller.id, page=PageParams(page=1, size=10))
    )
    assert page.total == 2
    assert len(page.items) == 2


@pytest.mark.asyncio
async def test_update_device_success(
    module: FieldDeviceModule,
    controller_repo: InMemorySpsControllerAdapter,
    clock: FixedClock,
) -> None:
    controller = await _seed_controller(controller_repo, clock)
    created = (
        await module.create_device(
            CreateFieldDeviceCommand(
                controller_id=controller.id, name="Sensor 1", description="Old desc"
            )
        )
    ).unwrap()

    result = await module.update_device(
        UpdateFieldDeviceCommand(
            controller_id=controller.id,
            device_id=created.id,
            name="Sensor Renamed",
            description="New desc",
        )
    )

    assert isinstance(result, Ok)
    updated = result.unwrap()
    assert updated.name == "Sensor Renamed"
    assert updated.description == "New desc"


@pytest.mark.asyncio
async def test_delete_device_success(
    module: FieldDeviceModule,
    controller_repo: InMemorySpsControllerAdapter,
    clock: FixedClock,
) -> None:
    controller = await _seed_controller(controller_repo, clock)
    created = (
        await module.create_device(
            CreateFieldDeviceCommand(controller_id=controller.id, name="Sensor 1")
        )
    ).unwrap()

    result = await module.delete_device(
        controller_id=controller.id, device_id=created.id
    )
    assert isinstance(result, Ok)

    get_result = await module.get_device(
        GetFieldDeviceQuery(controller_id=controller.id, device_id=created.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, FieldDeviceNotFoundError)
