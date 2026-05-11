"""add_facilities_table

Revision ID: e73ac4edbe82
Revises: d72ac4edbe81
Create Date: 2026-05-11 21:30:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e73ac4edbe82"
down_revision: str | Sequence[str] | None = "d72ac4edbe81"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "facilities",
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
        sa.UniqueConstraint("name", name="uq_facilities_name"),
    )
    op.create_index(op.f("ix_facilities_name"), "facilities", ["name"], unique=False)
    op.create_index(op.f("ix_facilities_created_at"), "facilities", ["created_at"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_facilities_created_at"), table_name="facilities")
    op.drop_index(op.f("ix_facilities_name"), table_name="facilities")
    op.drop_table("facilities")
