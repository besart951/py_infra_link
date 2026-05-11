from __future__ import annotations

from app.modules.control_cabinet.domain.interface import ControlCabinetRepository
from app.modules.sps_controller.application.commands import (
    CreateSpsControllerCommand,
    UpdateSpsControllerCommand,
)
from app.modules.sps_controller.application.queries import (
    GetSpsControllerQuery,
    ListSpsControllersQuery,
)
from app.modules.sps_controller.domain.errors import (
    ControlCabinetDoesNotExistError,
    InvalidSpsControllerNameError,
    SpsControllerNameConflictError,
    SpsControllerNotFoundError,
    SpsControllerSystemTypeDoesNotExistError,
)
from app.modules.sps_controller.domain.interface import SpsControllerRepository
from app.modules.sps_controller.domain.models import SpsController
from app.modules.sps_controller.domain.value_objects import SpsControllerName
from app.modules.sps_controller_system_type.domain.interface import (
    SpsControllerSystemTypeRepository,
)
from app.shared.clock import Clock
from app.shared.ids import ControlCabinetId, SpsControllerId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


class SpsControllerModule:
    def __init__(
        self,
        controller_repository: SpsControllerRepository,
        cabinet_repository: ControlCabinetRepository,
        system_type_repository: SpsControllerSystemTypeRepository,
        clock: Clock,
    ) -> None:
        self._controller_repository = controller_repository
        self._cabinet_repository = cabinet_repository
        self._system_type_repository = system_type_repository
        self._clock = clock

    async def create_controller(
        self, command: CreateSpsControllerCommand
    ) -> Result[
        SpsController,
        ControlCabinetDoesNotExistError
        | SpsControllerSystemTypeDoesNotExistError
        | SpsControllerNameConflictError
        | InvalidSpsControllerNameError,
    ]:
        try:
            name = SpsControllerName.parse(command.name)
        except InvalidSpsControllerNameError as exc:
            return Err(exc)

        cabinet = await self._cabinet_repository.get_by_id(command.cabinet_id)
        if cabinet is None:
            return Err(
                ControlCabinetDoesNotExistError(
                    f"Control cabinet '{command.cabinet_id}' does not exist"
                )
            )

        system_type = await self._system_type_repository.get_by_id(command.system_type_id)
        if system_type is None:
            return Err(
                SpsControllerSystemTypeDoesNotExistError(
                    f"SPS controller system type '{command.system_type_id}' does not exist"
                )
            )

        existing = await self._controller_repository.get_by_cabinet_and_name(
            command.cabinet_id, name
        )
        if existing is not None:
            return Err(
                SpsControllerNameConflictError(
                    f"SPS controller with name '{name.value}' already exists in this cabinet"
                )
            )

        controller = SpsController(
            id=new_id(SpsControllerId),
            cabinet_id=command.cabinet_id,
            system_type_id=command.system_type_id,
            name=name.value,
            description=command.description,
            created_at=self._clock.now(),
        )
        created = await self._controller_repository.create(controller)
        return Ok(created)

    async def get_controller(
        self, query: GetSpsControllerQuery
    ) -> Result[SpsController, SpsControllerNotFoundError]:
        controller = await self._controller_repository.get_by_id(query.controller_id)
        if controller is None or controller.cabinet_id != query.cabinet_id:
            return Err(
                SpsControllerNotFoundError(f"SPS controller '{query.controller_id}' was not found")
            )
        return Ok(controller)

    async def list_controllers(self, query: ListSpsControllersQuery) -> Page[SpsController]:
        items, total = await self._controller_repository.list_page(query.cabinet_id, query.page)
        return Page[SpsController](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def update_controller(
        self, command: UpdateSpsControllerCommand
    ) -> Result[
        SpsController,
        SpsControllerNotFoundError
        | SpsControllerSystemTypeDoesNotExistError
        | SpsControllerNameConflictError
        | InvalidSpsControllerNameError,
    ]:
        controller = await self._controller_repository.get_by_id(command.controller_id)
        if controller is None or controller.cabinet_id != command.cabinet_id:
            return Err(
                SpsControllerNotFoundError(
                    f"SPS controller '{command.controller_id}' was not found"
                )
            )

        name_value = controller.name
        if command.name is not None:
            try:
                name = SpsControllerName.parse(command.name)
                name_value = name.value
            except InvalidSpsControllerNameError as exc:
                return Err(exc)

            if name_value != controller.name:
                existing = await self._controller_repository.get_by_cabinet_and_name(
                    command.cabinet_id, name
                )
                if existing is not None:
                    return Err(
                        SpsControllerNameConflictError(
                            f"SPS controller with name '{name.value}' "
                            "already exists in this cabinet"
                        )
                    )

        system_type_id = controller.system_type_id
        if command.system_type_id is not None:
            system_type = await self._system_type_repository.get_by_id(command.system_type_id)
            if system_type is None:
                return Err(
                    SpsControllerSystemTypeDoesNotExistError(
                        f"SPS controller system type '{command.system_type_id}' does not exist"
                    )
                )
            system_type_id = command.system_type_id

        description = (
            command.description if command.description is not None else controller.description
        )

        updated_controller = SpsController(
            id=controller.id,
            cabinet_id=controller.cabinet_id,
            system_type_id=system_type_id,
            name=name_value,
            description=description,
            created_at=controller.created_at,
        )
        updated = await self._controller_repository.update(updated_controller)
        return Ok(updated)

    async def delete_controller(
        self, cabinet_id: ControlCabinetId, controller_id: SpsControllerId
    ) -> Result[None, SpsControllerNotFoundError]:
        controller = await self._controller_repository.get_by_id(controller_id)
        if controller is None or controller.cabinet_id != cabinet_id:
            return Err(
                SpsControllerNotFoundError(f"SPS controller '{controller_id}' was not found")
            )

        await self._controller_repository.delete(controller_id)
        return Ok(None)
