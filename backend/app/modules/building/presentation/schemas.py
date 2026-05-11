from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BuildingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    facility_id: UUID
    name: str
    description: str | None
    created_at: datetime


class BuildingCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class BuildingUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
