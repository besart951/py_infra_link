from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import BuildingId, FacilityId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class GetBuildingQuery:
    facility_id: FacilityId
    building_id: BuildingId


@dataclass(frozen=True, slots=True)
class ListBuildingsQuery:
    facility_id: FacilityId
    page: PageParams
