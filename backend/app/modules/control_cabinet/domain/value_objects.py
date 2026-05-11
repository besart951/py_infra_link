from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.modules.control_cabinet.domain.errors import InvalidControlCabinetNameError


@dataclass(frozen=True, slots=True)
class ControlCabinetName:
    value: str

    @classmethod
    def parse(cls, value: str) -> Self:
        name = value.strip()
        if not name:
            raise InvalidControlCabinetNameError("Control cabinet name cannot be empty")
        if len(name) > 100:
            raise InvalidControlCabinetNameError(
                "Control cabinet name cannot exceed 100 characters"
            )
        return cls(name)

    def __str__(self) -> str:
        return self.value
