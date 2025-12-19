"""Add highlight_color to profiles

Revision ID: a2b3c4d5e6f7
Revises: 1da20884d6da
Create Date: 2025-12-13 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a2b3c4d5e6f7"
down_revision: str | Sequence[str] | None = "5e0888ee7d18"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "profiles",
        sa.Column(
            "highlight_color",
            sa.String(length=20),
            nullable=False,
            server_default="#4CAF50",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("profiles", "highlight_color")
