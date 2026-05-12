from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ProjectOrm(Base):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(index=True)

    __table_args__ = (
        UniqueConstraint("owner_id", "name", name="uq_projects_owner_name"),
    )
