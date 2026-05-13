"""Integration tests for SqlAlchemyBuildingAdapter against a real PostgreSQL database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.building.application.commands import (
    CreateBuildingCommand,
    UpdateBuildingCommand,
)
from app.modules.building.application.queries import GetBuildingQuery, ListBuildingsQuery
from app.modules.building.application.use_cases import BuildingModule
from app.modules.building.domain.errors import (
    BuildingNameConflictError,
    BuildingNotFoundError,
)
from app.modules.building.infrastructure.sqlalchemy_adapter import SqlAlchemyBuildingAdapter
from app.modules.facility.application.commands import CreateFacilityCommand
from app.modules.facility.application.use_cases import FacilityModule
from app.modules.facility.infrastructure.sqlalchemy_adapter import SqlAlchemyFacilityAdapter
from app.shared.clock import FixedClock
from app.shared.ids import BuildingId, FacilityId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


async def _create_facility(session: AsyncSession, name: str = "Test Facility") -> FacilityId:
    module = FacilityModule(
        repository=SqlAlchemyFacilityAdapter(session), clock=FixedClock(_FIXED)
    )
    result = await module.create_facility(CreateFacilityCommand(name=name))
    assert isinstance(result, Ok)
    return result.value.id


def _make_module(session: AsyncSession) -> BuildingModule:
    return BuildingModule(
        building_repository=SqlAlchemyBuildingAdapter(session),
        facility_repository=SqlAlchemyFacilityAdapter(session),
        clock=FixedClock(_FIXED),
    )


@pytest.mark.asyncio
async def test_create_and_get_building(session: AsyncSession) -> None:
    facility_id = await _create_facility(session, "Facility For Building")
    module = _make_module(session)

    result = await module.create_building(
        CreateBuildingCommand(
            facility_id=facility_id, name="Block A", description="Main block"
        )
    )
    assert isinstance(result, Ok)
    building = result.value

    fetched = await module.get_building(
        GetBuildingQuery(facility_id=facility_id, building_id=building.id)
    )
    assert isinstance(fetched, Ok)
    assert fetched.value.name == "Block A"
    assert fetched.value.description == "Main block"
    assert fetched.value.facility_id == facility_id


@pytest.mark.asyncio
async def test_get_building_not_found(session: AsyncSession) -> None:
    facility_id = await _create_facility(session, "Facility NF Building")
    module = _make_module(session)

    result = await module.get_building(
        GetBuildingQuery(facility_id=facility_id, building_id=new_id(BuildingId))
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, BuildingNotFoundError)


@pytest.mark.asyncio
async def test_create_duplicate_building_name_in_same_facility_raises_conflict(
    session: AsyncSession,
) -> None:
    facility_id = await _create_facility(session, "Facility Dup Building")
    module = _make_module(session)

    first = await module.create_building(
        CreateBuildingCommand(facility_id=facility_id, name="Dup Block")
    )
    assert isinstance(first, Ok)

    second = await module.create_building(
        CreateBuildingCommand(facility_id=facility_id, name=" Dup Block ")
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, BuildingNameConflictError)


@pytest.mark.asyncio
async def test_same_building_name_allowed_in_different_facilities(
    session: AsyncSession,
) -> None:
    f1 = await _create_facility(session, "Facility A For Building")
    f2 = await _create_facility(session, "Facility B For Building")
    module = _make_module(session)

    r1 = await module.create_building(
        CreateBuildingCommand(facility_id=f1, name="Block X")
    )
    r2 = await module.create_building(
        CreateBuildingCommand(facility_id=f2, name="Block X")
    )
    assert isinstance(r1, Ok)
    assert isinstance(r2, Ok)


@pytest.mark.asyncio
async def test_update_building(session: AsyncSession) -> None:
    facility_id = await _create_facility(session, "Facility Upd Building")
    module = _make_module(session)

    created = (
        await module.create_building(
            CreateBuildingCommand(
                facility_id=facility_id, name="Before Building", description="Old"
            )
        )
    ).unwrap()

    updated = (
        await module.update_building(
            UpdateBuildingCommand(
                facility_id=facility_id,
                building_id=created.id,
                name="After Building",
                description="New",
            )
        )
    ).unwrap()

    assert updated.name == "After Building"
    assert updated.description == "New"


@pytest.mark.asyncio
async def test_delete_building(session: AsyncSession) -> None:
    facility_id = await _create_facility(session, "Facility Del Building")
    module = _make_module(session)

    created = (
        await module.create_building(
            CreateBuildingCommand(facility_id=facility_id, name="To Delete Building")
        )
    ).unwrap()

    delete_result = await module.delete_building(
        facility_id=facility_id, building_id=created.id
    )
    assert isinstance(delete_result, Ok)

    get_result = await module.get_building(
        GetBuildingQuery(facility_id=facility_id, building_id=created.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, BuildingNotFoundError)


@pytest.mark.asyncio
async def test_list_buildings_scoped_to_facility(session: AsyncSession) -> None:
    f1 = await _create_facility(session, "Facility List Bld 1")
    f2 = await _create_facility(session, "Facility List Bld 2")
    module = _make_module(session)

    for i in range(3):
        await module.create_building(
            CreateBuildingCommand(facility_id=f1, name=f"F1 Block {i}")
        )
    await module.create_building(
        CreateBuildingCommand(facility_id=f2, name="F2 Only Block")
    )

    page = await module.list_buildings(
        ListBuildingsQuery(facility_id=f1, page=PageParams(page=1, size=10))
    )
    assert page.total == 3
    assert all(b.facility_id == f1 for b in page.items)
