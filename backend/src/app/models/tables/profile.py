"""Profile model for user app-specific data linked to Supabase Auth."""

from datetime import date
from uuid import UUID

from sqlalchemy import Uuid
from sqlmodel import Column, Field, SQLModel

from app.models.base import TimestampMixin


class ProfileBase(SQLModel):
    """Base Profile model with shared fields."""

    # Learning preferences (DB-1, DB-2)
    select_all_decks: bool = Field(default=True)  # If true, study from all decks
    daily_goal: int = Field(default=20)  # Daily learning goal (number of cards)

    # Review ratio settings (Issue #47)
    # - normal 모드: 새 단어 최소 min_new_ratio(25%) 보장
    # - custom 모드: 복습 비율 custom_review_ratio 그대로 적용
    review_ratio_mode: str = Field(
        default="normal",
        max_length=20,
        description="복습 비율 모드: normal(일반) | custom(커스텀)",
    )
    custom_review_ratio: float = Field(
        default=0.75,
        ge=0.0,
        le=1.0,
        description="커스텀 모드 복습 비율 (0.0~1.0). 0.75 = 복습 75%, 새 단어 25%",
    )
    min_new_ratio: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="일반 모드 최소 새 단어 비율 (기본 25%)",
    )

    # Review scope setting (Issue #49)
    review_scope: str = Field(
        default="selected_decks_only",
        max_length=30,
        description="복습 범위: selected_decks_only(선택한 단어장만) | all_learned(학습한 모든 단어)",
    )

    # User settings (DB-8)
    timezone: str = Field(default="UTC", max_length=50)
    theme: str = Field(default="auto", max_length=20)  # light/dark/auto
    notification_enabled: bool = Field(default=True)

    # UI customization (Issue #55)
    highlight_color: str = Field(
        default="#4CAF50", max_length=20, description="Clue 하이라이트 색상 (HEX 코드)"
    )


class Profile(ProfileBase, TimestampMixin, table=True):
    """Profile database model linked to Supabase Auth user."""

    __tablename__ = "profiles"

    # UUID from Supabase auth.users.id - direct reference, no separate supabase_uid needed
    id: UUID = Field(
        sa_column=Column(Uuid, primary_key=True, nullable=False),
        description="User ID from Supabase Auth (auth.users.id)",
    )

    # Streak tracking
    current_streak: int = Field(default=0)
    longest_streak: int = Field(default=0)
    last_study_date: date | None = Field(default=None, index=True)

    # Study statistics
    total_study_time_minutes: int = Field(default=0)
