"""
통계 관련 API 엔드포인트.

총 학습량, 학습 기록, 정확도 통계 등 학습 분석 데이터를 제공합니다.
"""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models.schemas.stats import (
    StatsAccuracyRead,
    StatsHistoryRead,
    TodayStatsRead,
    TotalLearnedRead,
)
from app.services.stats_service import StatsService

TAG = "stats"
TAG_METADATA = {
    "name": TAG,
    "description": "통계 관련 API. 총 학습량, 학습 기록, 정확도 통계 등 학습 분석 데이터를 제공합니다.",
}

router = APIRouter(prefix="/stats", tags=[TAG])


@router.get(
    "/total-learned",
    response_model=TotalLearnedRead,
    summary="총 학습량 통계",
    description="전체 학습 완료 카드 수와 CEFR 레벨별 분류를 반환합니다.",
    responses={
        200: {"description": "총 학습량 통계 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_total_learned(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    총 학습량 통계를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `total_learned`: 학습 완료한 총 카드 수 (REVIEW 상태)
    - `by_level`: CEFR 레벨별 학습 완료 카드 수 (A1, A2, B1, B2, C1, C2)
    - `total_study_time_minutes`: 총 학습 시간 (분)

    **학습 완료 기준:**
    - 카드 상태가 REVIEW인 카드 (FSRS 알고리즘에서 장기 기억으로 분류)
    """
    return await StatsService.get_total_learned(
        session,
        current_profile.id,
        current_profile.total_study_time_minutes,
    )


@router.get(
    "/history",
    response_model=StatsHistoryRead,
    summary="학습 기록 조회",
    description="기간별 일일 학습 기록을 반환합니다. 차트 데이터로 사용할 수 있습니다.",
    responses={
        200: {"description": "학습 기록 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_stats_history(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
    period: Literal["7d", "30d", "1y", "all"] = Query(
        default="30d",
        description="조회 기간. 7d(7일), 30d(30일), 1y(1년), all(전체) 중 선택",
    ),
):
    """
    기간별 학습 기록을 조회합니다.

    **인증 필요:** Bearer 토큰

    **쿼리 파라미터:**
    - `period`: 조회 기간
      - `7d`: 최근 7일
      - `30d`: 최근 30일 (기본값)
      - `1y`: 최근 1년
      - `all`: 전체 기간

    **반환 정보 (일별):**
    - `date`: 날짜
    - `cards_studied`: 학습한 카드 수
    - `correct_count`: 정답 수
    - `accuracy_rate`: 정확도 (%)
    - `study_time_seconds`: 학습 시간 (초)

    **반환 정보 (요약):**
    - `total_study_time_seconds`: 기간 내 총 학습 시간
    - `total_cards_studied`: 기간 내 총 학습 카드 수
    - `avg_daily_study_time_seconds`: 하루 평균 학습 시간 (활동 일수 기준)
    - `avg_daily_cards_studied`: 하루 평균 학습 카드 수 (활동 일수 기준)
    - `days_with_activity`: 활동이 있었던 일수

    **용도:**
    - 학습 추이 그래프
    - 일별 학습량 비교
    - 평균 통계 표시
    """
    return await StatsService.get_stats_history(session, current_profile.id, period)


@router.get(
    "/accuracy",
    response_model=StatsAccuracyRead,
    summary="정확도 통계",
    description="전체 정확도, 기간별 정확도, CEFR 레벨별 정확도를 반환합니다.",
    responses={
        200: {"description": "정확도 통계 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_stats_accuracy(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    정확도 통계를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `overall_accuracy`: 전체 정확도 (%)
    - `total_reviews`: 총 복습 횟수
    - `total_correct`: 총 정답 수
    - `by_period`: 기간별 정확도
      - `all_time`: 전체 기간
      - `last_7_days`: 최근 7일
      - `last_30_days`: 최근 30일
      - `last_90_days`: 최근 90일
    - `by_cefr_level`: CEFR 레벨별 정확도 (A1~C2)
    - `trend`: 추세 ("improving", "stable", "declining")

    **추세 계산 기준:**
    - 최근 7일 정확도와 그 이전 7일 정확도 비교
    - 5% 이상 상승: improving
    - 5% 이상 하락: declining
    - 그 외: stable
    """
    return await StatsService.get_stats_accuracy(session, current_profile.id)


@router.get(
    "/today",
    response_model=TodayStatsRead,
    summary="오늘의 학습 정보",
    description="오늘 하루 동안의 학습 통계를 반환합니다. 총 학습 시간, 학습 문제 수, 신규/복습 카드 수, 정답률, 일일 목표 진행률 등을 포함합니다.",
    responses={
        200: {"description": "오늘의 학습 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_today_stats(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    오늘의 학습 정보를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `total_study_time_seconds`: 오늘 학습한 총 시간 (초 단위)
    - `total_cards_studied`: 오늘 학습한 총 문제 수
    - `vocabulary`: 어휘 학습 상세 통계
      - `new_cards_count`: 오늘 학습한 신규 카드 수
      - `review_cards_count`: 오늘 학습한 복습 카드 수
      - `review_accuracy`: 오늘 복습 카드의 정답률 (%, 복습 카드가 없으면 null)
      - `progress`: 일일 목표 대비 진행률 (0-100%)
      - `daily_goal`: 일일 학습 목표 카드 수

    **오늘 기준:**
    - UTC 기준 오늘 날짜 (00:00:00 ~ 23:59:59)
    """
    return await StatsService.get_today_stats(
        session,
        current_profile.id,
        current_profile.daily_goal,
    )
