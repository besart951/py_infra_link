from __future__ import annotations

from app.modules.building.domain.interface import BuildingRepository
from app.modules.control_cabinet.application.commands import (
    CreateControlCabinetCommand,
    UpdateControlCabinetCommand,
)
from app.modules.control_cabinet.application.queries import (
    GetControlCabinetQuery,
    ListControlCabinetsQuery,
)
from app.modules.control_cabinet.domain.errors import (
    BuildingDoesNotExistError,
    ControlCabinetNameConflictError,
    ControlCabinetNotFoundError,
    InvalidControlCabinetNameError,
)
from app.modules.control_cabinet.domain.interface import ControlCabinetRepository
from app.modules.control_cabinet.domain.models import ControlCabinet
from app.modules.control_cabinet.domain.value_objects import ControlCabinetName
from app.shared.clock import Clock
from app.shared.ids import BuildingId, ControlCabinetId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


class ControlCabinetModule:
    def __init__(
        self,
        cabinet_repository: ControlCabinetRepository,
        building_repository: BuildingRepository,
        clock: Clock,
    ) -> None:
        self._cabinet_repository = cabinet_repository
        self._building_repository = building_repository
        self._clock = clock

    async def create_cabinet(
        self, command: CreateControlCabinetCommand
    ) -> Result[
        ControlCabinet,
        BuildingDoesNotExistError
        | ControlCabinetNameConflictError
        | InvalidControlCabinetNameError,
    ]:
        try:
            name = ControlCabinetName.parse(command.name)
        except InvalidControlCabinetNameError as exc:
            return Err(exc)

        building = await self._building_repository.get_by_id(command.building_id)
        if building is None:
            return Err(
                BuildingDoesNotExistError(f"Building '{command.building_id}' does not exist")
            )

        existing = await self._cabinet_repository.get_by_building_and_name(
            command.building_id, name
        )
        if existing is not None:
            return Err(
                ControlCabinetNameConflictError(
                    f"Control cabinet with name '{name.value}' already exists in this building"
                )
            )

        cabinet = ControlCabinet(
            id=new_id(ControlCabinetId),
            building_id=command.building_id,
            name=name.value,
            description=command.description,
            created_at=self._clock.now(),
        )
        created = await self._cabinet_repository.create(cabinet)
        return Ok(created)

    async def get_cabinet(
        self, query: GetControlCabinetQuery
    ) -> Result[ControlCabinet, ControlCabinetNotFoundError]:
        cabinet = await self._cabinet_repository.get_by_id(query.cabinet_id)
        if cabinet is None or cabinet.building_id != query.building_id:
            return Err(
                ControlCabinetNotFoundError(f"Control cabinet '{query.cabinet_id}' was not found")
            )
        return Ok(cabinet)

    async def list_cabinets(self, query: ListControlCabinetsQuery) -> Page[ControlCabinet]:
        items, total = await self._cabinet_repository.list_page(query.building_id, query.page)
        return Page[ControlCabinet](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def update_cabinet(
        self, command: UpdateControlCabinetCommand
    ) -> Result[
        ControlCabinet,
        ControlCabinetNotFoundError
        | ControlCabinetNameConflictError
        | InvalidControlCabinetNameError,
    ]:
        cabinet = await self._cabinet_repository.get_by_id(command.cabinet_id)
        if cabinet is None or cabinet.building_id != command.building_id:
            return Err(
                ControlCabinetNotFoundError(f"Control cabinet '{command.cabinet_id}' was not found")
            )

        name_value = cabinet.name
        if command.name is not None:
            try:
                name = ControlCabinetName.parse(command.name)
                name_value = name.value
            except InvalidControlCabinetNameError as exc:
                return Err(exc)

            if name_value != cabinet.name:
                existing = await self._cabinet_repository.get_by_building_and_name(
                    command.building_id, name
                )
                if existing is not None:
                    return Err(
                        ControlCabinetNameConflictError(
                            f"Control cabinet with name '{name.value}' "
                            "already exists in this building"
                        )
                    )

        description = (
            command.description if command.description is not None else cabinet.description
        )

        updated_cabinet = ControlCabinet(
            id=cabinet.id,
            building_id=cabinet.building_id,
            name=name_value,
            description=description,
            created_at=cabinet.created_at,
        )
        updated = await self._cabinet_repository.update(updated_cabinet)
        return Ok(updated)

    async def delete_cabinet(
        self, building_id: BuildingId, cabinet_id: ControlCabinetId
    ) -> Result[None, ControlCabinetNotFoundError]:
        cabinet = await self._cabinet_repository.get_by_id(cabinet_id)
        if cabinet is None or cabinet.building_id != building_id:
            return Err(ControlCabinetNotFoundError(f"Control cabinet '{cabinet_id}' was not found"))

        await self._cabinet_repository.delete(cabinet_id)
        return Ok(None)
