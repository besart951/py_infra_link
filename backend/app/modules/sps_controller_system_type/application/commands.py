from __future__ import annotations

from dataclasses import dataclass

from app.shared.ids import SpsControllerSystemTypeId


@dataclass(frozen=True, slots=True)
class CreateSpsControllerSystemTypeCommand:
    name: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateSpsControllerSystemTypeCommand:
    system_type_id: SpsControllerSystemTypeId
    name: str | None = None
    description: str | None = None
