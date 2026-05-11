from __future__ import annotations

from datetime import UTC, datetime

import pytest

from app.modules.sps_controller_system_type.application.commands import (
    CreateSpsControllerSystemTypeCommand,
    UpdateSpsControllerSystemTypeCommand,
)
from app.modules.sps_controller_system_type.application.queries import (
    GetSpsControllerSystemTypeQuery,
    ListSpsControllerSystemTypesQuery,
)
from app.modules.sps_controller_system_type.application.use_cases import (
    SpsControllerSystemTypeModule,
)
from app.modules.sps_controller_system_type.domain.errors import (
    SpsControllerSystemTypeNameConflictError,
    SpsControllerSystemTypeNotFoundError,
)
from app.modules.sps_controller_system_type.infrastructure.in_memory_adapter import (
    InMemorySpsControllerSystemTypeAdapter,
)
from app.shared.clock import FixedClock
from app.shared.ids import SpsControllerSystemTypeId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock(datetime(2026, 1, 1, tzinfo=UTC))


@pytest.fixture
def repository() -> InMemorySpsControllerSystemTypeAdapter:
    return InMemorySpsControllerSystemTypeAdapter()


@pytest.fixture
def module(
    repository: InMemorySpsControllerSystemTypeAdapter, clock: FixedClock
) -> SpsControllerSystemTypeModule:
    return SpsControllerSystemTypeModule(repository=repository, clock=clock)


@pytest.mark.asyncio
async def test_create_system_type_success(
    module: SpsControllerSystemTypeModule, clock: FixedClock
) -> None:
    result = await module.create_system_type(
        CreateSpsControllerSystemTypeCommand(name=" Siemens S7-1200 ", description="Test")
    )

    assert isinstance(result, Ok)
    system_type = result.unwrap()
    assert system_type.name == "Siemens S7-1200"
    assert system_type.description == "Test"
    assert system_type.created_at == clock.now()


@pytest.mark.asyncio
async def test_create_system_type_duplicate_name(module: SpsControllerSystemTypeModule) -> None:
    await module.create_system_type(CreateSpsControllerSystemTypeCommand(name="S1"))
    result = await module.create_system_type(CreateSpsControllerSystemTypeCommand(name="S1"))

    assert isinstance(result, Err)
    assert isinstance(result.error, SpsControllerSystemTypeNameConflictError)


@pytest.mark.asyncio
async def test_get_system_type_success(module: SpsControllerSystemTypeModule) -> None:
    created = (
        await module.create_system_type(CreateSpsControllerSystemTypeCommand(name="S1"))
    ).unwrap()

    result = await module.get_system_type(
        GetSpsControllerSystemTypeQuery(system_type_id=created.id)
    )
    assert isinstance(result, Ok)
    assert result.unwrap().id == created.id


@pytest.mark.asyncio
async def test_get_system_type_not_found(module: SpsControllerSystemTypeModule) -> None:
    result = await module.get_system_type(
        GetSpsControllerSystemTypeQuery(system_type_id=new_id(SpsControllerSystemTypeId))
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, SpsControllerSystemTypeNotFoundError)


@pytest.mark.asyncio
async def test_list_system_types(module: SpsControllerSystemTypeModule) -> None:
    await module.create_system_type(CreateSpsControllerSystemTypeCommand(name="S1"))
    await module.create_system_type(CreateSpsControllerSystemTypeCommand(name="S2"))

    page = await module.list_system_types(
        ListSpsControllerSystemTypesQuery(page=PageParams(page=1, size=10))
    )
    assert page.total == 2
    assert len(page.items) == 2


@pytest.mark.asyncio
async def test_update_system_type_success(module: SpsControllerSystemTypeModule) -> None:
    created = (
        await module.create_system_type(CreateSpsControllerSystemTypeCommand(name="S1"))
    ).unwrap()

    result = await module.update_system_type(
        UpdateSpsControllerSystemTypeCommand(
            system_type_id=created.id, name="S2", description="New desc"
        )
    )
    assert isinstance(result, Ok)
    assert result.unwrap().name == "S2"
    assert result.unwrap().description == "New desc"


@pytest.mark.asyncio
async def test_delete_system_type_success(module: SpsControllerSystemTypeModule) -> None:
    created = (
        await module.create_system_type(CreateSpsControllerSystemTypeCommand(name="S1"))
    ).unwrap()

    result = await module.delete_system_type(system_type_id=created.id)
    assert isinstance(result, Ok)

    get_result = await module.get_system_type(
        GetSpsControllerSystemTypeQuery(system_type_id=created.id)
    )
    assert isinstance(get_result, Err)
