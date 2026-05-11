from __future__ import annotations

from app.modules.sps_controller.domain.models import SpsController
from app.modules.sps_controller.domain.value_objects import SpsControllerName
from app.shared.ids import ControlCabinetId, SpsControllerId
from app.shared.pagination import PageParams


class InMemorySpsControllerAdapter:
    def __init__(self) -> None:
        self._controllers: dict[SpsControllerId, SpsController] = {}

    async def get_by_id(self, controller_id: SpsControllerId) -> SpsController | None:
        return self._controllers.get(controller_id)

    async def get_by_cabinet_and_name(
        self, cabinet_id: ControlCabinetId, name: SpsControllerName
    ) -> SpsController | None:
        for controller in self._controllers.values():
            if controller.cabinet_id == cabinet_id and controller.name == name.value:
                return controller
        return None

    async def create(self, controller: SpsController) -> SpsController:
        self._controllers[controller.id] = controller
        return controller

    async def update(self, controller: SpsController) -> SpsController:
        self._controllers[controller.id] = controller
        return controller

    async def delete(self, controller_id: SpsControllerId) -> None:
        self._controllers.pop(controller_id, None)

    async def list_page(
        self, cabinet_id: ControlCabinetId, params: PageParams
    ) -> tuple[list[SpsController], int]:
        all_items = sorted(
            [c for c in self._controllers.values() if c.cabinet_id == cabinet_id],
            key=lambda c: c.created_at,
            reverse=True,
        )
        total = len(all_items)
        items = all_items[params.offset : params.offset + params.size]
        return list(items), total
