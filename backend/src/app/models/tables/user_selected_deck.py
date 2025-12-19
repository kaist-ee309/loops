"""UserSelectedDeck model for tracking user's selected decks."""

from uuid import UUID

from sqlalchemy import ForeignKey, Uuid
from sqlmodel import Column, Field, UniqueConstraint

from app.models.base import TimestampMixin


class UserSelectedDeck(TimestampMixin, table=True):
    """Junction table for user's selected decks.

    Tracks which decks a user has selected for learning.
    Only used when user.select_all_decks is False.
    """

    __tablename__ = "user_selected_decks"
    __table_args__ = (UniqueConstraint("user_id", "deck_id", name="uq_user_deck"),)

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    user_id: UUID = Field(
        sa_column=Column(Uuid, ForeignKey("profiles.id"), nullable=False, index=True),
    )
    deck_id: int = Field(foreign_key="decks.id", index=True, nullable=False)
