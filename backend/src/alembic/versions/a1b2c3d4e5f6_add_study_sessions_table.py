"""add study_sessions table

Revision ID: a1b2c3d4e5f6
Revises: 65b7c40aca48
Create Date: 2025-12-10 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "65b7c40aca48"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create study_sessions table."""
    # Create SessionStatus enum type
    session_status_enum = postgresql.ENUM(
        "active", "completed", "abandoned", name="sessionstatus", create_type=False
    )
    session_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "study_sessions",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("new_cards_limit", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("review_cards_limit", sa.Integer(), nullable=False, server_default="20"),
        sa.Column(
            "status",
            postgresql.ENUM(
                "active",
                "completed",
                "abandoned",
                name="sessionstatus",
                create_type=False,
            ),
            nullable=False,
            server_default="active",
        ),
        sa.Column("card_ids", sa.JSON(), nullable=True),
        sa.Column("current_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("wrong_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_study_sessions_user_id"), "study_sessions", ["user_id"], unique=False)
    op.create_index(op.f("ix_study_sessions_status"), "study_sessions", ["status"], unique=False)


def downgrade() -> None:
    """Drop study_sessions table."""
    op.drop_index(op.f("ix_study_sessions_status"), table_name="study_sessions")
    op.drop_index(op.f("ix_study_sessions_user_id"), table_name="study_sessions")
    op.drop_table("study_sessions")

    # Drop the enum type
    session_status_enum = postgresql.ENUM("active", "completed", "abandoned", name="sessionstatus")
    session_status_enum.drop(op.get_bind(), checkfirst=True)
