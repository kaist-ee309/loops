"""Profile schemas for API request/response models."""

from datetime import date, datetime
from uuid import UUID

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.models.tables.profile import ProfileBase


class ProfileRead(ProfileBase):
    """프로필 조회 응답 스키마."""

    id: UUID = Field(description="사용자 고유 ID (Supabase Auth ID)")
    current_streak: int = Field(description="현재 연속 학습일 수")
    longest_streak: int = Field(description="최장 연속 학습일 수 (역대 기록)")
    last_study_date: date | None = Field(default=None, description="마지막 학습 날짜")
    select_all_decks: bool = Field(description="전체 덱 선택 여부. true면 모든 공개 덱에서 학습")
    daily_goal: int = Field(description="일일 학습 목표 카드 수")
    review_ratio_mode: str = Field(description="복습 비율 모드: normal(일반) | custom(커스텀)")
    custom_review_ratio: float = Field(description="커스텀 모드 복습 비율 (0.0~1.0)")
    min_new_ratio: float = Field(description="일반 모드 최소 새 단어 비율 (0.0~1.0)")
    review_scope: str = Field(
        description="복습 범위: selected_decks_only(선택한 단어장만) | all_learned(학습한 모든 단어)"
    )
    timezone: str = Field(description="사용자 타임존 (예: Asia/Seoul)")
    theme: str = Field(description="앱 테마 (light, dark, auto)")
    notification_enabled: bool = Field(description="알림 활성화 여부")
    highlight_color: str = Field(description="Clue 하이라이트 색상 (HEX 코드)")
    total_study_time_minutes: int = Field(default=0, description="총 학습 시간 (분)")
    created_at: datetime = Field(description="계정 생성 시간 (UTC)")
    updated_at: datetime | None = Field(default=None, description="계정 정보 최종 수정 시간 (UTC)")


class ProfileUpdate(SQLModel):
    """프로필 정보 수정 스키마. 부분 업데이트 지원."""

    select_all_decks: bool | None = Field(default=None, description="전체 덱 선택 여부")
    daily_goal: int | None = Field(
        default=None, gt=0, le=1000, description="일일 학습 목표 (1~1000)"
    )
    review_ratio_mode: str | None = Field(
        default=None,
        max_length=20,
        description="복습 비율 모드: normal(일반) | custom(커스텀)",
    )
    custom_review_ratio: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="커스텀 모드 복습 비율 (0.0~1.0)",
    )
    min_new_ratio: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="일반 모드 최소 새 단어 비율 (0.0~1.0)",
    )
    review_scope: str | None = Field(
        default=None,
        max_length=30,
        description="복습 범위: selected_decks_only(선택한 단어장만) | all_learned(학습한 모든 단어)",
    )
    timezone: str | None = Field(default=None, max_length=50, description="타임존 (예: Asia/Seoul)")
    theme: str | None = Field(default=None, max_length=20, description="테마 (light, dark, auto)")
    notification_enabled: bool | None = Field(default=None, description="알림 활성화 여부")
    highlight_color: str | None = Field(
        default=None, max_length=20, description="Clue 하이라이트 색상 (HEX 코드)"
    )

    @field_validator("theme")
    @classmethod
    def theme_valid(cls, v: str | None) -> str | None:
        """테마가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f"Theme must be one of: {', '.join(allowed_themes)}")
        return v

    @field_validator("review_ratio_mode")
    @classmethod
    def review_ratio_mode_valid(cls, v: str | None) -> str | None:
        """복습 비율 모드가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_modes = {"normal", "custom"}
        if v not in allowed_modes:
            raise ValueError(f"Review ratio mode must be one of: {', '.join(allowed_modes)}")
        return v

    @field_validator("review_scope")
    @classmethod
    def review_scope_valid(cls, v: str | None) -> str | None:
        """복습 범위가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_scopes = {"selected_decks_only", "all_learned"}
        if v not in allowed_scopes:
            raise ValueError(f"Review scope must be one of: {', '.join(allowed_scopes)}")
        return v


class DailyGoalRead(SQLModel):
    """일일 목표 조회 응답 스키마."""

    daily_goal: int = Field(description="설정된 일일 목표 카드 수")
    completed_today: int = Field(description="오늘 학습 완료한 카드 수")


class StreakRead(SQLModel):
    """스트릭 정보 조회 응답 스키마."""

    current_streak: int = Field(description="현재 연속 학습일 수")
    longest_streak: int = Field(description="최장 연속 학습일 수 (역대 기록)")
    last_study_date: date | None = Field(default=None, description="마지막 학습 날짜")
    days_studied_this_month: int = Field(description="이번 달 학습한 일수")
    streak_status: str = Field(description="스트릭 상태. 'active'(유지 중) 또는 'broken'(끊김)")
    message: str = Field(description="사용자에게 표시할 동기 부여 메시지")


class ProfileConfigRead(SQLModel):
    """사용자 설정 조회 응답 스키마."""

    daily_goal: int = Field(description="일일 학습 목표 카드 수")
    select_all_decks: bool = Field(description="전체 덱 선택 여부")
    review_ratio_mode: str = Field(description="복습 비율 모드: normal(일반) | custom(커스텀)")
    custom_review_ratio: float = Field(description="커스텀 모드 복습 비율 (0.0~1.0)")
    min_new_ratio: float = Field(description="일반 모드 최소 새 단어 비율 (0.0~1.0)")
    review_scope: str = Field(
        description="복습 범위: selected_decks_only(선택한 단어장만) | all_learned(학습한 모든 단어)"
    )
    timezone: str = Field(description="사용자 타임존")
    theme: str = Field(description="앱 테마 (light, dark, auto)")
    notification_enabled: bool = Field(description="알림 활성화 여부")
    highlight_color: str = Field(description="Clue 하이라이트 색상 (HEX 코드)")


class ProfileConfigUpdate(SQLModel):
    """사용자 설정 수정 스키마. 부분 업데이트 지원."""

    daily_goal: int | None = Field(
        default=None, gt=0, le=1000, description="일일 학습 목표 (1~1000)"
    )
    select_all_decks: bool | None = Field(default=None, description="전체 덱 선택 여부")
    review_ratio_mode: str | None = Field(
        default=None,
        max_length=20,
        description="복습 비율 모드: normal(일반) | custom(커스텀)",
    )
    custom_review_ratio: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="커스텀 모드 복습 비율 (0.0~1.0)",
    )
    min_new_ratio: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="일반 모드 최소 새 단어 비율 (0.0~1.0)",
    )
    review_scope: str | None = Field(
        default=None,
        max_length=30,
        description="복습 범위: selected_decks_only(선택한 단어장만) | all_learned(학습한 모든 단어)",
    )
    timezone: str | None = Field(default=None, max_length=50, description="타임존 (예: Asia/Seoul)")
    theme: str | None = Field(default=None, max_length=20, description="테마 (light, dark, auto)")
    notification_enabled: bool | None = Field(default=None, description="알림 활성화 여부")
    highlight_color: str | None = Field(
        default=None, max_length=20, description="Clue 하이라이트 색상 (HEX 코드)"
    )

    @field_validator("theme")
    @classmethod
    def theme_valid(cls, v: str | None) -> str | None:
        """테마가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_themes = {"light", "dark", "auto"}
        if v not in allowed_themes:
            raise ValueError(f"Theme must be one of: {', '.join(allowed_themes)}")
        return v

    @field_validator("review_ratio_mode")
    @classmethod
    def review_ratio_mode_valid(cls, v: str | None) -> str | None:
        """복습 비율 모드가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_modes = {"normal", "custom"}
        if v not in allowed_modes:
            raise ValueError(f"Review ratio mode must be one of: {', '.join(allowed_modes)}")
        return v

    @field_validator("review_scope")
    @classmethod
    def review_scope_valid(cls, v: str | None) -> str | None:
        """복습 범위가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_scopes = {"selected_decks_only", "all_learned"}
        if v not in allowed_scopes:
            raise ValueError(f"Review scope must be one of: {', '.join(allowed_scopes)}")
        return v


class ProfileLevelRead(SQLModel):
    """사용자 레벨 조회 응답 스키마."""

    level: float = Field(description="숙련도 레벨 (1.0 ~ 10.0)")
    cefr_equivalent: str = Field(description="CEFR 등급 (A1, A2, B1, B2, C1, C2)")
    total_reviews: int = Field(description="총 복습 횟수")
    accuracy_rate: float = Field(description="전체 정확도 (%)")
    mastered_cards: int = Field(description="마스터한 카드 수 (REVIEW 상태)")
