"""add related_words to vocabulary_cards

Revision ID: 4c5d6e7f8g9h
Revises: 3b4c5d6e7f8g
Create Date: 2025-12-13 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4c5d6e7f8g9h"
down_revision: str | Sequence[str] | None = "3b4c5d6e7f8g"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add related_words column (JSONB)
    op.add_column(
        "vocabulary_cards",
        sa.Column(
            "related_words",
            sa.JSON(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("vocabulary_cards", "related_words")
