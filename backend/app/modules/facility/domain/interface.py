from __future__ import annotations

from typing import Protocol

from app.modules.facility.domain.models import Facility
from app.modules.facility.domain.value_objects import FacilityName
from app.shared.ids import FacilityId
from app.shared.pagination import PageParams


class FacilityRepository(Protocol):
    async def get_by_id(self, facility_id: FacilityId) -> Facility | None: ...

    async def get_by_name(self, name: FacilityName) -> Facility | None: ...

    async def create(self, facility: Facility) -> Facility: ...

    async def update(self, facility: Facility) -> Facility: ...

    async def delete(self, facility_id: FacilityId) -> None: ...

    async def list_page(self, params: PageParams) -> tuple[list[Facility], int]: ...
