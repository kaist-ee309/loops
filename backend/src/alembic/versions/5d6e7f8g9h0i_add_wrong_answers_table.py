"""add wrong_answers table

Revision ID: 5d6e7f8g9h0i
Revises: 4c5d6e7f8g9h
Create Date: 2025-12-13 15:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5d6e7f8g9h0i"
down_revision: str | None = "4c5d6e7f8g9h"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "wrong_answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=True),
        sa.Column("user_answer", sa.String(), nullable=False),
        sa.Column("correct_answer", sa.String(), nullable=False),
        sa.Column("quiz_type", sa.String(), nullable=False),
        sa.Column("reviewed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["card_id"], ["vocabulary_cards.id"]),
    )
    op.create_index("ix_wrong_answers_user_id", "wrong_answers", ["user_id"])
    op.create_index("ix_wrong_answers_card_id", "wrong_answers", ["card_id"])
    op.create_index("ix_wrong_answers_session_id", "wrong_answers", ["session_id"])


def downgrade() -> None:
    op.drop_index("ix_wrong_answers_session_id", table_name="wrong_answers")
    op.drop_index("ix_wrong_answers_card_id", table_name="wrong_answers")
    op.drop_index("ix_wrong_answers_user_id", table_name="wrong_answers")
    op.drop_table("wrong_answers")
