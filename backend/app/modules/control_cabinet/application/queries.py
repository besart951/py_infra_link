from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import BuildingId, ControlCabinetId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class GetControlCabinetQuery:
    building_id: BuildingId
    cabinet_id: ControlCabinetId


@dataclass(frozen=True, slots=True)
class ListControlCabinetsQuery:
    building_id: BuildingId
    page: PageParams
