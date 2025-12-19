"""baseline for unknown remote revision

Revision ID: 0dc1f3eefd7a
Revises:
Create Date: 2025-12-13

This is a compatibility baseline to allow Alembic to operate against an existing
database whose alembic_version was set to 0dc1f3eefd7a outside of this repo's
current migration history.

It is intentionally a no-op migration.
"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "0dc1f3eefd7a"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema (no-op baseline)."""


def downgrade() -> None:
    """Downgrade schema (no-op baseline)."""
