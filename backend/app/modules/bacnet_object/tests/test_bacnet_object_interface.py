from __future__ import annotations

from datetime import UTC, datetime

import pytest

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
    FieldDeviceDoesNotExistError,
    InvalidBacnetObjectInstanceError,
)
from app.modules.bacnet_object.domain.value_objects import BacnetObjectType
from app.modules.bacnet_object.infrastructure.in_memory_adapter import InMemoryBacnetObjectAdapter
from app.modules.field_device.domain.models import FieldDevice
from app.modules.field_device.infrastructure.in_memory_adapter import InMemoryFieldDeviceAdapter
from app.shared.clock import FixedClock
from app.shared.ids import (
    BacnetObjectId,
    FieldDeviceId,
    SpsControllerId,
    new_id,
)
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, tzinfo=UTC))


@pytest.fixture
def device_repo() -> InMemoryFieldDeviceAdapter:
    return InMemoryFieldDeviceAdapter()


@pytest.fixture
def object_repo() -> InMemoryBacnetObjectAdapter:
    return InMemoryBacnetObjectAdapter()


@pytest.fixture
def module(
    object_repo: InMemoryBacnetObjectAdapter,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> BacnetObjectModule:
    return BacnetObjectModule(
        object_repository=object_repo,
        device_repository=device_repo,
        clock=clock,
    )


async def _seed_device(
    device_repo: InMemoryFieldDeviceAdapter, clock: FixedClock
) -> FieldDevice:
    device = FieldDevice(
        id=new_id(FieldDeviceId),
        controller_id=new_id(SpsControllerId),
        name="Temp Sensor",
        description=None,
        created_at=clock.now(),
    )
    await device_repo.create(device)
    return device


@pytest.mark.asyncio
async def test_create_object_success(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device = await _seed_device(device_repo, clock)

    result = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device.id,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=1,
            name=" Room Temp ",
            description="Room temperature sensor",
        )
    )

    assert isinstance(result, Ok)
    obj = result.unwrap()
    assert obj.name == "Room Temp"
    assert obj.device_id == device.id
    assert obj.object_type == BacnetObjectType.ANALOG_INPUT
    assert obj.object_instance == 1
    assert obj.created_at == clock.now()


@pytest.mark.asyncio
async def test_create_object_device_missing(
    module: BacnetObjectModule,
) -> None:
    result = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=new_id(FieldDeviceId),
            object_type=BacnetObjectType.BINARY_INPUT,
            object_instance=0,
            name="Object 1",
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, FieldDeviceDoesNotExistError)


@pytest.mark.asyncio
async def test_create_object_duplicate_type_instance(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device = await _seed_device(device_repo, clock)

    await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device.id,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=1,
            name="Temp 1",
        )
    )
    result = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device.id,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=1,
            name="Temp 2",
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, BacnetObjectInstanceConflictError)


@pytest.mark.asyncio
async def test_create_object_duplicate_name(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device = await _seed_device(device_repo, clock)

    await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device.id,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=1,
            name="Room Temp",
        )
    )
    result = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device.id,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=2,
            name="Room Temp",
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, BacnetObjectNameConflictError)


@pytest.mark.asyncio
async def test_create_object_same_type_instance_different_devices(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device_a = await _seed_device(device_repo, clock)
    device_b = await _seed_device(device_repo, clock)

    result_a = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device_a.id,
            object_type=BacnetObjectType.BINARY_OUTPUT,
            object_instance=0,
            name="Switch A",
        )
    )
    result_b = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device_b.id,
            object_type=BacnetObjectType.BINARY_OUTPUT,
            object_instance=0,
            name="Switch B",
        )
    )

    assert isinstance(result_a, Ok)
    assert isinstance(result_b, Ok)


@pytest.mark.asyncio
async def test_create_object_invalid_negative_instance(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device = await _seed_device(device_repo, clock)

    result = await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device.id,
            object_type=BacnetObjectType.ANALOG_VALUE,
            object_instance=-1,
            name="Bad Object",
        )
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidBacnetObjectInstanceError)


@pytest.mark.asyncio
async def test_get_object_success(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device = await _seed_device(device_repo, clock)
    created = (
        await module.create_object(
            CreateBacnetObjectCommand(
                device_id=device.id,
                object_type=BacnetObjectType.ANALOG_INPUT,
                object_instance=0,
                name="Sensor",
            )
        )
    ).unwrap()

    result = await module.get_object(
        GetBacnetObjectQuery(device_id=device.id, object_id=created.id)
    )

    assert isinstance(result, Ok)
    assert result.unwrap().id == created.id


@pytest.mark.asyncio
async def test_get_object_not_found(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device = await _seed_device(device_repo, clock)

    result = await module.get_object(
        GetBacnetObjectQuery(device_id=device.id, object_id=new_id(BacnetObjectId))
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, BacnetObjectNotFoundError)


@pytest.mark.asyncio
async def test_list_objects(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device = await _seed_device(device_repo, clock)

    await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device.id,
            object_type=BacnetObjectType.ANALOG_INPUT,
            object_instance=0,
            name="Sensor 1",
        )
    )
    await module.create_object(
        CreateBacnetObjectCommand(
            device_id=device.id,
            object_type=BacnetObjectType.BINARY_INPUT,
            object_instance=0,
            name="Sensor 2",
        )
    )

    page = await module.list_objects(
        ListBacnetObjectsQuery(device_id=device.id, page=PageParams(page=1, size=10))
    )
    assert page.total == 2
    assert len(page.items) == 2


@pytest.mark.asyncio
async def test_update_object_success(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device = await _seed_device(device_repo, clock)
    created = (
        await module.create_object(
            CreateBacnetObjectCommand(
                device_id=device.id,
                object_type=BacnetObjectType.ANALOG_INPUT,
                object_instance=1,
                name="Old Name",
                description="Old desc",
            )
        )
    ).unwrap()

    result = await module.update_object(
        UpdateBacnetObjectCommand(
            device_id=device.id,
            object_id=created.id,
            name="New Name",
            description="New desc",
            object_instance=5,
        )
    )

    assert isinstance(result, Ok)
    updated = result.unwrap()
    assert updated.name == "New Name"
    assert updated.description == "New desc"
    assert updated.object_instance == 5


@pytest.mark.asyncio
async def test_delete_object_success(
    module: BacnetObjectModule,
    device_repo: InMemoryFieldDeviceAdapter,
    clock: FixedClock,
) -> None:
    device = await _seed_device(device_repo, clock)
    created = (
        await module.create_object(
            CreateBacnetObjectCommand(
                device_id=device.id,
                object_type=BacnetObjectType.BINARY_OUTPUT,
                object_instance=0,
                name="Switch",
            )
        )
    ).unwrap()

    result = await module.delete_object(device_id=device.id, object_id=created.id)
    assert isinstance(result, Ok)

    get_result = await module.get_object(
        GetBacnetObjectQuery(device_id=device.id, object_id=created.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, BacnetObjectNotFoundError)
