"""add cloze_sentences to vocabulary_cards

Revision ID: 65b7c40aca48
Revises: b1c2d3e4f5g6
Create Date: 2025-12-10 10:35:14.689241

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "65b7c40aca48"
down_revision: str | Sequence[str] | None = "b1c2d3e4f5g6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add cloze_sentences column to vocabulary_cards."""
    op.add_column("vocabulary_cards", sa.Column("cloze_sentences", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Remove cloze_sentences column from vocabulary_cards."""
    op.drop_column("vocabulary_cards", "cloze_sentences")
