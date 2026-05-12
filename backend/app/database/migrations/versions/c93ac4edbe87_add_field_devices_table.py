"""add_field_devices_table

Revision ID: c93ac4edbe87
Revises: b93ac4edbe86
Create Date: 2026-05-12 08:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c93ac4edbe87"
down_revision: str | Sequence[str] | None = "b93ac4edbe86"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "field_devices",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("controller_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["controller_id"], ["sps_controllers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("controller_id", "name", name="uq_field_devices_controller_name"),
    )
    op.create_index(
        op.f("ix_field_devices_controller_id"), "field_devices", ["controller_id"], unique=False
    )
    op.create_index(op.f("ix_field_devices_name"), "field_devices", ["name"], unique=False)
    op.create_index(
        op.f("ix_field_devices_created_at"), "field_devices", ["created_at"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_field_devices_created_at"), table_name="field_devices")
    op.drop_index(op.f("ix_field_devices_name"), table_name="field_devices")
    op.drop_index(op.f("ix_field_devices_controller_id"), table_name="field_devices")
    op.drop_table("field_devices")
