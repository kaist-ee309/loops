"""add image fields to vocabulary_cards

Revision ID: 9f8e7d6c5b4a
Revises: 4c5d6e7f8g9h, 5e0888ee7d18, a2b3c4d5e6f7
Create Date: 2025-12-13

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9f8e7d6c5b4a"
down_revision: str | Sequence[str] | None = (
    "4c5d6e7f8g9h",
    "5e0888ee7d18",
    "a2b3c4d5e6f7",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add image association columns to vocabulary_cards."""
    op.add_column(
        "vocabulary_cards",
        sa.Column("image_url", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "vocabulary_cards",
        sa.Column("image_storage_path", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "vocabulary_cards",
        sa.Column("image_prompt", sa.Text(), nullable=True),
    )
    op.add_column(
        "vocabulary_cards",
        sa.Column("image_model", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "vocabulary_cards",
        sa.Column("image_status", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "vocabulary_cards",
        sa.Column("image_error", sa.Text(), nullable=True),
    )
    op.add_column(
        "vocabulary_cards",
        sa.Column("image_generated_at", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    """Remove image association columns from vocabulary_cards."""
    op.drop_column("vocabulary_cards", "image_generated_at")
    op.drop_column("vocabulary_cards", "image_error")
    op.drop_column("vocabulary_cards", "image_status")
    op.drop_column("vocabulary_cards", "image_model")
    op.drop_column("vocabulary_cards", "image_prompt")
    op.drop_column("vocabulary_cards", "image_storage_path")
    op.drop_column("vocabulary_cards", "image_url")
