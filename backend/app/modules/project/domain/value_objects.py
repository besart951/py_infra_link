from __future__ import annotations

from dataclasses import dataclass
from typing import Self

from app.modules.project.domain.errors import InvalidProjectNameError


@dataclass(frozen=True, slots=True)
class ProjectName:
    value: str

    @classmethod
    def parse(cls, value: str) -> Self:
        name = value.strip()
        if not name:
            raise InvalidProjectNameError("Project name cannot be empty")
        if len(name) > 100:
            raise InvalidProjectNameError("Project name cannot exceed 100 characters")
        return cls(name)

    def __str__(self) -> str:
        return self.value
