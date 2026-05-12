from __future__ import annotations

from dataclasses import dataclass

from app.modules.field_device.application.commands import (
    CreateFieldDeviceCommand,
    UpdateFieldDeviceCommand,
)
from app.modules.field_device.application.queries import (
    GetFieldDeviceQuery,
    ListFieldDevicesQuery,
)
from app.modules.field_device.domain.errors import (
    FieldDeviceNameConflictError,
    FieldDeviceNotFoundError,
    InvalidFieldDeviceNameError,
    SpsControllerDoesNotExistError,
)
from app.modules.field_device.domain.interface import FieldDeviceRepository
from app.modules.field_device.domain.models import FieldDevice
from app.modules.field_device.domain.value_objects import FieldDeviceName
from app.modules.sps_controller.domain.interface import SpsControllerRepository
from app.shared.clock import Clock
from app.shared.ids import FieldDeviceId, SpsControllerId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class FieldDeviceModule:
    device_repository: FieldDeviceRepository
    controller_repository: SpsControllerRepository
    clock: Clock

    async def create_device(
        self, command: CreateFieldDeviceCommand
    ) -> Result[
        FieldDevice,
        SpsControllerDoesNotExistError
        | FieldDeviceNameConflictError
        | InvalidFieldDeviceNameError,
    ]:
        try:
            name = FieldDeviceName.parse(command.name)
        except InvalidFieldDeviceNameError as exc:
            return Err(exc)

        controller = await self.controller_repository.get_by_id(command.controller_id)
        if controller is None:
            return Err(
                SpsControllerDoesNotExistError(
                    f"SPS controller '{command.controller_id}' does not exist"
                )
            )

        existing = await self.device_repository.get_by_controller_and_name(
            command.controller_id, name
        )
        if existing is not None:
            return Err(
                FieldDeviceNameConflictError(
                    f"Field device with name '{name.value}' "
                    "already exists under this SPS controller"
                )
            )

        device = FieldDevice(
            id=new_id(FieldDeviceId),
            controller_id=command.controller_id,
            name=name.value,
            description=command.description,
            created_at=self.clock.now(),
        )
        created = await self.device_repository.create(device)
        return Ok(created)

    async def get_device(
        self, query: GetFieldDeviceQuery
    ) -> Result[FieldDevice, FieldDeviceNotFoundError]:
        device = await self.device_repository.get_by_id(query.device_id)
        if device is None or device.controller_id != query.controller_id:
            return Err(
                FieldDeviceNotFoundError(f"Field device '{query.device_id}' was not found")
            )
        return Ok(device)

    async def list_devices(self, query: ListFieldDevicesQuery) -> Page[FieldDevice]:
        items, total = await self.device_repository.list_page(query.controller_id, query.page)
        return Page[FieldDevice](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def update_device(
        self, command: UpdateFieldDeviceCommand
    ) -> Result[
        FieldDevice,
        FieldDeviceNotFoundError | FieldDeviceNameConflictError | InvalidFieldDeviceNameError,
    ]:
        device = await self.device_repository.get_by_id(command.device_id)
        if device is None or device.controller_id != command.controller_id:
            return Err(
                FieldDeviceNotFoundError(f"Field device '{command.device_id}' was not found")
            )

        name_value = device.name
        if command.name is not None:
            try:
                name = FieldDeviceName.parse(command.name)
                name_value = name.value
            except InvalidFieldDeviceNameError as exc:
                return Err(exc)

            if name_value != device.name:
                existing = await self.device_repository.get_by_controller_and_name(
                    command.controller_id, name
                )
                if existing is not None:
                    return Err(
                        FieldDeviceNameConflictError(
                            f"Field device with name '{name.value}' "
                            "already exists under this SPS controller"
                        )
                    )

        description = command.description if command.description is not None else device.description

        updated_device = FieldDevice(
            id=device.id,
            controller_id=device.controller_id,
            name=name_value,
            description=description,
            created_at=device.created_at,
        )
        updated = await self.device_repository.update(updated_device)
        return Ok(updated)

    async def delete_device(
        self, controller_id: SpsControllerId, device_id: FieldDeviceId
    ) -> Result[None, FieldDeviceNotFoundError]:
        device = await self.device_repository.get_by_id(device_id)
        if device is None or device.controller_id != controller_id:
            return Err(FieldDeviceNotFoundError(f"Field device '{device_id}' was not found"))

        await self.device_repository.delete(device_id)
        return Ok(None)
