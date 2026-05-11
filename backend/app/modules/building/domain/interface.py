from __future__ import annotations

from typing import Protocol

from app.modules.building.domain.models import Building
from app.modules.building.domain.value_objects import BuildingName
from app.shared.ids import BuildingId, FacilityId
from app.shared.pagination import PageParams


class BuildingRepository(Protocol):
    async def get_by_id(self, building_id: BuildingId) -> Building | None: ...

    async def get_by_facility_and_name(
        self, facility_id: FacilityId, name: BuildingName
    ) -> Building | None: ...

    async def create(self, building: Building) -> Building: ...

    async def update(self, building: Building) -> Building: ...

    async def delete(self, building_id: BuildingId) -> None: ...

    async def list_page(
        self, facility_id: FacilityId, params: PageParams
    ) -> tuple[list[Building], int]: ...
