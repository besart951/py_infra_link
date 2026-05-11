from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.control_cabinet.domain.models import ControlCabinet
from app.modules.control_cabinet.infrastructure.in_memory_adapter import (
    InMemoryControlCabinetAdapter,
)
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
    ControlCabinetDoesNotExistError,
    SpsControllerNameConflictError,
    SpsControllerSystemTypeDoesNotExistError,
)
from app.modules.sps_controller.infrastructure.in_memory_adapter import (
    InMemorySpsControllerAdapter,
)
from app.modules.sps_controller_system_type.domain.models import SpsControllerSystemType
from app.modules.sps_controller_system_type.infrastructure.in_memory_adapter import (
    InMemorySpsControllerSystemTypeAdapter,
)
from app.shared.clock import FixedClock
from app.shared.ids import (
    BuildingId,
    ControlCabinetId,
    SpsControllerSystemTypeId,
    new_id,
)
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, tzinfo=UTC))


@pytest.fixture
def cabinet_repo() -> InMemoryControlCabinetAdapter:
    return InMemoryControlCabinetAdapter()


@pytest.fixture
def system_type_repo() -> InMemorySpsControllerSystemTypeAdapter:
    return InMemorySpsControllerSystemTypeAdapter()


@pytest.fixture
def controller_repo() -> InMemorySpsControllerAdapter:
    return InMemorySpsControllerAdapter()


@pytest.fixture
def module(
    controller_repo: InMemorySpsControllerAdapter,
    cabinet_repo: InMemoryControlCabinetAdapter,
    system_type_repo: InMemorySpsControllerSystemTypeAdapter,
    clock: FixedClock,
) -> SpsControllerModule:
    return SpsControllerModule(
        controller_repository=controller_repo,
        cabinet_repository=cabinet_repo,
        system_type_repository=system_type_repo,
        clock=clock,
    )


@pytest.mark.asyncio
async def test_create_controller_success(
    module: SpsControllerModule,
    cabinet_repo: InMemoryControlCabinetAdapter,
    system_type_repo: InMemorySpsControllerSystemTypeAdapter,
    clock: FixedClock,
) -> None:
    cid = new_id(ControlCabinetId)
    await cabinet_repo.create(
        ControlCabinet(
            id=cid,
            building_id=new_id(BuildingId),
            name="Cabinet 1",
            description=None,
            created_at=clock.now(),
        )
    )

    stid = new_id(SpsControllerSystemTypeId)
    await system_type_repo.create(
        SpsControllerSystemType(
            id=stid,
            name="S7-1200",
            description=None,
            created_at=clock.now(),
        )
    )

    result = await module.create_controller(
        CreateSpsControllerCommand(
            cabinet_id=cid,
            system_type_id=stid,
            name=" Controller 1 ",
            description="Test",
        )
    )

    assert isinstance(result, Ok)
    controller = result.unwrap()
    assert controller.name == "Controller 1"
    assert controller.cabinet_id == cid
    assert controller.system_type_id == stid
    assert controller.created_at == clock.now()


@pytest.mark.asyncio
async def test_create_controller_cabinet_missing(
    module: SpsControllerModule,
    system_type_repo: InMemorySpsControllerSystemTypeAdapter,
    clock: FixedClock,
) -> None:
    cid = new_id(ControlCabinetId)
    stid = new_id(SpsControllerSystemTypeId)
    await system_type_repo.create(
        SpsControllerSystemType(
            id=stid,
            name="S7-1200",
            description=None,
            created_at=clock.now(),
        )
    )

    result = await module.create_controller(
        CreateSpsControllerCommand(cabinet_id=cid, system_type_id=stid, name="C1")
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, ControlCabinetDoesNotExistError)


@pytest.mark.asyncio
async def test_create_controller_system_type_missing(
    module: SpsControllerModule,
    cabinet_repo: InMemoryControlCabinetAdapter,
    clock: FixedClock,
) -> None:
    cid = new_id(ControlCabinetId)
    await cabinet_repo.create(
        ControlCabinet(
            id=cid,
            building_id=new_id(BuildingId),
            name="Cabinet 1",
            description=None,
            created_at=clock.now(),
        )
    )

    stid = new_id(SpsControllerSystemTypeId)
    result = await module.create_controller(
        CreateSpsControllerCommand(cabinet_id=cid, system_type_id=stid, name="C1")
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, SpsControllerSystemTypeDoesNotExistError)


@pytest.mark.asyncio
async def test_create_controller_duplicate_name_in_cabinet(
    module: SpsControllerModule,
    cabinet_repo: InMemoryControlCabinetAdapter,
    system_type_repo: InMemorySpsControllerSystemTypeAdapter,
    clock: FixedClock,
) -> None:
    cid = new_id(ControlCabinetId)
    await cabinet_repo.create(
        ControlCabinet(
            id=cid,
            building_id=new_id(BuildingId),
            name="Cabinet 1",
            description=None,
            created_at=clock.now(),
        )
    )

    stid = new_id(SpsControllerSystemTypeId)
    await system_type_repo.create(
        SpsControllerSystemType(
            id=stid,
            name="S7-1200",
            description=None,
            created_at=clock.now(),
        )
    )

    await module.create_controller(
        CreateSpsControllerCommand(cabinet_id=cid, system_type_id=stid, name="C1")
    )
    result = await module.create_controller(
        CreateSpsControllerCommand(cabinet_id=cid, system_type_id=stid, name="C1")
    )

    assert isinstance(result, Err)
    assert isinstance(result.error, SpsControllerNameConflictError)


@pytest.mark.asyncio
async def test_get_controller_success(
    module: SpsControllerModule,
    cabinet_repo: InMemoryControlCabinetAdapter,
    system_type_repo: InMemorySpsControllerSystemTypeAdapter,
    clock: FixedClock,
) -> None:
    cid = new_id(ControlCabinetId)
    await cabinet_repo.create(
        ControlCabinet(
            id=cid,
            building_id=new_id(BuildingId),
            name="C1",
            description=None,
            created_at=clock.now(),
        )
    )
    stid = new_id(SpsControllerSystemTypeId)
    await system_type_repo.create(
        SpsControllerSystemType(id=stid, name="S1", description=None, created_at=clock.now())
    )

    created = (
        await module.create_controller(
            CreateSpsControllerCommand(cabinet_id=cid, system_type_id=stid, name="CTRL1")
        )
    ).unwrap()

    result = await module.get_controller(
        GetSpsControllerQuery(cabinet_id=cid, controller_id=created.id)
    )
    assert isinstance(result, Ok)
    assert result.unwrap().id == created.id


@pytest.mark.asyncio
async def test_list_controllers(
    module: SpsControllerModule,
    cabinet_repo: InMemoryControlCabinetAdapter,
    system_type_repo: InMemorySpsControllerSystemTypeAdapter,
    clock: FixedClock,
) -> None:
    cid = new_id(ControlCabinetId)
    await cabinet_repo.create(
        ControlCabinet(
            id=cid,
            building_id=new_id(BuildingId),
            name="C1",
            description=None,
            created_at=clock.now(),
        )
    )
    stid = new_id(SpsControllerSystemTypeId)
    await system_type_repo.create(
        SpsControllerSystemType(id=stid, name="S1", description=None, created_at=clock.now())
    )

    await module.create_controller(
        CreateSpsControllerCommand(cabinet_id=cid, system_type_id=stid, name="CTRL1")
    )
    await module.create_controller(
        CreateSpsControllerCommand(cabinet_id=cid, system_type_id=stid, name="CTRL2")
    )

    page = await module.list_controllers(
        ListSpsControllersQuery(cabinet_id=cid, page=PageParams(page=1, size=10))
    )
    assert page.total == 2
    assert len(page.items) == 2


@pytest.mark.asyncio
async def test_update_controller_success(
    module: SpsControllerModule,
    cabinet_repo: InMemoryControlCabinetAdapter,
    system_type_repo: InMemorySpsControllerSystemTypeAdapter,
    clock: FixedClock,
) -> None:
    cid = new_id(ControlCabinetId)
    await cabinet_repo.create(
        ControlCabinet(
            id=cid,
            building_id=new_id(BuildingId),
            name="C1",
            description=None,
            created_at=clock.now(),
        )
    )
    stid = new_id(SpsControllerSystemTypeId)
    await system_type_repo.create(
        SpsControllerSystemType(id=stid, name="S1", description=None, created_at=clock.now())
    )

    created = (
        await module.create_controller(
            CreateSpsControllerCommand(cabinet_id=cid, system_type_id=stid, name="CTRL1")
        )
    ).unwrap()

    result = await module.update_controller(
        UpdateSpsControllerCommand(
            cabinet_id=cid, controller_id=created.id, name="CTRL2", description="New desc"
        )
    )
    assert isinstance(result, Ok)
    assert result.unwrap().name == "CTRL2"
    assert result.unwrap().description == "New desc"


@pytest.mark.asyncio
async def test_delete_controller_success(
    module: SpsControllerModule,
    cabinet_repo: InMemoryControlCabinetAdapter,
    system_type_repo: InMemorySpsControllerSystemTypeAdapter,
    clock: FixedClock,
) -> None:
    cid = new_id(ControlCabinetId)
    await cabinet_repo.create(
        ControlCabinet(
            id=cid,
            building_id=new_id(BuildingId),
            name="C1",
            description=None,
            created_at=clock.now(),
        )
    )
    stid = new_id(SpsControllerSystemTypeId)
    await system_type_repo.create(
        SpsControllerSystemType(id=stid, name="S1", description=None, created_at=clock.now())
    )

    created = (
        await module.create_controller(
            CreateSpsControllerCommand(cabinet_id=cid, system_type_id=stid, name="CTRL1")
        )
    ).unwrap()

    result = await module.delete_controller(cabinet_id=cid, controller_id=created.id)
    assert isinstance(result, Ok)

    get_result = await module.get_controller(
        GetSpsControllerQuery(cabinet_id=cid, controller_id=created.id)
    )
    assert isinstance(get_result, Err)
