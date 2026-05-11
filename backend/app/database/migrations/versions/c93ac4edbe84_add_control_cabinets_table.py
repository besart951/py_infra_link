"""add_control_cabinets_table

Revision ID: c93ac4edbe84
Revises: b93ac4edbe83
Create Date: 2026-05-11 22:30:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "c93ac4edbe84"
down_revision: str | Sequence[str] | None = "b93ac4edbe83"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "control_cabinets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("building_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["building_id"], ["buildings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("building_id", "name", name="uq_control_cabinets_building_name"),
    )
    op.create_index(
        op.f("ix_control_cabinets_building_id"), "control_cabinets", ["building_id"], unique=False
    )
    op.create_index(op.f("ix_control_cabinets_name"), "control_cabinets", ["name"], unique=False)
    op.create_index(
        op.f("ix_control_cabinets_created_at"), "control_cabinets", ["created_at"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_control_cabinets_created_at"), table_name="control_cabinets")
    op.drop_index(op.f("ix_control_cabinets_name"), table_name="control_cabinets")
    op.drop_index(op.f("ix_control_cabinets_building_id"), table_name="control_cabinets")
    op.drop_table("control_cabinets")
