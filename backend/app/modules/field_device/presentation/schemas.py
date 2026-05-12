from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FieldDeviceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    controller_id: UUID
    name: str
    description: str | None
    created_at: datetime


class FieldDeviceCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class FieldDeviceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
