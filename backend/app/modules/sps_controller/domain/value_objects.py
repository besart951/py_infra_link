from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.modules.sps_controller.domain.errors import InvalidSpsControllerNameError


@dataclass(frozen=True, slots=True)
class SpsControllerName:
    value: str

    @classmethod
    def parse(cls, value: str) -> Self:
        name = value.strip()
        if not name:
            raise InvalidSpsControllerNameError("SPS controller name cannot be empty")
        if len(name) > 100:
            raise InvalidSpsControllerNameError("SPS controller name cannot exceed 100 characters")
        return cls(name)

    def __str__(self) -> str:
        return self.value
