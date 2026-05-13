"""Integration tests for SqlAlchemySpsControllerSystemTypeAdapter.

Tests cover CRUD + pagination + uniqueness constraints for SPS controller system types
against a real PostgreSQL database.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

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
from app.modules.sps_controller_system_type.infrastructure.sqlalchemy_adapter import (
    SqlAlchemySpsControllerSystemTypeAdapter,
)
from app.shared.clock import FixedClock
from app.shared.ids import SpsControllerSystemTypeId, new_id
from app.shared.pagination import PageParams
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def _make_module(session: AsyncSession) -> SpsControllerSystemTypeModule:
    return SpsControllerSystemTypeModule(
        repository=SqlAlchemySpsControllerSystemTypeAdapter(session),
        clock=FixedClock(_FIXED),
    )


@pytest.mark.asyncio
async def test_create_and_get_system_type(session: AsyncSession) -> None:
    module = _make_module(session)

    result = await module.create_system_type(
        CreateSpsControllerSystemTypeCommand(name="Siemens S7-300", description="Classic PLC")
    )
    assert isinstance(result, Ok)
    system_type = result.value

    fetched = await module.get_system_type(
        GetSpsControllerSystemTypeQuery(system_type_id=system_type.id)
    )
    assert isinstance(fetched, Ok)
    assert fetched.value.name == "Siemens S7-300"
    assert fetched.value.description == "Classic PLC"


@pytest.mark.asyncio
async def test_get_system_type_not_found(session: AsyncSession) -> None:
    module = _make_module(session)

    result = await module.get_system_type(
        GetSpsControllerSystemTypeQuery(
            system_type_id=new_id(SpsControllerSystemTypeId)
        )
    )
    assert isinstance(result, Err)
    assert isinstance(result.error, SpsControllerSystemTypeNotFoundError)


@pytest.mark.asyncio
async def test_duplicate_system_type_name_raises_conflict(session: AsyncSession) -> None:
    module = _make_module(session)

    first = await module.create_system_type(
        CreateSpsControllerSystemTypeCommand(name="Unique Type ST")
    )
    assert isinstance(first, Ok)

    second = await module.create_system_type(
        CreateSpsControllerSystemTypeCommand(name=" Unique Type ST ")
    )
    assert isinstance(second, Err)
    assert isinstance(second.error, SpsControllerSystemTypeNameConflictError)


@pytest.mark.asyncio
async def test_update_system_type(session: AsyncSession) -> None:
    module = _make_module(session)

    created = (
        await module.create_system_type(
            CreateSpsControllerSystemTypeCommand(
                name="Before ST", description="Old desc"
            )
        )
    ).unwrap()

    updated = (
        await module.update_system_type(
            UpdateSpsControllerSystemTypeCommand(
                system_type_id=created.id,
                name="After ST",
                description="New desc",
            )
        )
    ).unwrap()

    assert updated.name == "After ST"
    assert updated.description == "New desc"


@pytest.mark.asyncio
async def test_delete_system_type(session: AsyncSession) -> None:
    module = _make_module(session)

    created = (
        await module.create_system_type(
            CreateSpsControllerSystemTypeCommand(name="To Delete ST")
        )
    ).unwrap()

    delete_result = await module.delete_system_type(created.id)
    assert isinstance(delete_result, Ok)

    get_result = await module.get_system_type(
        GetSpsControllerSystemTypeQuery(system_type_id=created.id)
    )
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, SpsControllerSystemTypeNotFoundError)


@pytest.mark.asyncio
async def test_list_system_types_pagination(session: AsyncSession) -> None:
    module = _make_module(session)

    for i in range(4):
        await module.create_system_type(
            CreateSpsControllerSystemTypeCommand(name=f"Paginated ST {i}")
        )

    page = await module.list_system_types(
        ListSpsControllerSystemTypesQuery(page=PageParams(page=1, size=3))
    )
    assert page.total >= 4
    assert len(page.items) <= 3
