"""Favorite model for user's favorite vocabulary cards."""

from uuid import UUID

from sqlalchemy import ForeignKey, Uuid
from sqlmodel import Column, Field, UniqueConstraint

from app.models.base import TimestampMixin


class Favorite(TimestampMixin, table=True):
    """User's favorite vocabulary cards.

    Allows users to bookmark/favorite cards for quick access.
    """

    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "card_id", name="uq_user_card_favorite"),)

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    user_id: UUID = Field(
        sa_column=Column(Uuid, ForeignKey("profiles.id"), nullable=False, index=True),
    )
    card_id: int = Field(foreign_key="vocabulary_cards.id", index=True, nullable=False)
