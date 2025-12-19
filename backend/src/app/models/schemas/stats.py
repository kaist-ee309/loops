import datetime

from sqlmodel import Field, SQLModel


class TotalLearnedRead(SQLModel):
    """총 학습량 통계 응답 스키마."""

    total_learned: int = Field(description="학습 완료한 총 카드 수 (REVIEW 상태 카드)")
    by_level: dict[str, int] = Field(
        description='CEFR 레벨별 학습 완료 카드 수. 예: {"A1": 50, "A2": 30, "B1": 10}'
    )
    total_study_time_minutes: int = Field(description="누적 총 학습 시간 (분)")


class StatsHistoryItem(SQLModel):
    """일별 학습 기록 항목 스키마."""

    date: datetime.date = Field(description="학습 날짜")
    cards_studied: int = Field(description="해당 날짜에 학습한 카드 수")
    correct_count: int = Field(description="해당 날짜의 정답 수")
    accuracy_rate: float = Field(description="해당 날짜의 정확도 (%)")
    study_time_seconds: int = Field(default=0, description="해당 날짜의 총 학습 시간 (초)")


class StatsHistorySummary(SQLModel):
    """학습 기록 요약 통계 스키마."""

    total_study_time_seconds: int = Field(description="기간 내 총 학습 시간 (초)")
    total_cards_studied: int = Field(description="기간 내 총 학습 카드 수")
    avg_daily_study_time_seconds: int = Field(
        description="하루 평균 학습 시간 (초, 활동 일수 기준)"
    )
    avg_daily_cards_studied: int = Field(description="하루 평균 학습 카드 수 (활동 일수 기준)")
    days_with_activity: int = Field(description="활동이 있었던 일수")


class StatsHistoryRead(SQLModel):
    """학습 기록 응답 스키마 (차트용 데이터)."""

    period: str = Field(description="조회 기간. 7d(7일), 30d(30일), 1y(1년), all(전체)")
    summary: StatsHistorySummary = Field(description="기간 요약 통계")
    data: list[StatsHistoryItem] = Field(description="일별 학습 기록 목록")


class AccuracyByPeriod(SQLModel):
    """기간별 정확도 스키마."""

    all_time: float = Field(description="전체 기간 정확도 (%)")
    last_7_days: float | None = Field(
        default=None, description="최근 7일 정확도 (%). 데이터 없으면 null"
    )
    last_30_days: float | None = Field(
        default=None, description="최근 30일 정확도 (%). 데이터 없으면 null"
    )
    last_90_days: float | None = Field(
        default=None, description="최근 90일 정확도 (%). 데이터 없으면 null"
    )


class StatsAccuracyRead(SQLModel):
    """정확도 통계 응답 스키마."""

    overall_accuracy: float = Field(description="전체 정확도 (%)")
    total_reviews: int = Field(description="총 복습 횟수")
    total_correct: int = Field(description="총 정답 수")
    by_period: AccuracyByPeriod = Field(description="기간별 정확도 정보")
    by_cefr_level: dict[str, float] = Field(
        description='CEFR 레벨별 정확도 (%). 예: {"A1": 85.0, "A2": 78.5, "B1": 72.3}'
    )
    trend: str = Field(
        description="정확도 추세. 'improving'(상승), 'stable'(안정), 'declining'(하락). 최근 7일과 이전 7일 비교"
    )


class TodayVocabularyStats(SQLModel):
    """오늘의 어휘 학습 통계 스키마."""

    new_cards_count: int = Field(description="오늘 학습한 신규 카드 수")
    review_cards_count: int = Field(description="오늘 학습한 복습 카드 수")
    review_accuracy: float | None = Field(
        default=None, description="오늘 복습 카드의 정답률 (%). 복습 카드가 없으면 null"
    )
    progress: float = Field(description="일일 목표 대비 진행률 (0-100%)")
    daily_goal: int = Field(description="일일 학습 목표 카드 수")


class TodayStatsRead(SQLModel):
    """오늘의 학습 정보 응답 스키마."""

    total_study_time_seconds: int = Field(description="오늘 학습한 총 시간 (초 단위)")
    total_cards_studied: int = Field(description="오늘 학습한 총 문제 수")
    vocabulary: TodayVocabularyStats = Field(description="어휘 학습 상세 통계")
