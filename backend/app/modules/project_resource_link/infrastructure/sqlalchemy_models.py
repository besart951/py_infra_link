from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class ProjectResourceLinkOrm(Base):
    __tablename__ = "project_resource_links"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    project_id: Mapped[UUID] = mapped_column(ForeignKey("projects.id"), index=True)
    resource_type: Mapped[str] = mapped_column(String(30), index=True)
    resource_id: Mapped[UUID] = mapped_column(index=True)
    linked_at: Mapped[datetime] = mapped_column(index=True)

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "resource_type",
            "resource_id",
            name="uq_project_resource_links_project_type_resource",
        ),
    )
