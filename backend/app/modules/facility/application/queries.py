from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import FacilityId
from app.shared.pagination import PageParams


@dataclass(frozen=True, slots=True)
class GetFacilityQuery:
    facility_id: FacilityId


@dataclass(frozen=True, slots=True)
class ListFacilitiesQuery:
    page: PageParams
