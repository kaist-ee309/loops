"""Add total_study_time_minutes to user

Revision ID: f1a2b3c4d5e6
Revises: eccc1f1a2c21
Create Date: 2025-12-04 10:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f1a2b3c4d5e6"
down_revision: str | Sequence[str] | None = "eccc1f1a2c21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("total_study_time_minutes", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "total_study_time_minutes")
