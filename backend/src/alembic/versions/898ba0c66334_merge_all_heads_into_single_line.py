"""merge all heads into single line

Revision ID: 898ba0c66334
Revises: 0dc1f3eefd7a, 58f07e279e66, 6e7f8g9h0i1j, 9f8e7d6c5b4a
Create Date: 2025-12-14 16:08:56.051799

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "898ba0c66334"
down_revision: str | Sequence[str] | None = (
    "0dc1f3eefd7a",
    "58f07e279e66",
    "6e7f8g9h0i1j",
    "9f8e7d6c5b4a",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
