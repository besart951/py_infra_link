"""add_sps_controllers_table

Revision ID: b93ac4edbe86
Revises: a93ac4edbe85
Create Date: 2026-05-11 23:30:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b93ac4edbe86"
down_revision: str | Sequence[str] | None = "a93ac4edbe85"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sps_controllers",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cabinet_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("system_type_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["cabinet_id"], ["control_cabinets.id"]),
        sa.ForeignKeyConstraint(["system_type_id"], ["sps_controller_system_types.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cabinet_id", "name", name="uq_sps_controllers_cabinet_name"),
    )
    op.create_index(
        op.f("ix_sps_controllers_cabinet_id"), "sps_controllers", ["cabinet_id"], unique=False
    )
    op.create_index(
        op.f("ix_sps_controllers_system_type_id"),
        "sps_controllers",
        ["system_type_id"],
        unique=False,
    )
    op.create_index(op.f("ix_sps_controllers_name"), "sps_controllers", ["name"], unique=False)
    op.create_index(
        op.f("ix_sps_controllers_created_at"), "sps_controllers", ["created_at"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_sps_controllers_created_at"), table_name="sps_controllers")
    op.drop_index(op.f("ix_sps_controllers_name"), table_name="sps_controllers")
    op.drop_index(op.f("ix_sps_controllers_system_type_id"), table_name="sps_controllers")
    op.drop_index(op.f("ix_sps_controllers_cabinet_id"), table_name="sps_controllers")
    op.drop_table("sps_controllers")
