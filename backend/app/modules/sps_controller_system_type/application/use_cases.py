from __future__ import annotations

from app.modules.sps_controller_system_type.application.commands import (
    CreateSpsControllerSystemTypeCommand,
    UpdateSpsControllerSystemTypeCommand,
)
from app.modules.sps_controller_system_type.application.queries import (
    GetSpsControllerSystemTypeQuery,
    ListSpsControllerSystemTypesQuery,
)
from app.modules.sps_controller_system_type.domain.errors import (
    InvalidSpsControllerSystemTypeNameError,
    SpsControllerSystemTypeNameConflictError,
    SpsControllerSystemTypeNotFoundError,
)
from app.modules.sps_controller_system_type.domain.interface import (
    SpsControllerSystemTypeRepository,
)
from app.modules.sps_controller_system_type.domain.models import SpsControllerSystemType
from app.modules.sps_controller_system_type.domain.value_objects import SpsControllerSystemTypeName
from app.shared.clock import Clock
from app.shared.ids import SpsControllerSystemTypeId, new_id
from app.shared.pagination import Page
from app.shared.result import Err, Ok, Result


class SpsControllerSystemTypeModule:
    def __init__(self, repository: SpsControllerSystemTypeRepository, clock: Clock) -> None:
        self._repository = repository
        self._clock = clock

    async def create_system_type(
        self, command: CreateSpsControllerSystemTypeCommand
    ) -> Result[
        SpsControllerSystemType,
        SpsControllerSystemTypeNameConflictError | InvalidSpsControllerSystemTypeNameError,
    ]:
        try:
            name = SpsControllerSystemTypeName.parse(command.name)
        except InvalidSpsControllerSystemTypeNameError as exc:
            return Err(exc)

        existing = await self._repository.get_by_name(name)
        if existing is not None:
            return Err(
                SpsControllerSystemTypeNameConflictError(
                    f"SPS controller system type with name '{name.value}' already exists"
                )
            )

        system_type = SpsControllerSystemType(
            id=new_id(SpsControllerSystemTypeId),
            name=name.value,
            description=command.description,
            created_at=self._clock.now(),
        )
        created = await self._repository.create(system_type)
        return Ok(created)

    async def get_system_type(
        self, query: GetSpsControllerSystemTypeQuery
    ) -> Result[SpsControllerSystemType, SpsControllerSystemTypeNotFoundError]:
        system_type = await self._repository.get_by_id(query.system_type_id)
        if system_type is None:
            return Err(
                SpsControllerSystemTypeNotFoundError(
                    f"SPS controller system type '{query.system_type_id}' was not found"
                )
            )
        return Ok(system_type)

    async def list_system_types(
        self, query: ListSpsControllerSystemTypesQuery
    ) -> Page[SpsControllerSystemType]:
        items, total = await self._repository.list_page(query.page)
        return Page[SpsControllerSystemType](
            items=items,
            total=total,
            page=query.page.page,
            size=query.page.size,
        )

    async def update_system_type(
        self, command: UpdateSpsControllerSystemTypeCommand
    ) -> Result[
        SpsControllerSystemType,
        SpsControllerSystemTypeNotFoundError
        | SpsControllerSystemTypeNameConflictError
        | InvalidSpsControllerSystemTypeNameError,
    ]:
        system_type = await self._repository.get_by_id(command.system_type_id)
        if system_type is None:
            return Err(
                SpsControllerSystemTypeNotFoundError(
                    f"SPS controller system type '{command.system_type_id}' was not found"
                )
            )

        name_value = system_type.name
        if command.name is not None:
            try:
                name = SpsControllerSystemTypeName.parse(command.name)
                name_value = name.value
            except InvalidSpsControllerSystemTypeNameError as exc:
                return Err(exc)

            if name_value != system_type.name:
                existing = await self._repository.get_by_name(name)
                if existing is not None:
                    return Err(
                        SpsControllerSystemTypeNameConflictError(
                            f"SPS controller system type with name '{name.value}' already exists"
                        )
                    )

        description = (
            command.description if command.description is not None else system_type.description
        )

        updated_system_type = SpsControllerSystemType(
            id=system_type.id,
            name=name_value,
            description=description,
            created_at=system_type.created_at,
        )
        updated = await self._repository.update(updated_system_type)
        return Ok(updated)

    async def delete_system_type(
        self, system_type_id: SpsControllerSystemTypeId
    ) -> Result[None, SpsControllerSystemTypeNotFoundError]:
        system_type = await self._repository.get_by_id(system_type_id)
        if system_type is None:
            return Err(
                SpsControllerSystemTypeNotFoundError(
                    f"SPS controller system type '{system_type_id}' was not found"
                )
            )

        await self._repository.delete(system_type_id)
        return Ok(None)
