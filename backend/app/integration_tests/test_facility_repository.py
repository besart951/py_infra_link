"""Integration tests for SqlAlchemyFacilityAdapter against a real PostgreSQL database."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.facility.application.commands import (
    CreateFacilityCommand,
    UpdateFacilityCommand,
)
from app.modules.facility.application.queries import GetFacilityQuery
from app.modules.facility.application.use_cases import FacilityModule
from app.modules.facility.domain.errors import FacilityNameConflictError, FacilityNotFoundError
from app.modules.facility.infrastructure.sqlalchemy_adapter import SqlAlchemyFacilityAdapter
from app.shared.clock import FixedClock
from app.shared.ids import FacilityId, new_id
from app.shared.result import Err, Ok

pytestmark = pytest.mark.integration

_FIXED = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)


def _make_module(session: AsyncSession) -> FacilityModule:
    return FacilityModule(
        repository=SqlAlchemyFacilityAdapter(session),
        clock=FixedClock(_FIXED),
    )


@pytest.mark.asyncio
async def test_create_and_get_facility(session: AsyncSession) -> None:
    module = _make_module(session)

    result = await module.create_facility(
        CreateFacilityCommand(name="Plant A", description="Main plant")
    )
    assert isinstance(result, Ok)
    facility = result.value

    fetched = await module.get_facility(GetFacilityQuery(facility_id=facility.id))
    assert isinstance(fetched, Ok)
    assert fetched.value.name == "Plant A"
    assert fetched.value.description == "Main plant"


@pytest.mark.asyncio
async def test_get_facility_not_found(session: AsyncSession) -> None:
    module = _make_module(session)

    result = await module.get_facility(GetFacilityQuery(facility_id=new_id(FacilityId)))
    assert isinstance(result, Err)
    assert isinstance(result.error, FacilityNotFoundError)


@pytest.mark.asyncio
async def test_create_duplicate_name_raises_conflict(session: AsyncSession) -> None:
    module = _make_module(session)

    first = await module.create_facility(CreateFacilityCommand(name="Unique Plant"))
    assert isinstance(first, Ok)

    second = await module.create_facility(CreateFacilityCommand(name=" Unique Plant "))
    assert isinstance(second, Err)
    assert isinstance(second.error, FacilityNameConflictError)


@pytest.mark.asyncio
async def test_update_facility(session: AsyncSession) -> None:
    module = _make_module(session)

    created = (
        await module.create_facility(CreateFacilityCommand(name="Old Name", description="Old"))
    ).unwrap()

    updated = (
        await module.update_facility(
            UpdateFacilityCommand(
                facility_id=created.id, name="New Name", description="New desc"
            )
        )
    ).unwrap()

    assert updated.name == "New Name"
    assert updated.description == "New desc"


@pytest.mark.asyncio
async def test_delete_facility(session: AsyncSession) -> None:
    module = _make_module(session)

    created = (await module.create_facility(CreateFacilityCommand(name="To Delete"))).unwrap()

    delete_result = await module.delete_facility(created.id)
    assert isinstance(delete_result, Ok)

    get_result = await module.get_facility(GetFacilityQuery(facility_id=created.id))
    assert isinstance(get_result, Err)
    assert isinstance(get_result.error, FacilityNotFoundError)
