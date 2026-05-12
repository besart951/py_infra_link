from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.modules.field_device.domain.errors import InvalidFieldDeviceNameError


@dataclass(frozen=True, slots=True)
class FieldDeviceName:
    value: str

    @classmethod
    def parse(cls, value: str) -> Self:
        name = value.strip()
        if not name:
            raise InvalidFieldDeviceNameError("Field device name cannot be empty")
        if len(name) > 100:
            raise InvalidFieldDeviceNameError("Field device name cannot exceed 100 characters")
        return cls(name)

    def __str__(self) -> str:
        return self.value
