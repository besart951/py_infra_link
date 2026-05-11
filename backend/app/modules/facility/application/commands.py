from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import FacilityId


@dataclass(frozen=True, slots=True)
class CreateFacilityCommand:
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateFacilityCommand:
    facility_id: FacilityId
    name: str | None = None
    description: str | None = None
