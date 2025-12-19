"""add review ratio settings to profile

Revision ID: 2a3b4c5d6e7f
Revises: 1da20884d6da
Create Date: 2025-12-13 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2a3b4c5d6e7f"
down_revision: str | Sequence[str] | None = "a2b3c4d5e6f7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add review_ratio_mode column
    op.add_column(
        "profiles",
        sa.Column(
            "review_ratio_mode",
            sa.String(length=20),
            nullable=False,
            server_default="normal",
        ),
    )
    # Add custom_review_ratio column
    op.add_column(
        "profiles",
        sa.Column(
            "custom_review_ratio",
            sa.Float(),
            nullable=False,
            server_default="0.75",
        ),
    )
    # Add min_new_ratio column
    op.add_column(
        "profiles",
        sa.Column(
            "min_new_ratio",
            sa.Float(),
            nullable=False,
            server_default="0.25",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("profiles", "min_new_ratio")
    op.drop_column("profiles", "custom_review_ratio")
    op.drop_column("profiles", "review_ratio_mode")
