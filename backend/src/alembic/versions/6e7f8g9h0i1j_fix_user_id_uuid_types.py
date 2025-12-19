"""fix user_id uuid types in multiple tables

Revision ID: 6e7f8g9h0i1j
Revises: 5d6e7f8g9h0i
Create Date: 2025-12-13 23:00:00.000000

This migration:
1. Drops legacy foreign keys referencing 'users' table
2. Changes user_id/creator_id columns from integer to UUID
3. Recreates foreign keys referencing 'profiles' table

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6e7f8g9h0i1j"
down_revision: str | Sequence[str] | None = "5d6e7f8g9h0i"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - convert integer user_id columns to UUID and fix FK references."""
    # Step 1: Drop old foreign keys (referencing legacy 'users' table)
    op.drop_constraint("user_card_progress_user_id_fkey", "user_card_progress", type_="foreignkey")
    op.drop_constraint("favorites_user_id_fkey", "favorites", type_="foreignkey")
    op.drop_constraint(
        "user_selected_decks_user_id_fkey", "user_selected_decks", type_="foreignkey"
    )
    op.drop_constraint("decks_creator_id_fkey", "decks", type_="foreignkey")

    # Step 2: Alter column types from integer to UUID
    # user_card_progress.user_id
    op.alter_column(
        "user_card_progress",
        "user_id",
        existing_type=sa.Integer(),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=False,
        postgresql_using="gen_random_uuid()",  # Empty table, use placeholder
    )

    # favorites.user_id
    op.alter_column(
        "favorites",
        "user_id",
        existing_type=sa.Integer(),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=False,
        postgresql_using="gen_random_uuid()",  # Empty table, use placeholder
    )

    # user_selected_decks.user_id
    op.alter_column(
        "user_selected_decks",
        "user_id",
        existing_type=sa.Integer(),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=False,
        postgresql_using="gen_random_uuid()",  # Empty table, use placeholder
    )

    # decks.creator_id (nullable)
    op.alter_column(
        "decks",
        "creator_id",
        existing_type=sa.Integer(),
        type_=postgresql.UUID(as_uuid=True),
        existing_nullable=True,
        postgresql_using="NULL",  # Set to NULL since we can't convert integer to UUID meaningfully
    )

    # Step 3: Recreate foreign keys referencing 'profiles' table
    op.create_foreign_key(
        "user_card_progress_user_id_fkey",
        "user_card_progress",
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
        "user_selected_decks_user_id_fkey",
        "user_selected_decks",
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


def downgrade() -> None:
    """Downgrade schema - this is a one-way migration, downgrade not fully supported."""
    # Drop new foreign keys
    op.drop_constraint("user_card_progress_user_id_fkey", "user_card_progress", type_="foreignkey")
    op.drop_constraint("favorites_user_id_fkey", "favorites", type_="foreignkey")
    op.drop_constraint(
        "user_selected_decks_user_id_fkey", "user_selected_decks", type_="foreignkey"
    )
    op.drop_constraint("decks_creator_id_fkey", "decks", type_="foreignkey")

    # Revert column types (will lose data if there are UUIDs)
    op.alter_column(
        "decks",
        "creator_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="NULL",
    )
    op.alter_column(
        "user_selected_decks",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="0",
    )
    op.alter_column(
        "favorites",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="0",
    )
    op.alter_column(
        "user_card_progress",
        "user_id",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="0",
    )

    # Note: Cannot recreate original foreign keys to 'users' table as it may not exist
