from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.building.domain.models import Building
from app.modules.building.infrastructure.in_memory_adapter import InMemoryBuildingAdapter
from app.modules.control_cabinet.application.commands import (
    CreateControlCabinetCommand,
    UpdateControlCabinetCommand,
)
from app.modules.control_cabinet.application.queries import (
    GetControlCabinetQuery,
)
from app.modules.control_cabinet.application.use_cases import ControlCabinetModule
from app.modules.control_cabinet.domain.errors import (
    BuildingDoesNotExistError,
    ControlCabinetNameConflictError,
    ControlCabinetNotFoundError,
)
from app.modules.control_cabinet.infrastructure.in_memory_adapter import (
    InMemoryControlCabinetAdapter,
)
from app.shared.clock import FixedClock
from app.shared.ids import BuildingId, FacilityId, new_id
from app.shared.result import Err, Ok


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, tzinfo=UTC))


@pytest.fixture
def building_repo() -> InMemoryBuildingAdapter:
    return InMemoryBuildingAdapter()


@pytest.fixture
def cabinet_repo() -> InMemoryControlCabinetAdapter:
    return InMemoryControlCabinetAdapter()


@pytest.fixture
def module(
    cabinet_repo: InMemoryControlCabinetAdapter,
    building_repo: InMemoryBuildingAdapter,
    clock: FixedClock,
) -> ControlCabinetModule:
    return ControlCabinetModule(
        cabinet_repository=cabinet_repo, building_repository=building_repo, clock=clock
    )


@pytest.mark.asyncio
async def test_create_cabinet_success(
    module: ControlCabinetModule, building_repo: InMemoryBuildingAdapter, clock: FixedClock
) -> None:
    bid = new_id(BuildingId)
    await building_repo.create(
        Building(
            id=bid,
            facility_id=new_id(FacilityId),
            name="B1",
            description=None,
            created_at=clock.now(),
        )
    )

    result = await module.create_cabinet(
        CreateControlCabinetCommand(building_id=bid, name=" Cabinet 1 ", description="Test")
    )

    assert isinstance(result, Ok)
    cabinet = result.unwrap()
    assert cabinet.name == "Cabinet 1"
    assert cabinet.building_id == bid
    assert cabinet.created_at == clock.now()


@pytest.mark.asyncio
async def test_create_cabinet_building_missing(module: ControlCabinetModule) -> None:
    bid = new_id(BuildingId)
    result = await module.create_cabinet(CreateControlCabinetCommand(building_id=bid, name="C1"))

    assert isinstance(result, Err)
    assert isinstance(result.error, BuildingDoesNotExistError)


@pytest.mark.asyncio
async def test_create_cabinet_duplicate_name_in_building(
    module: ControlCabinetModule, building_repo: InMemoryBuildingAdapter, clock: FixedClock
) -> None:
    bid = new_id(BuildingId)
    await building_repo.create(
        Building(
            id=bid,
            facility_id=new_id(FacilityId),
            name="B1",
            description=None,
            created_at=clock.now(),
        )
    )

    await module.create_cabinet(CreateControlCabinetCommand(building_id=bid, name="C1"))
    result = await module.create_cabinet(CreateControlCabinetCommand(building_id=bid, name="C1"))

    assert isinstance(result, Err)
    assert isinstance(result.error, ControlCabinetNameConflictError)


@pytest.mark.asyncio
async def test_get_cabinet_success(
    module: ControlCabinetModule, building_repo: InMemoryBuildingAdapter, clock: FixedClock
) -> None:
    bid = new_id(BuildingId)
    await building_repo.create(
        Building(
            id=bid,
            facility_id=new_id(FacilityId),
            name="B1",
            description=None,
            created_at=clock.now(),
        )
    )

    created = (
        await module.create_cabinet(CreateControlCabinetCommand(building_id=bid, name="C1"))
    ).unwrap()

    result = await module.get_cabinet(
        GetControlCabinetQuery(building_id=bid, cabinet_id=created.id)
    )
    assert isinstance(result, Ok)
    assert result.unwrap().id == created.id


@pytest.mark.asyncio
async def test_get_cabinet_wrong_building(
    module: ControlCabinetModule, building_repo: InMemoryBuildingAdapter, clock: FixedClock
) -> None:
    bid1 = new_id(BuildingId)
    bid2 = new_id(BuildingId)
    await building_repo.create(
        Building(
            id=bid1,
            facility_id=new_id(FacilityId),
            name="B1",
            description=None,
            created_at=clock.now(),
        )
    )

    created = (
        await module.create_cabinet(CreateControlCabinetCommand(building_id=bid1, name="C1"))
    ).unwrap()

    result = await module.get_cabinet(
        GetControlCabinetQuery(building_id=bid2, cabinet_id=created.id)
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, ControlCabinetNotFoundError)


@pytest.mark.asyncio
async def test_update_cabinet_success(
    module: ControlCabinetModule, building_repo: InMemoryBuildingAdapter, clock: FixedClock
) -> None:
    bid = new_id(BuildingId)
    await building_repo.create(
        Building(
            id=bid,
            facility_id=new_id(FacilityId),
            name="B1",
            description=None,
            created_at=clock.now(),
        )
    )

    created = (
        await module.create_cabinet(CreateControlCabinetCommand(building_id=bid, name="C1"))
    ).unwrap()

    result = await module.update_cabinet(
        UpdateControlCabinetCommand(building_id=bid, cabinet_id=created.id, name="C2")
    )
    assert isinstance(result, Ok)
    assert result.unwrap().name == "C2"


@pytest.mark.asyncio
async def test_delete_cabinet_success(
    module: ControlCabinetModule, building_repo: InMemoryBuildingAdapter, clock: FixedClock
) -> None:
    bid = new_id(BuildingId)
    await building_repo.create(
        Building(
            id=bid,
            facility_id=new_id(FacilityId),
            name="B1",
            description=None,
            created_at=clock.now(),
        )
    )

    created = (
        await module.create_cabinet(CreateControlCabinetCommand(building_id=bid, name="C1"))
    ).unwrap()

    result = await module.delete_cabinet(building_id=bid, cabinet_id=created.id)
    assert isinstance(result, Ok)

    get_result = await module.get_cabinet(
        GetControlCabinetQuery(building_id=bid, cabinet_id=created.id)
    )
    assert isinstance(get_result, Err)
