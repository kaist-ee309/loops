from uuid import UUID

from sqlalchemy import ForeignKey, Uuid
from sqlmodel import Column, Field, SQLModel

from app.models.base import TimestampMixin


class DeckBase(SQLModel):
    """Base Deck model with shared fields."""

    name: str = Field(max_length=255)
    description: str | None = Field(default=None)
    category: str | None = Field(
        default=None, max_length=100, index=True
    )  # business/toeic/academic/daily
    difficulty_level: str | None = Field(
        default=None, max_length=50
    )  # beginner/intermediate/advanced
    is_public: bool = Field(default=False, index=True)
    is_official: bool = Field(default=False)


class Deck(DeckBase, TimestampMixin, table=True):
    """Deck database model."""

    __tablename__ = "decks"

    id: int | None = Field(default=None, primary_key=True, nullable=False)
    creator_id: UUID | None = Field(
        default=None,
        sa_column=Column(Uuid, ForeignKey("profiles.id"), nullable=True, index=True),
    )
