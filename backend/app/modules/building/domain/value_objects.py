from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.modules.building.domain.errors import InvalidBuildingNameError


@dataclass(frozen=True, slots=True)
class BuildingName:
    value: str

    @classmethod
    def parse(cls, value: str) -> Self:
        name = value.strip()
        if not name:
            raise InvalidBuildingNameError("Building name cannot be empty")
        if len(name) > 100:
            raise InvalidBuildingNameError("Building name cannot exceed 100 characters")
        return cls(name)

    def __str__(self) -> str:
        return self.value
