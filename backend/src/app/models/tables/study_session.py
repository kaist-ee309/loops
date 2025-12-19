"""Study session model for tracking learning sessions."""

from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import JSON, Enum, Uuid
from sqlmodel import Column, Field, SQLModel

from app.models.base import TimestampMixin
from app.models.enums import SessionStatus


class StudySessionBase(SQLModel):
    """Base StudySession model with shared fields."""

    # 세션 설정
    new_cards_limit: int = Field(default=10, ge=0, le=50)
    review_cards_limit: int = Field(default=20, ge=0, le=100)


class StudySession(StudySessionBase, TimestampMixin, table=True):
    """Study session database model for tracking learning sessions."""

    __tablename__ = "study_sessions"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(Uuid, primary_key=True, nullable=False),
    )
    user_id: UUID = Field(
        sa_column=Column(Uuid, nullable=False, index=True),
    )

    # 세션 상태
    status: SessionStatus = Field(
        default=SessionStatus.ACTIVE,
        sa_column=Column(
            Enum(SessionStatus, values_callable=lambda x: [e.value for e in x]),
            nullable=False,
            index=True,
        ),
    )

    # 카드 목록 (학습할 카드 ID 목록)
    card_ids: list[int] = Field(default_factory=list, sa_column=Column(JSON))

    # 진행 상태
    current_index: int = Field(default=0)

    # 결과 집계
    correct_count: int = Field(default=0)
    wrong_count: int = Field(default=0)
    new_cards_count: int = Field(default=0, description="오늘 학습한 신규 카드 수")
    review_cards_count: int = Field(default=0, description="오늘 학습한 복습 카드 수")

    # 타임스탬프
    started_at: datetime = Field(default_factory=lambda: datetime.utcnow())
    completed_at: datetime | None = Field(default=None)
