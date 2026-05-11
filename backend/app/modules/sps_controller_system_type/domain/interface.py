from __future__ import annotations

from typing import Protocol

from app.modules.sps_controller_system_type.domain.models import SpsControllerSystemType
from app.modules.sps_controller_system_type.domain.value_objects import SpsControllerSystemTypeName
from app.shared.ids import SpsControllerSystemTypeId
from app.shared.pagination import PageParams


class SpsControllerSystemTypeRepository(Protocol):
    async def get_by_id(
        self, system_type_id: SpsControllerSystemTypeId
    ) -> SpsControllerSystemType | None: ...

    async def get_by_name(
        self, name: SpsControllerSystemTypeName
    ) -> SpsControllerSystemType | None: ...

    async def create(self, system_type: SpsControllerSystemType) -> SpsControllerSystemType: ...

    async def update(self, system_type: SpsControllerSystemType) -> SpsControllerSystemType: ...

    async def delete(self, system_type_id: SpsControllerSystemTypeId) -> None: ...

    async def list_page(self, params: PageParams) -> tuple[list[SpsControllerSystemType], int]: ...
