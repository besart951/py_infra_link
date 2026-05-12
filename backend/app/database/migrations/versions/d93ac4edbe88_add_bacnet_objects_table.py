"""add_bacnet_objects_table

Revision ID: d93ac4edbe88
Revises: c93ac4edbe87
Create Date: 2026-05-12 09:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d93ac4edbe88"
down_revision: str | Sequence[str] | None = "c93ac4edbe87"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "bacnet_objects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("object_type", sa.String(length=50), nullable=False),
        sa.Column("object_instance", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["device_id"], ["field_devices.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "device_id",
            "object_type",
            "object_instance",
            name="uq_bacnet_objects_device_type_instance",
        ),
        sa.UniqueConstraint("device_id", "name", name="uq_bacnet_objects_device_name"),
    )
    op.create_index(
        op.f("ix_bacnet_objects_device_id"), "bacnet_objects", ["device_id"], unique=False
    )
    op.create_index(
        op.f("ix_bacnet_objects_object_type"), "bacnet_objects", ["object_type"], unique=False
    )
    op.create_index(
        op.f("ix_bacnet_objects_object_instance"),
        "bacnet_objects",
        ["object_instance"],
        unique=False,
    )
    op.create_index(op.f("ix_bacnet_objects_name"), "bacnet_objects", ["name"], unique=False)
    op.create_index(
        op.f("ix_bacnet_objects_created_at"), "bacnet_objects", ["created_at"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_bacnet_objects_created_at"), table_name="bacnet_objects")
    op.drop_index(op.f("ix_bacnet_objects_name"), table_name="bacnet_objects")
    op.drop_index(op.f("ix_bacnet_objects_object_instance"), table_name="bacnet_objects")
    op.drop_index(op.f("ix_bacnet_objects_object_type"), table_name="bacnet_objects")
    op.drop_index(op.f("ix_bacnet_objects_device_id"), table_name="bacnet_objects")
    op.drop_table("bacnet_objects")
