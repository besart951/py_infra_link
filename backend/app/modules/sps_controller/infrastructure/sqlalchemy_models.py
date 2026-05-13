from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class SpsControllerOrm(Base):
    __tablename__ = "sps_controllers"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    cabinet_id: Mapped[UUID] = mapped_column(ForeignKey("control_cabinets.id"), index=True)
    system_type_id: Mapped[UUID] = mapped_column(
        ForeignKey("sps_controller_system_types.id"), index=True
    )
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    __table_args__ = (
        UniqueConstraint("cabinet_id", "name", name="uq_sps_controllers_cabinet_name"),
    )
