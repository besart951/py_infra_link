from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class FieldDeviceOrm(Base):
    __tablename__ = "field_devices"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    controller_id: Mapped[UUID] = mapped_column(ForeignKey("sps_controllers.id"), index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(index=True)

    __table_args__ = (
        UniqueConstraint("controller_id", "name", name="uq_field_devices_controller_name"),
    )
