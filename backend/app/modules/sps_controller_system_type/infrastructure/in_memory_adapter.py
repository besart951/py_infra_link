from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.sps_controller_system_type.domain.models import SpsControllerSystemType
from app.modules.sps_controller_system_type.domain.value_objects import SpsControllerSystemTypeName
from app.shared.ids import SpsControllerSystemTypeId
from app.shared.pagination import PageParams


def _system_type_store() -> dict[SpsControllerSystemTypeId, SpsControllerSystemType]:
    return {}


@dataclass(frozen=True, slots=True)
class InMemorySpsControllerSystemTypeAdapter:
    _system_types: dict[SpsControllerSystemTypeId, SpsControllerSystemType] = field(
        default_factory=_system_type_store
    )

    async def get_by_id(
        self, system_type_id: SpsControllerSystemTypeId
    ) -> SpsControllerSystemType | None:
        return self._system_types.get(system_type_id)

    async def get_by_name(
        self, name: SpsControllerSystemTypeName
    ) -> SpsControllerSystemType | None:
        for system_type in self._system_types.values():
            if system_type.name == name.value:
                return system_type
        return None

    async def create(self, system_type: SpsControllerSystemType) -> SpsControllerSystemType:
        self._system_types[system_type.id] = system_type
        return system_type

    async def update(self, system_type: SpsControllerSystemType) -> SpsControllerSystemType:
        self._system_types[system_type.id] = system_type
        return system_type

    async def delete(self, system_type_id: SpsControllerSystemTypeId) -> None:
        self._system_types.pop(system_type_id, None)

    async def list_page(self, params: PageParams) -> tuple[list[SpsControllerSystemType], int]:
        all_items = sorted(
            self._system_types.values(), key=lambda s: s.created_at, reverse=True
        )
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total
