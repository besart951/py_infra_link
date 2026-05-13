"""Integration tests for SqlAlchemySpsControllerAdapter against a real PostgreSQL database."""

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
from app.modules.sps_controller.application.commands import (
    CreateSpsControllerCommand,
    UpdateSpsControllerCommand,
)
from app.modules.sps_controller.application.queries import (
    GetSpsControllerQuery,
    ListSpsControllersQuery,
)
from app.modules.sps_controller.application.use_cases import SpsControllerModule
from app.modules.sps_controller.domain.errors import (
    SpsControllerNameConflictError,
    SpsControllerNotFoundError,
)
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
from app.shared.ids import ControlCabinetId, SpsControllerId, SpsControllerSystemTypeId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


async def _create_cabinet(
    session: AsyncSession, suffix: str = "Ctrl"
) -> tuple[ControlCabinetId, SpsControllerSystemTypeId]:
    """Create a full physical hierarchy up to ControlCabinet + a SystemType."""
    fac_module = FacilityModule(
        repository=SqlAlchemyFacilityAdapter(session), clock=FixedClock(_FIXED)
    )
    facility = (
        await fac_module.create_facility(
            CreateFacilityCommand(name=f"Facility SpsCtrl {suffix}")
        )
    ).unwrap()

    bld_module = BuildingModule(
        building_repository=SqlAlchemyBuildingAdapter(session),
        facility_repository=SqlAlchemyFacilityAdapter(session),
        clock=FixedClock(_FIXED),
    )
    building = (
        await bld_module.create_building(
            CreateBuildingCommand(facility_id=facility.id, name=f"Building SpsCtrl {suffix}")
        )
    ).unwrap()

    cab_module = ControlCabinetModule(
        cabinet_repository=SqlAlchemyControlCabinetAdapter(session),
        building_repository=SqlAlchemyBuildingAdapter(session),
        clock=FixedClock(_FIXED),
    )
    cabinet = (
        await cab_module.create_cabinet(
            CreateControlCabinetCommand(
                building_id=building.id, name=f"Cabinet SpsCtrl {suffix}"
            )
        )
    ).unwrap()

    st_module = SpsControllerSystemTypeModule(
        repository=SqlAlchemySpsControllerSystemTypeAdapter(session),
        clock=FixedClock(_FIXED),
    )
    system_type = (
        await st_module.create_system_type(
            CreateSpsControllerSystemTypeCommand(name=f"Type SpsCtrl {suffix}")
        )
    ).unwrap()

    return cabinet.id, system_type.id


def _make_module(session: AsyncSession) -> SpsControllerModule:
    return SpsControllerModule(
        controller_repository=SqlAlchemySpsControllerAdapter(session),
        cabinet_repository=SqlAlchemyControlCabinetAdapter(session),
        system_type_repository=SqlAlchemySpsControllerSystemTypeAdapter(session),
        clock=FixedClock(_FIXED),
    )


@pytest.mark.asyncio
async def test_create_and_get_sps_controller(session: AsyncSession) -> None:
    cabinet_id, system_type_id = await _create_cabinet(session, "Create")
    module = _make_module(session)

    result = await module.create_controller(
        CreateSpsControllerCommand(
            cabinet_id=cabinet_id,
            system_type_id=system_type_id,
            name="Controller 1",
            description="Primary controller",
        )
    )
    assert isinstance(result, Ok)
    controller = result.value

    fetched = await module.get_controller(
        GetSpsControllerQuery(cabinet_id=cabinet_id, controller_id=controller.id)
    )
    assert isinstance(fetched, Ok)
    assert fetched.value.name == "Controller 1"
    assert fetched.value.cabinet_id == cabinet_id
    assert fetched.value.system_type_id == system_type_id


@pytest.mark.asyncio
async def test_get_sps_controller_not_found(session: AsyncSession) -> None:
    cabinet_id, _ = await _create_cabinet(session, "NF")
    module = _make_module(session)

    result = await module.get_controller(
        GetSpsControllerQuery(cabinet_id=cabinet_id, controller_id=new_id(SpsControllerId))
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, SpsControllerNotFoundError)


@pytest.mark.asyncio
async def test_duplicate_controller_name_in_same_cabinet_raises_conflict(
    session: AsyncSession,
) -> None:
    cabinet_id, system_type_id = await _create_cabinet(session, "Dup")
    module = _make_module(session)

    first = await module.create_controller(
        CreateSpsControllerCommand(
            cabinet_id=cabinet_id, system_type_id=system_type_id, name="Dup Ctrl"
        )
    )
    assert isinstance(first, Ok)

    second = await module.create_controller(
        CreateSpsControllerCommand(
            cabinet_id=cabinet_id, system_type_id=system_type_id, name=" Dup Ctrl "
        )
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, SpsControllerNameConflictError)


@pytest.mark.asyncio
async def test_update_sps_controller(session: AsyncSession) -> None:
    cabinet_id, system_type_id = await _create_cabinet(session, "Upd")
    module = _make_module(session)

    created = (
        await module.create_controller(
            CreateSpsControllerCommand(
                cabinet_id=cabinet_id,
                system_type_id=system_type_id,
                name="Before Ctrl",
                description="Old",
            )
        )
    ).unwrap()

    updated = (
        await module.update_controller(
            UpdateSpsControllerCommand(
                cabinet_id=cabinet_id,
                controller_id=created.id,
                name="After Ctrl",
                description="New",
            )
        )
    ).unwrap()

    assert updated.name == "After Ctrl"
    assert updated.description == "New"


@pytest.mark.asyncio
async def test_delete_sps_controller(session: AsyncSession) -> None:
    cabinet_id, system_type_id = await _create_cabinet(session, "Del")
    module = _make_module(session)

    created = (
        await module.create_controller(
            CreateSpsControllerCommand(
                cabinet_id=cabinet_id,
                system_type_id=system_type_id,
                name="To Delete Ctrl",
            )
        )
    ).unwrap()

    delete_result = await module.delete_controller(
        cabinet_id=cabinet_id, controller_id=created.id
    )
    assert isinstance(delete_result, Ok)

    get_result = await module.get_controller(
        GetSpsControllerQuery(cabinet_id=cabinet_id, controller_id=created.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, SpsControllerNotFoundError)


@pytest.mark.asyncio
async def test_list_controllers_scoped_to_cabinet(session: AsyncSession) -> None:
    c1, st1 = await _create_cabinet(session, "List1")
    c2, st2 = await _create_cabinet(session, "List2")
    module = _make_module(session)

    for i in range(3):
        await module.create_controller(
            CreateSpsControllerCommand(
                cabinet_id=c1, system_type_id=st1, name=f"C1 Ctrl {i}"
            )
        )
    await module.create_controller(
        CreateSpsControllerCommand(
            cabinet_id=c2, system_type_id=st2, name="C2 Only Ctrl"
        )
    )

    page = await module.list_controllers(
        ListSpsControllersQuery(cabinet_id=c1, page=PageParams(page=1, size=10))
    )
    assert page.total == 3
    assert all(c.cabinet_id == c1 for c in page.items)
