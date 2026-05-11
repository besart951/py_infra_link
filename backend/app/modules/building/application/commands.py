from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import BuildingId, FacilityId


@dataclass(frozen=True, slots=True)
class CreateBuildingCommand:
    facility_id: FacilityId
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateBuildingCommand:
    facility_id: FacilityId
    building_id: BuildingId
    name: str | None = None
    description: str | None = None
