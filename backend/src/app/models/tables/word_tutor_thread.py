"""Word tutor chat thread model."""

from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy import JSON, ForeignKey, Uuid
from sqlmodel import Column, Field, SQLModel, UniqueConstraint

from app.models.base import TimestampMixin


class WordTutorThreadBase(SQLModel):
    """Base WordTutorThread model with shared fields."""

    user_id: UUID = Field(
        sa_column=Column(Uuid, ForeignKey("profiles.id"), nullable=False, index=True),
    )
    session_id: UUID = Field(
        sa_column=Column(Uuid, ForeignKey("study_sessions.id"), nullable=False, index=True),
    )
    card_id: int = Field(
        sa_column=Column(sa.Integer, ForeignKey("vocabulary_cards.id"), nullable=False, index=True),
    )

    starter_questions: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class WordTutorThread(WordTutorThreadBase, TimestampMixin, table=True):
    """Word tutor thread for a (user, session, card) tuple."""

    __tablename__ = "word_tutor_threads"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "session_id",
            "card_id",
            name="uq_word_tutor_thread_user_session_card",
        ),
    )

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(Uuid, primary_key=True, nullable=False),
    )
