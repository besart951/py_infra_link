"""add_project_resource_links_table

Revision ID: f93ac4edbe90
Revises: e93ac4edbe89
Create Date: 2026-05-12 11:00:00.000000

"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "f93ac4edbe90"
down_revision: str | Sequence[str] | None = "e93ac4edbe89"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "project_resource_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("resource_type", sa.String(length=30), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "linked_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "resource_type",
            "resource_id",
            name="uq_project_resource_links_project_type_resource",
        ),
    )
    op.create_index(
        op.f("ix_project_resource_links_project_id"),
        "project_resource_links",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_resource_links_resource_type"),
        "project_resource_links",
        ["resource_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_resource_links_resource_id"),
        "project_resource_links",
        ["resource_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_project_resource_links_linked_at"),
        "project_resource_links",
        ["linked_at"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        op.f("ix_project_resource_links_linked_at"),
        table_name="project_resource_links",
    )
    op.drop_index(
        op.f("ix_project_resource_links_resource_id"),
        table_name="project_resource_links",
    )
    op.drop_index(
        op.f("ix_project_resource_links_resource_type"),
        table_name="project_resource_links",
    )
    op.drop_index(
        op.f("ix_project_resource_links_project_id"),
        table_name="project_resource_links",
    )
    op.drop_table("project_resource_links")
