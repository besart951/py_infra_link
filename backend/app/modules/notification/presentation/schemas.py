from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    body: str
    is_read: bool
    created_at: datetime


class MarkAllReadResponse(BaseModel):
    marked: int
