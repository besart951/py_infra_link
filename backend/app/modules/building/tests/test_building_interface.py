from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.building.application.commands import (
    CreateBuildingCommand,
    UpdateBuildingCommand,
)
from app.modules.building.application.queries import (
    GetBuildingQuery,
)
from app.modules.building.application.use_cases import BuildingModule
from app.modules.building.domain.errors import (
    BuildingNameConflictError,
    BuildingNotFoundError,
    FacilityDoesNotExistError,
)
from app.modules.building.infrastructure.in_memory_adapter import InMemoryBuildingAdapter
from app.modules.facility.domain.models import Facility
from app.modules.facility.infrastructure.in_memory_adapter import InMemoryFacilityAdapter
from app.shared.clock import FixedClock
from app.shared.ids import FacilityId, new_id
from app.shared.result import Err, Ok


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, tzinfo=UTC))


@pytest.fixture
def facility_repo() -> InMemoryFacilityAdapter:
    return InMemoryFacilityAdapter()


@pytest.fixture
def building_repo() -> InMemoryBuildingAdapter:
    return InMemoryBuildingAdapter()


@pytest.fixture
def module(
    building_repo: InMemoryBuildingAdapter,
    facility_repo: InMemoryFacilityAdapter,
    clock: FixedClock,
) -> BuildingModule:
    return BuildingModule(
        building_repository=building_repo, facility_repository=facility_repo, clock=clock
    )


@pytest.mark.asyncio
async def test_create_building_success(
    module: BuildingModule, facility_repo: InMemoryFacilityAdapter, clock: FixedClock
) -> None:
    # Setup: Create a facility first
    fid = new_id(FacilityId)
    await facility_repo.create(
        Facility(id=fid, name="Facility 1", description=None, created_at=clock.now())
    )

    result = await module.create_building(
        CreateBuildingCommand(facility_id=fid, name=" Building A ", description="Test")
    )

    assert isinstance(result, Ok)
    building = result.unwrap()
    assert building.name == "Building A"
    assert building.facility_id == fid
    assert building.created_at == clock.now()


@pytest.mark.asyncio
async def test_create_building_facility_missing(module: BuildingModule) -> None:
    fid = new_id(FacilityId)
    result = await module.create_building(CreateBuildingCommand(facility_id=fid, name="A"))

    assert isinstance(result, Err)
    assert isinstance(result.error, FacilityDoesNotExistError)


@pytest.mark.asyncio
async def test_create_building_duplicate_name_in_facility(
    module: BuildingModule, facility_repo: InMemoryFacilityAdapter, clock: FixedClock
) -> None:
    fid = new_id(FacilityId)
    await facility_repo.create(
        Facility(id=fid, name="F1", description=None, created_at=clock.now())
    )

    await module.create_building(CreateBuildingCommand(facility_id=fid, name="A"))
    result = await module.create_building(CreateBuildingCommand(facility_id=fid, name="A"))

    assert isinstance(result, Err)
    assert isinstance(result.error, BuildingNameConflictError)


@pytest.mark.asyncio
async def test_get_building_success(
    module: BuildingModule, facility_repo: InMemoryFacilityAdapter, clock: FixedClock
) -> None:
    fid = new_id(FacilityId)
    await facility_repo.create(
        Facility(id=fid, name="F1", description=None, created_at=clock.now())
    )

    created = (
        await module.create_building(CreateBuildingCommand(facility_id=fid, name="A"))
    ).unwrap()

    result = await module.get_building(GetBuildingQuery(facility_id=fid, building_id=created.id))
    assert isinstance(result, Ok)
    assert result.unwrap().id == created.id


@pytest.mark.asyncio
async def test_get_building_wrong_facility(
    module: BuildingModule, facility_repo: InMemoryFacilityAdapter, clock: FixedClock
) -> None:
    fid1 = new_id(FacilityId)
    fid2 = new_id(FacilityId)
    await facility_repo.create(
        Facility(id=fid1, name="F1", description=None, created_at=clock.now())
    )

    created = (
        await module.create_building(CreateBuildingCommand(facility_id=fid1, name="A"))
    ).unwrap()

    result = await module.get_building(GetBuildingQuery(facility_id=fid2, building_id=created.id))
    assert isinstance(result, Err)
    assert isinstance(result.error, BuildingNotFoundError)


@pytest.mark.asyncio
async def test_update_building_success(
    module: BuildingModule, facility_repo: InMemoryFacilityAdapter, clock: FixedClock
) -> None:
    fid = new_id(FacilityId)
    await facility_repo.create(
        Facility(id=fid, name="F1", description=None, created_at=clock.now())
    )

    created = (
        await module.create_building(CreateBuildingCommand(facility_id=fid, name="A"))
    ).unwrap()

    result = await module.update_building(
        UpdateBuildingCommand(facility_id=fid, building_id=created.id, name="B")
    )
    assert isinstance(result, Ok)
    assert result.unwrap().name == "B"


@pytest.mark.asyncio
async def test_delete_building_success(
    module: BuildingModule, facility_repo: InMemoryFacilityAdapter, clock: FixedClock
) -> None:
    fid = new_id(FacilityId)
    await facility_repo.create(
        Facility(id=fid, name="F1", description=None, created_at=clock.now())
    )

    created = (
        await module.create_building(CreateBuildingCommand(facility_id=fid, name="A"))
    ).unwrap()

    result = await module.delete_building(facility_id=fid, building_id=created.id)
    assert isinstance(result, Ok)

    get_result = await module.get_building(
        GetBuildingQuery(facility_id=fid, building_id=created.id)
    )
    assert isinstance(get_result, Err)
