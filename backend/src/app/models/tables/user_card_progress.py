from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Uuid
from sqlmodel import JSON, Column, Enum, Field, SQLModel, UniqueConstraint

from app.models.base import TimestampMixin
from app.models.enums import CardState


class UserCardProgressBase(SQLModel):
    """Base UserCardProgress model with shared fields."""

    user_id: UUID = Field(
        sa_column=Column(Uuid, ForeignKey("profiles.id"), nullable=False, index=True),
    )
    card_id: int = Field(foreign_key="vocabulary_cards.id", index=True)

    # FSRS Algorithm Parameters
    interval: int = Field(default=0)
    repetitions: int = Field(default=0)

    # Statistics
    total_reviews: int = Field(default=0)
    correct_count: int = Field(default=0)

    # FSRS Extended Parameters
    stability: float | None = Field(default=0.0)
    difficulty: float | None = Field(default=5.0)
    scheduled_days: int = Field(default=0)
    lapses: int = Field(default=0)
    elapsed_days: int = Field(default=0)


class UserCardProgress(UserCardProgressBase, TimestampMixin, table=True):
    """UserCardProgress database model for tracking FSRS progress."""

    __tablename__ = "user_card_progress"
    __table_args__ = (UniqueConstraint("user_id", "card_id", name="uq_user_card"),)

    id: int | None = Field(default=None, primary_key=True, nullable=False)

    next_review_date: datetime = Field(index=True)
    last_review_date: datetime | None = Field(default=None)

    card_state: CardState = Field(
        default=CardState.NEW,
        sa_column=Column(
            Enum(CardState, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
            index=True,
        ),
    )

    quality_history: dict[str, Any] | list[Any] | None = Field(default=None, sa_column=Column(JSON))
