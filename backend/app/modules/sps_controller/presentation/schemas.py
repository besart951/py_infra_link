from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SpsControllerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    cabinet_id: UUID
    system_type_id: UUID
    name: str
    description: str | None
    created_at: datetime


class SpsControllerCreate(BaseModel):
    system_type_id: UUID
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class SpsControllerUpdate(BaseModel):
    system_type_id: UUID | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
