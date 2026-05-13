"""Integration tests for SqlAlchemyControlCabinetAdapter against a real PostgreSQL database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.building.application.commands import CreateBuildingCommand
from app.modules.building.application.use_cases import BuildingModule
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
from app.modules.control_cabinet.domain.errors import (
    ControlCabinetNameConflictError,
    ControlCabinetNotFoundError,
)
from app.modules.control_cabinet.infrastructure.sqlalchemy_adapter import (
    SqlAlchemyControlCabinetAdapter,
)
from app.modules.facility.application.commands import CreateFacilityCommand
from app.modules.facility.application.use_cases import FacilityModule
from app.modules.facility.infrastructure.sqlalchemy_adapter import SqlAlchemyFacilityAdapter
from app.shared.clock import FixedClock
from app.shared.ids import BuildingId, ControlCabinetId, FacilityId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


async def _create_building(
    session: AsyncSession, fac_suffix: str = "CC"
) -> tuple[FacilityId, BuildingId]:
    fac_module = FacilityModule(
        repository=SqlAlchemyFacilityAdapter(session), clock=FixedClock(_FIXED)
    )
    facility = (
        await fac_module.create_facility(
            CreateFacilityCommand(name=f"Facility For Cabinet {fac_suffix}")
        )
    ).unwrap()

    bld_module = BuildingModule(
        building_repository=SqlAlchemyBuildingAdapter(session),
        facility_repository=SqlAlchemyFacilityAdapter(session),
        clock=FixedClock(_FIXED),
    )
    building = (
        await bld_module.create_building(
            CreateBuildingCommand(
                facility_id=facility.id, name=f"Building For Cabinet {fac_suffix}"
            )
        )
    ).unwrap()

    return facility.id, building.id


def _make_module(session: AsyncSession) -> ControlCabinetModule:
    return ControlCabinetModule(
        cabinet_repository=SqlAlchemyControlCabinetAdapter(session),
        building_repository=SqlAlchemyBuildingAdapter(session),
        clock=FixedClock(_FIXED),
    )


@pytest.mark.asyncio
async def test_create_and_get_control_cabinet(session: AsyncSession) -> None:
    _, building_id = await _create_building(session, "Create")
    module = _make_module(session)

    result = await module.create_cabinet(
        CreateControlCabinetCommand(
            building_id=building_id, name="Cabinet 1", description="Main cabinet"
        )
    )
    assert isinstance(result, Ok)
    cabinet = result.value

    fetched = await module.get_cabinet(
        GetControlCabinetQuery(building_id=building_id, cabinet_id=cabinet.id)
    )
    assert isinstance(fetched, Ok)
    assert fetched.value.name == "Cabinet 1"
    assert fetched.value.building_id == building_id


@pytest.mark.asyncio
async def test_get_control_cabinet_not_found(session: AsyncSession) -> None:
    _, building_id = await _create_building(session, "NF")
    module = _make_module(session)

    result = await module.get_cabinet(
        GetControlCabinetQuery(building_id=building_id, cabinet_id=new_id(ControlCabinetId))
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, ControlCabinetNotFoundError)


@pytest.mark.asyncio
async def test_duplicate_cabinet_name_in_same_building_raises_conflict(
    session: AsyncSession,
) -> None:
    _, building_id = await _create_building(session, "Dup")
    module = _make_module(session)

    first = await module.create_cabinet(
        CreateControlCabinetCommand(building_id=building_id, name="Dup Cabinet")
    )
    assert isinstance(first, Ok)

    second = await module.create_cabinet(
        CreateControlCabinetCommand(building_id=building_id, name=" Dup Cabinet ")
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, ControlCabinetNameConflictError)


@pytest.mark.asyncio
async def test_update_control_cabinet(session: AsyncSession) -> None:
    _, building_id = await _create_building(session, "Upd")
    module = _make_module(session)

    created = (
        await module.create_cabinet(
            CreateControlCabinetCommand(
                building_id=building_id, name="Before Cabinet", description="Old"
            )
        )
    ).unwrap()

    updated = (
        await module.update_cabinet(
            UpdateControlCabinetCommand(
                building_id=building_id,
                cabinet_id=created.id,
                name="After Cabinet",
                description="New",
            )
        )
    ).unwrap()

    assert updated.name == "After Cabinet"
    assert updated.description == "New"


@pytest.mark.asyncio
async def test_delete_control_cabinet(session: AsyncSession) -> None:
    _, building_id = await _create_building(session, "Del")
    module = _make_module(session)

    created = (
        await module.create_cabinet(
            CreateControlCabinetCommand(building_id=building_id, name="To Delete Cabinet")
        )
    ).unwrap()

    delete_result = await module.delete_cabinet(
        building_id=building_id, cabinet_id=created.id
    )
    assert isinstance(delete_result, Ok)

    get_result = await module.get_cabinet(
        GetControlCabinetQuery(building_id=building_id, cabinet_id=created.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, ControlCabinetNotFoundError)


@pytest.mark.asyncio
async def test_list_cabinets_scoped_to_building(session: AsyncSession) -> None:
    _, b1 = await _create_building(session, "List1")
    _, b2 = await _create_building(session, "List2")
    module = _make_module(session)

    for i in range(3):
        await module.create_cabinet(
            CreateControlCabinetCommand(building_id=b1, name=f"B1 Cabinet {i}")
        )
    await module.create_cabinet(
        CreateControlCabinetCommand(building_id=b2, name="B2 Only Cabinet")
    )

    page = await module.list_cabinets(
        ListControlCabinetsQuery(building_id=b1, page=PageParams(page=1, size=10))
    )
    assert page.total == 3
    assert all(c.building_id == b1 for c in page.items)
