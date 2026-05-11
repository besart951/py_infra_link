from __future__ import annotations

from dataclasses import dataclass

from app.modules.facility.application.commands import (
    CreateFacilityCommand,
    UpdateFacilityCommand,
)
from app.modules.facility.application.queries import (
    GetFacilityQuery,
    ListFacilitiesQuery,
)
from app.modules.facility.domain.errors import (
    FacilityNameConflictError,
    FacilityNotFoundError,
    InvalidFacilityNameError,
)
from app.modules.facility.domain.interface import FacilityRepository
from app.modules.facility.domain.models import Facility
from app.modules.facility.domain.value_objects import FacilityName
from app.shared.clock import Clock
from app.shared.ids import FacilityId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class FacilityModule:
    repository: FacilityRepository
    clock: Clock

    async def create_facility(
        self, command: CreateFacilityCommand
    ) -> Result[Facility, FacilityNameConflictError | InvalidFacilityNameError]:
        try:
            name = FacilityName.parse(command.name)
        except InvalidFacilityNameError as exc:
            return Err(exc)

        existing = await self.repository.get_by_name(name)
        if existing is not None:
            return Err(
                FacilityNameConflictError(f"Facility with name '{name.value}' already exists")
            )

        facility = Facility(
            id=new_id(FacilityId),
            name=name.value,
            description=command.description,
            created_at=self.clock.now(),
        )
        created = await self.repository.create(facility)
        return Ok(created)

    async def get_facility(
        self, query: GetFacilityQuery
    ) -> Result[Facility, FacilityNotFoundError]:
        facility = await self.repository.get_by_id(query.facility_id)
        if facility is None:
            return Err(FacilityNotFoundError(f"Facility '{query.facility_id}' was not found"))
        return Ok(facility)

    async def list_facilities(self, query: ListFacilitiesQuery) -> Page[Facility]:
        items, total = await self.repository.list_page(query.page)
        return Page[Facility](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def update_facility(
        self, command: UpdateFacilityCommand
    ) -> Result[
        Facility, FacilityNotFoundError | FacilityNameConflictError | InvalidFacilityNameError
    ]:
        facility = await self.repository.get_by_id(command.facility_id)
        if facility is None:
            return Err(FacilityNotFoundError(f"Facility '{command.facility_id}' was not found"))

        name_value = facility.name
        if command.name is not None:
            try:
                name = FacilityName.parse(command.name)
                name_value = name.value
            except InvalidFacilityNameError as exc:
                return Err(exc)

            if name_value != facility.name:
                existing = await self.repository.get_by_name(name)
                if existing is not None:
                    return Err(
                        FacilityNameConflictError(
                            f"Facility with name '{name.value}' already exists"
                        )
                    )

        description = (
            command.description if command.description is not None else facility.description
        )

        updated_facility = Facility(
            id=facility.id,
            name=name_value,
            description=description,
            created_at=facility.created_at,
        )
        updated = await self.repository.update(updated_facility)
        return Ok(updated)

    async def delete_facility(self, facility_id: FacilityId) -> Result[None, FacilityNotFoundError]:
        facility = await self.repository.get_by_id(facility_id)
        if facility is None:
            return Err(FacilityNotFoundError(f"Facility '{facility_id}' was not found"))

        await self.repository.delete(facility_id)
        return Ok(None)
