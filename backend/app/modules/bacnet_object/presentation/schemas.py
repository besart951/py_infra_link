from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.modules.bacnet_object.domain.value_objects import BacnetObjectType


class BacnetObjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    device_id: UUID
    object_type: BacnetObjectType
    object_instance: int
    name: str
    description: str | None
    created_at: datetime


class BacnetObjectCreate(BaseModel):
    object_type: BacnetObjectType
    object_instance: int = Field(..., ge=0)
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class BacnetObjectUpdate(BaseModel):
    object_type: BacnetObjectType | None = None
    object_instance: int | None = Field(None, ge=0)
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
