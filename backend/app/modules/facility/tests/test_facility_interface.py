from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.modules.facility.application.commands import (
    CreateFacilityCommand,
    UpdateFacilityCommand,
)
from app.modules.facility.application.queries import (
    GetFacilityQuery,
)
from app.modules.facility.application.use_cases import FacilityModule
from app.modules.facility.domain.errors import (
    FacilityNameConflictError,
    FacilityNotFoundError,
    InvalidFacilityNameError,
)
from app.modules.facility.infrastructure.in_memory_adapter import InMemoryFacilityAdapter
from app.shared.clock import FixedClock
from app.shared.ids import FacilityId
from app.shared.result import Err, Ok


@pytest.mark.asyncio
async def test_create_facility_success() -> None:
    fixed = datetime(2026, 1, 1, tzinfo=UTC)
    module = FacilityModule(repository=InMemoryFacilityAdapter(), clock=FixedClock(fixed))

    result = await module.create_facility(
        CreateFacilityCommand(name=" Facility A ", description="Test Description")
    )

    assert isinstance(result, Ok)
    facility = result.unwrap()
    assert facility.name == "Facility A"
    assert facility.description == "Test Description"
    assert facility.created_at == fixed


@pytest.mark.asyncio
async def test_create_facility_duplicate_name_conflict() -> None:
    module = FacilityModule(
        repository=InMemoryFacilityAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    first = await module.create_facility(CreateFacilityCommand(name="A"))
    assert isinstance(first, Ok)

    second = await module.create_facility(CreateFacilityCommand(name=" A "))
    assert isinstance(second, Err)
    assert isinstance(second.error, FacilityNameConflictError)


@pytest.mark.asyncio
async def test_create_facility_invalid_name() -> None:
    module = FacilityModule(
        repository=InMemoryFacilityAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    result = await module.create_facility(CreateFacilityCommand(name=""))
    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidFacilityNameError)


@pytest.mark.asyncio
async def test_get_facility_success() -> None:
    module = FacilityModule(
        repository=InMemoryFacilityAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    created_result = await module.create_facility(CreateFacilityCommand(name="A"))
    created = created_result.unwrap()

    result = await module.get_facility(GetFacilityQuery(facility_id=created.id))
    assert isinstance(result, Ok)
    assert result.unwrap().id == created.id


@pytest.mark.asyncio
async def test_get_facility_missing() -> None:
    module = FacilityModule(
        repository=InMemoryFacilityAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    result = await module.get_facility(GetFacilityQuery(facility_id=FacilityId(uuid4())))
    assert isinstance(result, Err)
    assert isinstance(result.error, FacilityNotFoundError)


@pytest.mark.asyncio
async def test_update_facility_success() -> None:
    module = FacilityModule(
        repository=InMemoryFacilityAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    created_result = await module.create_facility(CreateFacilityCommand(name="A"))
    created = created_result.unwrap()

    update_result = await module.update_facility(
        UpdateFacilityCommand(facility_id=created.id, name="B", description="Updated")
    )
    assert isinstance(update_result, Ok)
    updated = update_result.unwrap()
    assert updated.name == "B"
    assert updated.description == "Updated"


@pytest.mark.asyncio
async def test_delete_facility_success() -> None:
    module = FacilityModule(
        repository=InMemoryFacilityAdapter(),
        clock=FixedClock(datetime(2026, 1, 1, tzinfo=UTC)),
    )

    created_result = await module.create_facility(CreateFacilityCommand(name="A"))
    created = created_result.unwrap()

    delete_result = await module.delete_facility(created.id)
    assert isinstance(delete_result, Ok)

    get_result = await module.get_facility(GetFacilityQuery(facility_id=created.id))
    assert isinstance(get_result, Err)
