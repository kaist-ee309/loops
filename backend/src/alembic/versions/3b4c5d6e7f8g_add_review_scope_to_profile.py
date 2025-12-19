"""add review_scope to profile

Revision ID: 3b4c5d6e7f8g
Revises: 2a3b4c5d6e7f
Create Date: 2025-12-13 13:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3b4c5d6e7f8g"
down_revision: str | Sequence[str] | None = "2a3b4c5d6e7f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add review_scope column
    op.add_column(
        "profiles",
        sa.Column(
            "review_scope",
            sa.String(length=30),
            nullable=False,
            server_default="selected_decks_only",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("profiles", "review_scope")
