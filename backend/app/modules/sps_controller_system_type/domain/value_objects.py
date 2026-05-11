from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.modules.sps_controller_system_type.domain.errors import (
    InvalidSpsControllerSystemTypeNameError,
)


@dataclass(frozen=True, slots=True)
class SpsControllerSystemTypeName:
    value: str

    @classmethod
    def parse(cls, value: str) -> Self:
        name = value.strip()
        if not name:
            raise InvalidSpsControllerSystemTypeNameError(
                "SPS controller system type name cannot be empty"
            )
        if len(name) > 100:
            raise InvalidSpsControllerSystemTypeNameError(
                "SPS controller system type name cannot exceed 100 characters"
            )
        return cls(name)

    def __str__(self) -> str:
        return self.value
