from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BuildingOrm(Base):
    __tablename__ = "buildings"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    facility_id: Mapped[UUID] = mapped_column(ForeignKey("facilities.id"), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(index=True)

    __table_args__ = (UniqueConstraint("facility_id", "name", name="uq_buildings_facility_name"),)
