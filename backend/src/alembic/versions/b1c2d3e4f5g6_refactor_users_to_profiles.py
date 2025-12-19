"""Refactor users table to profiles with UUID primary key

This migration:
1. Creates new profiles table with UUID primary key (from Supabase auth.users.id)
2. Updates all foreign keys (user_id) from INT to UUID
3. Drops the old users table

Revision ID: b1c2d3e4f5g6
Revises: f1a2b3c4d5e6
Create Date: 2025-12-10 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5g6"
down_revision: str | Sequence[str] | None = "f1a2b3c4d5e6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: users -> profiles with UUID PK."""
    # 1. Create new profiles table with UUID primary key
    op.create_table(
        "profiles",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("select_all_decks", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("daily_goal", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("timezone", sa.String(length=50), nullable=False, server_default="UTC"),
        sa.Column("theme", sa.String(length=20), nullable=False, server_default="auto"),
        sa.Column("notification_enabled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("longest_streak", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_study_date", sa.Date(), nullable=True),
        sa.Column("total_study_time_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_profiles_last_study_date"),
        "profiles",
        ["last_study_date"],
        unique=False,
    )

    # 2. Drop old foreign key constraints
    op.drop_constraint("user_card_progress_user_id_fkey", "user_card_progress", type_="foreignkey")
    op.drop_constraint(
        "user_selected_decks_user_id_fkey", "user_selected_decks", type_="foreignkey"
    )
    op.drop_constraint("favorites_user_id_fkey", "favorites", type_="foreignkey")
    op.drop_constraint("decks_creator_id_fkey", "decks", type_="foreignkey")

    # 3. Drop old indexes on user_id columns
    op.drop_index("ix_user_card_progress_user_id", table_name="user_card_progress")
    op.drop_index("ix_user_selected_decks_user_id", table_name="user_selected_decks")
    op.drop_index("ix_favorites_user_id", table_name="favorites")
    op.drop_index("ix_decks_creator_id", table_name="decks")

    # 4. Drop old user_id columns
    op.drop_column("user_card_progress", "user_id")
    op.drop_column("user_selected_decks", "user_id")
    op.drop_column("favorites", "user_id")
    op.drop_column("decks", "creator_id")

    # 5. Add new UUID user_id columns
    op.add_column(
        "user_card_progress",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.add_column(
        "user_selected_decks",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.add_column(
        "favorites",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
    )
    op.add_column(
        "decks",
        sa.Column("creator_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    # 6. Create new foreign key constraints referencing profiles
    op.create_foreign_key(
        "user_card_progress_user_id_fkey",
        "user_card_progress",
        "profiles",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "user_selected_decks_user_id_fkey",
        "user_selected_decks",
        "profiles",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "favorites_user_id_fkey",
        "favorites",
        "profiles",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "decks_creator_id_fkey",
        "decks",
        "profiles",
        ["creator_id"],
        ["id"],
    )

    # 7. Create new indexes on user_id columns
    op.create_index(
        op.f("ix_user_card_progress_user_id"),
        "user_card_progress",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_selected_decks_user_id"),
        "user_selected_decks",
        ["user_id"],
        unique=False,
    )
    op.create_index(op.f("ix_favorites_user_id"), "favorites", ["user_id"], unique=False)
    op.create_index(op.f("ix_decks_creator_id"), "decks", ["creator_id"], unique=False)

    # 8. Drop old users table
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_index("ix_users_is_active", table_name="users")
    op.drop_index("ix_users_last_study_date", table_name="users")
    op.drop_table("users")


def downgrade() -> None:
    """Downgrade schema: profiles -> users with INT PK."""
    # 1. Recreate old users table
    op.create_table(
        "users",
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("select_all_decks", sa.Boolean(), nullable=False),
        sa.Column("daily_goal", sa.Integer(), nullable=False),
        sa.Column("timezone", sa.String(length=50), nullable=False),
        sa.Column("theme", sa.String(length=20), nullable=False),
        sa.Column("notification_enabled", sa.Boolean(), nullable=False),
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("current_streak", sa.Integer(), nullable=False),
        sa.Column("longest_streak", sa.Integer(), nullable=False),
        sa.Column("last_study_date", sa.Date(), nullable=True),
        sa.Column("total_study_time_minutes", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_username", "users", ["username"], unique=True)
    op.create_index("ix_users_is_active", "users", ["is_active"], unique=False)
    op.create_index("ix_users_last_study_date", "users", ["last_study_date"], unique=False)

    # 2. Drop new foreign key constraints
    op.drop_constraint("user_card_progress_user_id_fkey", "user_card_progress", type_="foreignkey")
    op.drop_constraint(
        "user_selected_decks_user_id_fkey", "user_selected_decks", type_="foreignkey"
    )
    op.drop_constraint("favorites_user_id_fkey", "favorites", type_="foreignkey")
    op.drop_constraint("decks_creator_id_fkey", "decks", type_="foreignkey")

    # 3. Drop new indexes
    op.drop_index(op.f("ix_user_card_progress_user_id"), table_name="user_card_progress")
    op.drop_index(op.f("ix_user_selected_decks_user_id"), table_name="user_selected_decks")
    op.drop_index(op.f("ix_favorites_user_id"), table_name="favorites")
    op.drop_index(op.f("ix_decks_creator_id"), table_name="decks")

    # 4. Drop UUID columns
    op.drop_column("user_card_progress", "user_id")
    op.drop_column("user_selected_decks", "user_id")
    op.drop_column("favorites", "user_id")
    op.drop_column("decks", "creator_id")

    # 5. Add back INT columns
    op.add_column(
        "user_card_progress",
        sa.Column("user_id", sa.Integer(), nullable=False),
    )
    op.add_column(
        "user_selected_decks",
        sa.Column("user_id", sa.Integer(), nullable=False),
    )
    op.add_column(
        "favorites",
        sa.Column("user_id", sa.Integer(), nullable=False),
    )
    op.add_column(
        "decks",
        sa.Column("creator_id", sa.Integer(), nullable=True),
    )

    # 6. Recreate old foreign key constraints
    op.create_foreign_key(
        "user_card_progress_user_id_fkey",
        "user_card_progress",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "user_selected_decks_user_id_fkey",
        "user_selected_decks",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "favorites_user_id_fkey",
        "favorites",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "decks_creator_id_fkey",
        "decks",
        "users",
        ["creator_id"],
        ["id"],
    )

    # 7. Recreate old indexes
    op.create_index(
        "ix_user_card_progress_user_id", "user_card_progress", ["user_id"], unique=False
    )
    op.create_index(
        "ix_user_selected_decks_user_id",
        "user_selected_decks",
        ["user_id"],
        unique=False,
    )
    op.create_index("ix_favorites_user_id", "favorites", ["user_id"], unique=False)
    op.create_index("ix_decks_creator_id", "decks", ["creator_id"], unique=False)

    # 8. Drop profiles table
    op.drop_index(op.f("ix_profiles_last_study_date"), table_name="profiles")
    op.drop_table("profiles")
