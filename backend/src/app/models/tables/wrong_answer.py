"""Wrong answer model for tracking incorrect answers."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Uuid
from sqlmodel import Column, Field, SQLModel

from app.models.base import TimestampMixin


class WrongAnswerBase(SQLModel):
    """Base WrongAnswer model with shared fields."""

    user_answer: str = Field(description="사용자가 입력한 답")
    correct_answer: str = Field(description="정답")
    quiz_type: str = Field(
        description="퀴즈 유형 (cloze/word_to_meaning/meaning_to_word/listening)"
    )


class WrongAnswer(WrongAnswerBase, TimestampMixin, table=True):
    """Wrong answer database model for tracking incorrect answers."""

    __tablename__ = "wrong_answers"

    id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(
        sa_column=Column(Uuid, nullable=False, index=True),
    )
    card_id: int = Field(foreign_key="vocabulary_cards.id", index=True)
    session_id: UUID | None = Field(
        default=None,
        sa_column=Column(Uuid, nullable=True, index=True),
    )

    # 복습 상태
    reviewed: bool = Field(default=False, description="오답 노트에서 복습했는지")
    reviewed_at: datetime | None = Field(default=None, description="복습 완료 시간")
