from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CreateUserRequest(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    display_name: str = Field(min_length=1, max_length=120)


class UserResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    id: str
    email: str
    display_name: str
    created_at: datetime


class UserPageResponse(BaseModel):
    model_config = ConfigDict(frozen=True)

    items: list[UserResponse]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool
