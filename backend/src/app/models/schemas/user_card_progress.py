from datetime import datetime

from sqlmodel import Field, SQLModel

from app.models.enums import CardState
from app.models.tables.user_card_progress import UserCardProgressBase


class UserCardProgressCreate(UserCardProgressBase):
    """사용자 카드 학습 진행 생성 스키마."""

    next_review_date: datetime = Field(description="다음 복습 예정 시간 (UTC)")
    card_state: CardState = Field(
        default=CardState.NEW, description="카드 상태 (NEW/LEARNING/REVIEW/RELEARNING)"
    )


class UserCardProgressRead(UserCardProgressBase):
    """사용자 카드 학습 진행 조회 응답 스키마."""

    id: int = Field(description="학습 진행 기록 고유 ID")
    next_review_date: datetime = Field(description="다음 복습 예정 시간 (UTC)")
    last_review_date: datetime | None = Field(default=None, description="마지막 복습 시간 (UTC)")
    card_state: CardState = Field(
        description="카드 상태. NEW(미학습), LEARNING(학습중), REVIEW(복습), RELEARNING(재학습)"
    )
    created_at: datetime = Field(description="최초 학습 시작 시간 (UTC)")
    updated_at: datetime | None = Field(default=None, description="최종 업데이트 시간 (UTC)")


class ReviewRequest(SQLModel):
    """카드 복습 결과 제출 스키마."""

    card_id: int = Field(gt=0, description="복습한 카드 ID (양수)")
    is_correct: bool = Field(description="정답 여부. true=기억함(Good), false=잊음(Again)")


class TodayProgressRead(SQLModel):
    """오늘의 학습 진행 상황 응답 스키마."""

    total_reviews: int = Field(description="오늘 총 복습 횟수")
    correct_count: int = Field(description="오늘 정답 수")
    wrong_count: int = Field(description="오늘 오답 수")
    accuracy_rate: float = Field(description="오늘 정확도 (%) - (정답/총복습)*100")
    daily_goal: int = Field(description="설정된 일일 목표 카드 수")
    goal_progress: float = Field(description="일일 목표 달성률 (%) - (완료/목표)*100")


class NewCardsCountRead(SQLModel):
    """신규/복습 카드 수 응답 스키마."""

    new_cards_count: int = Field(description="아직 학습하지 않은 신규 카드 수 (선택한 덱 기준)")
    review_cards_count: int = Field(description="오늘 복습해야 할 카드 수 (선택한 덱 기준)")
