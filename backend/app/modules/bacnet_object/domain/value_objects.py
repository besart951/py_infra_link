from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Self

from app.modules.bacnet_object.domain.errors import (
    InvalidBacnetObjectInstanceError,
    InvalidBacnetObjectNameError,
)


class BacnetObjectType(StrEnum):
    """BACnet standard object types supported by the system."""

    ANALOG_INPUT = "AnalogInput"
    ANALOG_OUTPUT = "AnalogOutput"
    ANALOG_VALUE = "AnalogValue"
    BINARY_INPUT = "BinaryInput"
    BINARY_OUTPUT = "BinaryOutput"
    BINARY_VALUE = "BinaryValue"
    MULTI_STATE_INPUT = "MultiStateInput"
    MULTI_STATE_OUTPUT = "MultiStateOutput"
    MULTI_STATE_VALUE = "MultiStateValue"


@dataclass(frozen=True, slots=True)
class BacnetObjectName:
    value: str

    @classmethod
    def parse(cls, value: str) -> Self:
        name = value.strip()
        if not name:
            raise InvalidBacnetObjectNameError("BACnet object name cannot be empty")
        if len(name) > 100:
            raise InvalidBacnetObjectNameError("BACnet object name cannot exceed 100 characters")
        return cls(name)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class BacnetObjectInstance:
    value: int

    @classmethod
    def parse(cls, value: int) -> Self:
        if value < 0:
            raise InvalidBacnetObjectInstanceError(
                "BACnet object instance must be a non-negative integer"
            )
        return cls(value)
