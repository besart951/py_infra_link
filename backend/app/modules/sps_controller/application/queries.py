from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import ControlCabinetId, SpsControllerId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class GetSpsControllerQuery:
    cabinet_id: ControlCabinetId
    controller_id: SpsControllerId


@dataclass(frozen=True, slots=True)
class ListSpsControllersQuery:
    cabinet_id: ControlCabinetId
    page: PageParams
