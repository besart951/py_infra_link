from __future__ import annotations

from dataclasses import dataclass, field

from app.modules.building.domain.models import Building
from app.modules.building.domain.value_objects import BuildingName
from app.shared.ids import BuildingId, FacilityId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class InMemoryBuildingAdapter:
    _buildings: dict[BuildingId, Building] = field(default_factory=dict)

    async def get_by_id(self, building_id: BuildingId) -> Building | None:
        return self._buildings.get(building_id)

    async def get_by_facility_and_name(
        self, facility_id: FacilityId, name: BuildingName
    ) -> Building | None:
        for building in self._buildings.values():
            if building.facility_id == facility_id and building.name == name.value:
                return building
        return None

    async def create(self, building: Building) -> Building:
        self._buildings[building.id] = building
        return building

    async def update(self, building: Building) -> Building:
        self._buildings[building.id] = building
        return building

    async def delete(self, building_id: BuildingId) -> None:
        self._buildings.pop(building_id, None)

    async def list_page(
        self, facility_id: FacilityId, params: PageParams
    ) -> tuple[list[Building], int]:
        all_items = sorted(
            [b for b in self._buildings.values() if b.facility_id == facility_id],
            key=lambda b: b.created_at,
            reverse=True,
        )
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total
