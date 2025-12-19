"""
프로필 관련 API 엔드포인트.

프로필 조회/수정, 학습 설정, 스트릭 정보, 레벨 정보 등 사용자 데이터를 관리합니다.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models import (
    DailyGoalRead,
    Profile,
    ProfileConfigRead,
    ProfileConfigUpdate,
    ProfileLevelRead,
    ProfileRead,
    ProfileUpdate,
    StreakRead,
    TodayProgressRead,
)
from app.services.profile_service import ProfileService
from app.services.user_card_progress_service import UserCardProgressService

TAG = "profiles"
TAG_METADATA = {
    "name": TAG,
    "description": "프로필 관련 API. 프로필 조회/수정, 학습 설정, 스트릭 정보, 레벨 정보 등 사용자 데이터를 관리합니다.",
}

router = APIRouter(prefix="/profiles", tags=[TAG])


@router.get(
    "/me",
    response_model=ProfileRead,
    summary="내 프로필 조회",
    description="현재 인증된 사용자의 프로필 정보를 반환합니다.",
    responses={
        200: {"description": "프로필 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_current_profile(
    current_profile: CurrentActiveProfile,
) -> Profile:
    """
    현재 인증된 사용자의 프로필을 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - 기본 정보: ID (UUID)
    - 학습 설정: 일일 목표, 덱 선택 설정, 테마
    - 스트릭: 현재/최장 연속 학습일
    - 통계: 총 학습 시간
    """
    return current_profile


@router.get(
    "/me/today-progress",
    response_model=TodayProgressRead,
    summary="오늘의 학습 진행 상황",
    description="오늘 학습한 카드 수와 일일 목표 달성률을 반환합니다.",
    responses={
        200: {"description": "오늘의 학습 진행 상황 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_today_progress(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
):
    """
    오늘의 학습 진행 상황을 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `total_reviews`: 오늘 총 복습 횟수
    - `correct_count`: 오늘 정답 수
    - `wrong_count`: 오늘 오답 수
    - `accuracy_rate`: 오늘 정확도 (%)
    - `daily_goal`: 일일 목표 카드 수
    - `goal_progress`: 목표 달성률 (%)
    """
    progress_data = await UserCardProgressService.get_today_progress(
        session, current_profile.id, current_profile.daily_goal
    )
    return TodayProgressRead(**progress_data)


@router.get(
    "/me/daily-goal",
    response_model=DailyGoalRead,
    summary="일일 목표 조회",
    description="사용자의 일일 학습 목표와 오늘 완료한 카드 수를 반환합니다.",
    responses={
        200: {"description": "일일 목표 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "프로필을 찾을 수 없음"},
    },
)
async def get_daily_goal(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> dict:
    """
    일일 학습 목표 정보를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `daily_goal`: 설정된 일일 목표 카드 수
    - `completed_today`: 오늘 학습 완료한 카드 수
    """
    daily_goal_data = await ProfileService.get_daily_goal(session, current_profile.id)
    if not daily_goal_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return daily_goal_data


@router.get(
    "/me/config",
    response_model=ProfileConfigRead,
    summary="사용자 설정 조회",
    description="사용자의 학습 설정 및 앱 설정을 반환합니다.",
    responses={
        200: {"description": "사용자 설정 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_profile_config(
    current_profile: CurrentActiveProfile,
) -> ProfileConfigRead:
    """
    사용자 설정을 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `daily_goal`: 일일 학습 목표 카드 수
    - `select_all_decks`: 전체 덱 선택 여부
    - `timezone`: 사용자 타임존
    - `theme`: 앱 테마 (light/dark/auto)
    - `notification_enabled`: 알림 활성화 여부
    """
    return ProfileConfigRead(
        daily_goal=current_profile.daily_goal,
        select_all_decks=current_profile.select_all_decks,
        review_ratio_mode=current_profile.review_ratio_mode,
        custom_review_ratio=current_profile.custom_review_ratio,
        min_new_ratio=current_profile.min_new_ratio,
        review_scope=current_profile.review_scope,
        timezone=current_profile.timezone,
        theme=current_profile.theme,
        notification_enabled=current_profile.notification_enabled,
        highlight_color=current_profile.highlight_color,
    )


@router.put(
    "/me/config",
    response_model=ProfileConfigRead,
    summary="사용자 설정 수정",
    description="사용자의 학습 설정 및 앱 설정을 수정합니다. 부분 업데이트를 지원합니다.",
    responses={
        200: {"description": "설정 수정 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 잘못된 값 (예: theme이 허용되지 않는 값)"},
    },
)
async def update_profile_config(
    config_data: ProfileConfigUpdate,
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileConfigRead:
    """
    사용자 설정을 수정합니다.

    **인증 필요:** Bearer 토큰

    **부분 업데이트:** 변경하고 싶은 필드만 전송하면 됩니다.

    **수정 가능한 필드:**
    - `daily_goal`: 1~1000 사이의 정수
    - `select_all_decks`: true/false
    - `timezone`: 타임존 문자열 (예: "Asia/Seoul")
    - `theme`: "light", "dark", "auto" 중 하나
    - `notification_enabled`: true/false
    """
    update_data = config_data.model_dump(exclude_unset=True)
    updated_profile = await ProfileService.update_profile_config(
        session, current_profile, update_data
    )

    return ProfileConfigRead(
        daily_goal=updated_profile.daily_goal,
        select_all_decks=updated_profile.select_all_decks,
        review_ratio_mode=updated_profile.review_ratio_mode,
        custom_review_ratio=updated_profile.custom_review_ratio,
        min_new_ratio=updated_profile.min_new_ratio,
        review_scope=updated_profile.review_scope,
        timezone=updated_profile.timezone,
        theme=updated_profile.theme,
        notification_enabled=updated_profile.notification_enabled,
        highlight_color=updated_profile.highlight_color,
    )


@router.get(
    "/me/level",
    response_model=ProfileLevelRead,
    summary="사용자 레벨 조회",
    description="사용자의 학습 숙련도 레벨과 CEFR 등급을 계산하여 반환합니다.",
    responses={
        200: {"description": "레벨 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_profile_level(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProfileLevelRead:
    """
    사용자의 학습 숙련도 레벨을 조회합니다.

    **인증 필요:** Bearer 토큰

    **계산 기준:**
    - 최근 50회 복습 결과
    - 전체 정확도
    - 마스터한 카드의 난이도 분포

    **반환 정보:**
    - `level`: 숙련도 레벨 (1.0 ~ 10.0)
    - `cefr_equivalent`: CEFR 등급 (A1, A2, B1, B2, C1, C2)
    - `total_reviews`: 총 복습 횟수
    - `accuracy_rate`: 전체 정확도 (%)
    - `mastered_cards`: 마스터한 카드 수
    """
    level_data = await ProfileService.calculate_profile_level(session, current_profile.id)
    return ProfileLevelRead(**level_data)


@router.patch(
    "/me",
    response_model=ProfileRead,
    summary="프로필 정보 수정",
    description="프로필 정보를 수정합니다.",
    responses={
        200: {"description": "프로필 정보 수정 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 잘못된 데이터 형식"},
    },
)
async def update_profile(
    profile_data: ProfileUpdate,
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    프로필 정보를 수정합니다.

    **인증 필요:** Bearer 토큰

    **수정 가능한 필드:**
    - `daily_goal`: 일일 목표 (1~1000)
    - `select_all_decks`: 전체 덱 선택 여부
    - `timezone`: 타임존
    - `theme`: 테마 (light/dark/auto)
    - `notification_enabled`: 알림 설정
    """
    profile = await ProfileService.update_profile(session, current_profile.id, profile_data)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return profile


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="프로필 삭제",
    description="프로필을 삭제합니다.",
    responses={
        204: {"description": "프로필 삭제 성공 (응답 본문 없음)"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "프로필을 찾을 수 없음"},
    },
)
async def delete_profile(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    프로필을 삭제합니다.

    **인증 필요:** Bearer 토큰

    **주의사항:**
    - 이 작업은 되돌릴 수 없습니다
    - 사용자의 모든 학습 데이터가 함께 삭제됩니다
    - Supabase Auth 계정은 별도로 삭제해야 합니다
    """
    success = await ProfileService.delete_profile(session, current_profile.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )
    return None


@router.get(
    "/me/streak",
    response_model=StreakRead,
    summary="스트릭 정보 조회",
    description="사용자의 연속 학습 스트릭 정보와 이번 달 학습 통계를 반환합니다.",
    responses={
        200: {"description": "스트릭 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_profile_streak(
    current_profile: CurrentActiveProfile,
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    스트릭 정보를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `current_streak`: 현재 연속 학습일 수
    - `longest_streak`: 최장 연속 학습일 수
    - `last_study_date`: 마지막 학습 날짜
    - `days_studied_this_month`: 이번 달 학습한 일수
    - `streak_status`: 스트릭 상태 ("active" 또는 "broken")
    - `message`: 사용자에게 표시할 동기 부여 메시지
    """
    streak_data = await ProfileService.get_profile_streak(session, current_profile)
    return StreakRead(**streak_data)
