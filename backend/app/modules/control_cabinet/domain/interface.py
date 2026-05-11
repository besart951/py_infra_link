from __future__ import annotations

from typing import Protocol

from app.modules.control_cabinet.domain.models import ControlCabinet
from app.modules.control_cabinet.domain.value_objects import ControlCabinetName
from app.shared.ids import BuildingId, ControlCabinetId
from app.shared.pagination import PageParams


class ControlCabinetRepository(Protocol):
    async def get_by_id(self, cabinet_id: ControlCabinetId) -> ControlCabinet | None: ...

    async def get_by_building_and_name(
        self, building_id: BuildingId, name: ControlCabinetName
    ) -> ControlCabinet | None: ...

    async def create(self, cabinet: ControlCabinet) -> ControlCabinet: ...

    async def update(self, cabinet: ControlCabinet) -> ControlCabinet: ...

    async def delete(self, cabinet_id: ControlCabinetId) -> None: ...

    async def list_page(
        self, building_id: BuildingId, params: PageParams
    ) -> tuple[list[ControlCabinet], int]: ...
