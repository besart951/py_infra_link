from __future__ import annotations

from typing import Protocol

from app.modules.sps_controller.domain.models import SpsController
from app.modules.sps_controller.domain.value_objects import SpsControllerName
from app.shared.ids import ControlCabinetId, SpsControllerId
from app.shared.pagination import PageParams


class SpsControllerRepository(Protocol):
    async def get_by_id(self, controller_id: SpsControllerId) -> SpsController | None: ...

    async def get_by_cabinet_and_name(
        self, cabinet_id: ControlCabinetId, name: SpsControllerName
    ) -> SpsController | None: ...

    async def create(self, controller: SpsController) -> SpsController: ...

    async def update(self, controller: SpsController) -> SpsController: ...

    async def delete(self, controller_id: SpsControllerId) -> None: ...

    async def list_page(
        self, cabinet_id: ControlCabinetId, params: PageParams
    ) -> tuple[list[SpsController], int]: ...
