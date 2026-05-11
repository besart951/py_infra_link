"""baseline_empty_schema

Revision ID: f9f0b98a3e3a
Revises:
Create Date: 2026-05-11 18:07:14.114576

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "f9f0b98a3e3a"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
