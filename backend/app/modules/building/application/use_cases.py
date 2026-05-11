from __future__ import annotations

from app.modules.building.application.commands import (
    CreateBuildingCommand,
    UpdateBuildingCommand,
)
from app.modules.building.application.queries import (
    GetBuildingQuery,
    ListBuildingsQuery,
)
from app.modules.building.domain.errors import (
    BuildingNameConflictError,
    BuildingNotFoundError,
    FacilityDoesNotExistError,
    InvalidBuildingNameError,
)
from app.modules.building.domain.interface import BuildingRepository
from app.modules.building.domain.models import Building
from app.modules.building.domain.value_objects import BuildingName
from app.modules.facility.domain.interface import FacilityRepository
from app.shared.clock import Clock
from app.shared.ids import BuildingId, FacilityId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


class BuildingModule:
    def __init__(
        self,
        building_repository: BuildingRepository,
        facility_repository: FacilityRepository,
        clock: Clock,
    ) -> None:
        self._building_repository = building_repository
        self._facility_repository = facility_repository
        self._clock = clock

    async def create_building(
        self, command: CreateBuildingCommand
    ) -> Result[
        Building,
        FacilityDoesNotExistError | BuildingNameConflictError | InvalidBuildingNameError,
    ]:
        # Validate name
        try:
            name = BuildingName.parse(command.name)
        except InvalidBuildingNameError as exc:
            return Err(exc)

        # Verify facility exists
        facility = await self._facility_repository.get_by_id(command.facility_id)
        if facility is None:
            return Err(
                FacilityDoesNotExistError(f"Facility '{command.facility_id}' does not exist")
            )


        # Check for name conflict in this facility
        existing = await self._building_repository.get_by_facility_and_name(
            command.facility_id, name
        )
        if existing is not None:
            return Err(
                BuildingNameConflictError(
                    f"Building with name '{name.value}' already exists in this facility"
                )
            )

        building = Building(
            id=new_id(BuildingId),
            facility_id=command.facility_id,
            name=name.value,
            description=command.description,
            created_at=self._clock.now(),
        )
        created = await self._building_repository.create(building)
        return Ok(created)

    async def get_building(
        self, query: GetBuildingQuery
    ) -> Result[Building, BuildingNotFoundError]:
        building = await self._building_repository.get_by_id(query.building_id)
        if building is None or building.facility_id != query.facility_id:
            return Err(BuildingNotFoundError(f"Building '{query.building_id}' was not found"))
        return Ok(building)

    async def list_buildings(self, query: ListBuildingsQuery) -> Page[Building]:
        items, total = await self._building_repository.list_page(query.facility_id, query.page)
        return Page[Building](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def update_building(
        self, command: UpdateBuildingCommand
    ) -> Result[
        Building,
        BuildingNotFoundError | BuildingNameConflictError | InvalidBuildingNameError,
    ]:
        building = await self._building_repository.get_by_id(command.building_id)
        if building is None or building.facility_id != command.facility_id:
            return Err(BuildingNotFoundError(f"Building '{command.building_id}' was not found"))

        name_value = building.name
        if command.name is not None:
            try:
                name = BuildingName.parse(command.name)
                name_value = name.value
            except InvalidBuildingNameError as exc:
                return Err(exc)

            if name_value != building.name:
                existing = await self._building_repository.get_by_facility_and_name(
                    command.facility_id, name
                )
                if existing is not None:
                    return Err(
                        BuildingNameConflictError(
                            f"Building with name '{name.value}' already exists in this facility"
                        )
                    )

        description = (
            command.description if command.description is not None else building.description
        )

        updated_building = Building(
            id=building.id,
            facility_id=building.facility_id,
            name=name_value,
            description=description,
            created_at=building.created_at,
        )
        updated = await self._building_repository.update(updated_building)
        return Ok(updated)

    async def delete_building(
        self, facility_id: FacilityId, building_id: BuildingId
    ) -> Result[None, BuildingNotFoundError]:
        building = await self._building_repository.get_by_id(building_id)
        if building is None or building.facility_id != facility_id:
            return Err(BuildingNotFoundError(f"Building '{building_id}' was not found"))

        await self._building_repository.delete(building_id)
        return Ok(None)
