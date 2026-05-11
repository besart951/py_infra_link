"""add_buildings_table

Revision ID: b93ac4edbe83
Revises: e73ac4edbe82
Create Date: 2026-05-11 22:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b93ac4edbe83"
down_revision: str | Sequence[str] | None = "e73ac4edbe82"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "buildings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("facility_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["facility_id"], ["facilities.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("facility_id", "name", name="uq_buildings_facility_name"),
    )
    op.create_index(op.f("ix_buildings_facility_id"), "buildings", ["facility_id"], unique=False)
    op.create_index(op.f("ix_buildings_name"), "buildings", ["name"], unique=False)
    op.create_index(op.f("ix_buildings_created_at"), "buildings", ["created_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_buildings_created_at"), table_name="buildings")
    op.drop_index(op.f("ix_buildings_name"), table_name="buildings")
    op.drop_index(op.f("ix_buildings_facility_id"), table_name="buildings")
    op.drop_table("buildings")
