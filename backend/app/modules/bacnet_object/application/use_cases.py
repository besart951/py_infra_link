from __future__ import annotations

from dataclasses import dataclass

from app.modules.bacnet_object.application.commands import (
    CreateBacnetObjectCommand,
    UpdateBacnetObjectCommand,
)
from app.modules.bacnet_object.application.queries import (
    GetBacnetObjectQuery,
    ListBacnetObjectsQuery,
)
from app.modules.bacnet_object.domain.errors import (
    BacnetObjectInstanceConflictError,
    BacnetObjectNameConflictError,
    BacnetObjectNotFoundError,
    FieldDeviceDoesNotExistError,
    InvalidBacnetObjectInstanceError,
    InvalidBacnetObjectNameError,
)
from app.modules.bacnet_object.domain.interface import BacnetObjectRepository
from app.modules.bacnet_object.domain.models import BacnetObject
from app.modules.bacnet_object.domain.value_objects import (
    BacnetObjectInstance,
    BacnetObjectName,
)
from app.modules.field_device.domain.interface import FieldDeviceRepository
from app.shared.clock import Clock
from app.shared.ids import BacnetObjectId, FieldDeviceId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


@dataclass(frozen=True, slots=True)
class BacnetObjectModule:
    object_repository: BacnetObjectRepository
    device_repository: FieldDeviceRepository
    clock: Clock

    async def create_object(
        self, command: CreateBacnetObjectCommand
    ) -> Result[
        BacnetObject,
        FieldDeviceDoesNotExistError
        | BacnetObjectInstanceConflictError
        | BacnetObjectNameConflictError
        | InvalidBacnetObjectNameError
        | InvalidBacnetObjectInstanceError,
    ]:
        try:
            name = BacnetObjectName.parse(command.name)
        except InvalidBacnetObjectNameError as exc:
            return Err(exc)

        try:
            BacnetObjectInstance.parse(command.object_instance)
        except InvalidBacnetObjectInstanceError as exc:
            return Err(exc)

        device = await self.device_repository.get_by_id(command.device_id)
        if device is None:
            return Err(
                FieldDeviceDoesNotExistError(
                    f"Field device '{command.device_id}' does not exist"
                )
            )

        existing_instance = await self.object_repository.get_by_device_type_instance(
            command.device_id, command.object_type, command.object_instance
        )
        if existing_instance is not None:
            return Err(
                BacnetObjectInstanceConflictError(
                    f"BACnet object with type '{command.object_type.value}' and "
                    f"instance {command.object_instance} already exists on this field device"
                )
            )

        existing_name = await self.object_repository.get_by_device_and_name(
            command.device_id, name
        )
        if existing_name is not None:
            return Err(
                BacnetObjectNameConflictError(
                    f"BACnet object with name '{name.value}' "
                    "already exists on this field device"
                )
            )

        obj = BacnetObject(
            id=new_id(BacnetObjectId),
            device_id=command.device_id,
            object_type=command.object_type,
            object_instance=command.object_instance,
            name=name.value,
            description=command.description,
            created_at=self.clock.now(),
        )
        created = await self.object_repository.create(obj)
        return Ok(created)

    async def get_object(
        self, query: GetBacnetObjectQuery
    ) -> Result[BacnetObject, BacnetObjectNotFoundError]:
        obj = await self.object_repository.get_by_id(query.object_id)
        if obj is None or obj.device_id != query.device_id:
            return Err(
                BacnetObjectNotFoundError(f"BACnet object '{query.object_id}' was not found")
            )
        return Ok(obj)

    async def list_objects(self, query: ListBacnetObjectsQuery) -> Page[BacnetObject]:
        items, total = await self.object_repository.list_page(query.device_id, query.page)
        return Page[BacnetObject](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def update_object(
        self, command: UpdateBacnetObjectCommand
    ) -> Result[
        BacnetObject,
        BacnetObjectNotFoundError
        | BacnetObjectInstanceConflictError
        | BacnetObjectNameConflictError
        | InvalidBacnetObjectNameError
        | InvalidBacnetObjectInstanceError,
    ]:
        obj = await self.object_repository.get_by_id(command.object_id)
        if obj is None or obj.device_id != command.device_id:
            return Err(
                BacnetObjectNotFoundError(
                    f"BACnet object '{command.object_id}' was not found"
                )
            )

        # Resolve updated type and instance
        new_type = command.object_type if command.object_type is not None else obj.object_type
        new_instance = (
            command.object_instance
            if command.object_instance is not None
            else obj.object_instance
        )

        if command.object_instance is not None:
            try:
                BacnetObjectInstance.parse(command.object_instance)
            except InvalidBacnetObjectInstanceError as exc:
                return Err(exc)

        type_or_instance_changed = (
            new_type != obj.object_type or new_instance != obj.object_instance
        )
        if type_or_instance_changed:
            existing_instance = await self.object_repository.get_by_device_type_instance(
                command.device_id, new_type, new_instance
            )
            if existing_instance is not None:
                return Err(
                    BacnetObjectInstanceConflictError(
                        f"BACnet object with type '{new_type.value}' and "
                        f"instance {new_instance} already exists on this field device"
                    )
                )

        name_value = obj.name
        if command.name is not None:
            try:
                name = BacnetObjectName.parse(command.name)
                name_value = name.value
            except InvalidBacnetObjectNameError as exc:
                return Err(exc)

            if name_value != obj.name:
                existing_name = await self.object_repository.get_by_device_and_name(
                    command.device_id,
                    BacnetObjectName(name_value),
                )
                if existing_name is not None:
                    return Err(
                        BacnetObjectNameConflictError(
                            f"BACnet object with name '{name_value}' "
                            "already exists on this field device"
                        )
                    )

        description = command.description if command.description is not None else obj.description

        updated_obj = BacnetObject(
            id=obj.id,
            device_id=obj.device_id,
            object_type=new_type,
            object_instance=new_instance,
            name=name_value,
            description=description,
            created_at=obj.created_at,
        )
        updated = await self.object_repository.update(updated_obj)
        return Ok(updated)

    async def delete_object(
        self, device_id: FieldDeviceId, object_id: BacnetObjectId
    ) -> Result[None, BacnetObjectNotFoundError]:
        obj = await self.object_repository.get_by_id(object_id)
        if obj is None or obj.device_id != device_id:
            return Err(BacnetObjectNotFoundError(f"BACnet object '{object_id}' was not found"))

        await self.object_repository.delete(object_id)
        return Ok(None)
