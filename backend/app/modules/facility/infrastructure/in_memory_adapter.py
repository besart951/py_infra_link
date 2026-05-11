from __future__ import annotations

from app.modules.facility.domain.models import Facility
from app.modules.facility.domain.value_objects import FacilityName
from app.shared.ids import FacilityId
from app.shared.pagination import PageParams


class InMemoryFacilityAdapter:
    def __init__(self) -> None:
        self._facilities: dict[FacilityId, Facility] = {}

    async def get_by_id(self, facility_id: FacilityId) -> Facility | None:
        return self._facilities.get(facility_id)

    async def get_by_name(self, name: FacilityName) -> Facility | None:
        for facility in self._facilities.values():
            if facility.name == name.value:
                return facility
        return None

    async def create(self, facility: Facility) -> Facility:
        self._facilities[facility.id] = facility
        return facility

    async def update(self, facility: Facility) -> Facility:
        self._facilities[facility.id] = facility
        return facility

    async def delete(self, facility_id: FacilityId) -> None:
        self._facilities.pop(facility_id, None)

    async def list_page(self, params: PageParams) -> tuple[list[Facility], int]:
        all_items = sorted(self._facilities.values(), key=lambda f: f.created_at, reverse=True)
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total
