"""add_sps_controller_system_types_table

Revision ID: a93ac4edbe85
Revises: c93ac4edbe84
Create Date: 2026-05-11 23:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a93ac4edbe85"
down_revision: str | Sequence[str] | None = "c93ac4edbe84"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "sps_controller_system_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_sps_controller_system_types_name"),
    )
    op.create_index(
        op.f("ix_sps_controller_system_types_name"),
        "sps_controller_system_types",
        ["name"],
        unique=True,
    )
    op.create_index(
        op.f("ix_sps_controller_system_types_created_at"),
        "sps_controller_system_types",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_sps_controller_system_types_created_at"), table_name="sps_controller_system_types"
    )
    op.drop_index(
        op.f("ix_sps_controller_system_types_name"), table_name="sps_controller_system_types"
    )
    op.drop_table("sps_controller_system_types")
