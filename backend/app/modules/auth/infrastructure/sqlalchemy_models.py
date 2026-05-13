from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class UserCredentialRecord(Base):
    __tablename__ = "user_credentials"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )
    password_hash: Mapped[str] = mapped_column(String(72), nullable=False)
