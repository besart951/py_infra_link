from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.modules.facility.domain.errors import InvalidFacilityNameError


@dataclass(frozen=True, slots=True)
class FacilityName:
    value: str

    @classmethod
    def parse(cls, value: str) -> Self:
        name = value.strip()
        if not name:
            raise InvalidFacilityNameError("Facility name cannot be empty")
        if len(name) > 100:
            raise InvalidFacilityNameError("Facility name cannot exceed 100 characters")
        return cls(name)

    def __str__(self) -> str:
        return self.value
