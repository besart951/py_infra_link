from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.control_cabinet.domain.models import ControlCabinet
from app.modules.control_cabinet.domain.value_objects import ControlCabinetName
from app.shared.ids import BuildingId, ControlCabinetId
from app.shared.pagination import PageParams


def _cabinet_store() -> dict[ControlCabinetId, ControlCabinet]:
    return {}


@dataclass(frozen=True, slots=True)
class InMemoryControlCabinetAdapter:
    _cabinets: dict[ControlCabinetId, ControlCabinet] = field(default_factory=_cabinet_store)

    async def get_by_id(self, cabinet_id: ControlCabinetId) -> ControlCabinet | None:
        return self._cabinets.get(cabinet_id)

    async def get_by_building_and_name(
        self, building_id: BuildingId, name: ControlCabinetName
    ) -> ControlCabinet | None:
        for cabinet in self._cabinets.values():
            if cabinet.building_id == building_id and cabinet.name == name.value:
                return cabinet
        return None

    async def create(self, cabinet: ControlCabinet) -> ControlCabinet:
        self._cabinets[cabinet.id] = cabinet
        return cabinet

    async def update(self, cabinet: ControlCabinet) -> ControlCabinet:
        self._cabinets[cabinet.id] = cabinet
        return cabinet

    async def delete(self, cabinet_id: ControlCabinetId) -> None:
        self._cabinets.pop(cabinet_id, None)

    async def list_page(
        self, building_id: BuildingId, params: PageParams
    ) -> tuple[list[ControlCabinet], int]:
        all_items = sorted(
            [c for c in self._cabinets.values() if c.building_id == building_id],
            key=lambda c: c.created_at,
            reverse=True,
        )
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total
