from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class BacnetObjectOrm(Base):
    __tablename__ = "bacnet_objects"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    device_id: Mapped[UUID] = mapped_column(ForeignKey("field_devices.id"), index=True)
    object_type: Mapped[str] = mapped_column(String(50), index=True)
    object_instance: Mapped[int] = mapped_column(Integer, index=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    __table_args__ = (
        UniqueConstraint(
            "device_id",
            "object_type",
            "object_instance",
            name="uq_bacnet_objects_device_type_instance",
        ),
        UniqueConstraint("device_id", "name", name="uq_bacnet_objects_device_name"),
    )
