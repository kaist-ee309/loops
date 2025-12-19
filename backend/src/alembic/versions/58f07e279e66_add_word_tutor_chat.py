"""add word tutor chat

Revision ID: 58f07e279e66
Revises: 5e0888ee7d18
Create Date: 2025-12-13 10:53:09.225987

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "58f07e279e66"
down_revision: str | Sequence[str] | None = "5e0888ee7d18"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    chat_role_enum = postgresql.ENUM(
        "system",
        "user",
        "assistant",
        name="chatrole",
        create_type=False,
    )
    chat_role_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "word_tutor_threads",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("session_id", sa.Uuid(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("starter_questions", sa.JSON(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["card_id"], ["vocabulary_cards.id"]),
        sa.ForeignKeyConstraint(["session_id"], ["study_sessions.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["profiles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "session_id",
            "card_id",
            name="uq_word_tutor_thread_user_session_card",
        ),
    )
    op.create_index(
        op.f("ix_word_tutor_threads_user_id"),
        "word_tutor_threads",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_word_tutor_threads_session_id"),
        "word_tutor_threads",
        ["session_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_word_tutor_threads_card_id"),
        "word_tutor_threads",
        ["card_id"],
        unique=False,
    )

    op.create_table(
        "word_tutor_messages",
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.Column("thread_id", sa.Uuid(), nullable=False),
        sa.Column(
            "role",
            postgresql.ENUM(
                "system",
                "user",
                "assistant",
                name="chatrole",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("suggested_questions", sa.JSON(), nullable=True),
        sa.Column("openai_response_id", sa.String(length=255), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("usage", sa.JSON(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(
            ["thread_id"],
            ["word_tutor_threads.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_word_tutor_messages_thread_id"),
        "word_tutor_messages",
        ["thread_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_word_tutor_messages_role"),
        "word_tutor_messages",
        ["role"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_word_tutor_messages_role"), table_name="word_tutor_messages")
    op.drop_index(op.f("ix_word_tutor_messages_thread_id"), table_name="word_tutor_messages")
    op.drop_table("word_tutor_messages")

    op.drop_index(op.f("ix_word_tutor_threads_card_id"), table_name="word_tutor_threads")
    op.drop_index(op.f("ix_word_tutor_threads_session_id"), table_name="word_tutor_threads")
    op.drop_index(op.f("ix_word_tutor_threads_user_id"), table_name="word_tutor_threads")
    op.drop_table("word_tutor_threads")

    chat_role_enum = postgresql.ENUM("system", "user", "assistant", name="chatrole")
    chat_role_enum.drop(op.get_bind(), checkfirst=True)
