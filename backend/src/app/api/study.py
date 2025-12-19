"""
학습 세션 관련 API 엔드포인트.

학습 세션 시작/완료, 카드 조회, 정답 제출을 관리합니다.
퀴즈 기능이 통합되어 FSRS 업데이트, 스트릭, 일일 목표, XP가 모두 반영됩니다.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models import (
    AnswerRequest,
    AnswerResponse,
    CardRequest,
    CardResponse,
    SessionAbandonRequest,
    SessionAbandonResponse,
    SessionCompleteRequest,
    SessionCompleteResponse,
    SessionPreviewRequest,
    SessionPreviewResponse,
    SessionStartRequest,
    SessionStartResponse,
    SessionStatusResponse,
    StudyOverviewResponse,
    UserCardProgressRead,
    WrongAnswerReviewedResponse,
    WrongAnswersResponse,
    WrongReviewSessionRequest,
    WrongReviewSessionResponse,
)
from app.models.schemas.study import (
    PronunciationEvaluateRequest,
    PronunciationEvaluateResponse,
)
from app.services.pronunciation_service import PronunciationService
from app.services.study_session_service import StudySessionService
from app.services.user_card_progress_service import UserCardProgressService
from app.services.vocabulary_card_service import VocabularyCardService
from app.services.wrong_answer_service import WrongAnswerService

TAG = "study"
TAG_METADATA = {
    "name": TAG,
    "description": """학습 세션 및 학습 현황 관련 API. 퀴즈 기능이 통합되어 FSRS, 스트릭, XP가 모두 반영됩니다.

**학습 현황 조회:**
- `GET /overview` → 신규/복습 카드 수 + 복습 예정 카드 목록
- `GET /cards/{card_id}` → 개별 카드 FSRS 진행 상세

**세션 플로우:**
1. `POST /session/start` → session_id 발급
2. `POST /session/card` → quiz_type 지정하여 카드 조회 (반복)
3. `POST /session/answer` → 정답 제출, FSRS 자동 업데이트 (반복)
4. `POST /session/complete` → 세션 완료, XP/스트릭/일일목표 반영

**퀴즈 유형:** word_to_meaning, meaning_to_word, cloze, listening""",
}

router = APIRouter(prefix="/study", tags=[TAG])


@router.post(
    "/session/preview",
    response_model=SessionPreviewResponse,
    summary="학습 세션 프리뷰",
    description="세션 설정에 따른 카드 배정을 미리 확인합니다. 총 카드 수와 복습 비율을 입력하면 실제 배정될 카드 구성을 반환합니다.",
    responses={
        200: {"description": "프리뷰 조회 성공. 사용 가능한 카드와 배정 결과 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 잘못된 파라미터 값"},
    },
)
async def preview_study_session(
    request: SessionPreviewRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> SessionPreviewResponse:
    """
    학습 세션 프리뷰를 조회합니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `total_cards`: 총 학습할 카드 수 (1~150)
    - `review_ratio`: 복습 카드 비율 (0.0~1.0)
      - 예: 0.6 = 60% 복습, 40% 신규

    **반환 정보:**
    - `available`: 현재 사용 가능한 카드 수
      - `new_cards`: 사용 가능한 신규 카드 수
      - `review_cards`: 복습 예정 카드 수
      - `relearning_cards`: 재학습 카드 수
    - `allocation`: 설정에 따른 카드 배정
      - `new_cards`: 배정될 신규 카드 수
      - `review_cards`: 배정될 복습 카드 수 (재학습 포함)
      - `total`: 총 배정 카드 수
    - `message`: 경고 메시지 (카드 부족 시)

    **사용 시나리오:**
    - 모달에서 사용자가 단어 개수/복습 비율 조정 시 실시간 프리뷰
    - "새로운 단어 8개 + 복습할 단어 12개" 미리보기
    """
    return await StudySessionService.preview_session(
        session=session,
        user_id=current_profile.id,
        total_cards=request.total_cards,
        review_ratio=request.review_ratio,
    )


@router.post(
    "/session/start",
    response_model=SessionStartResponse,
    summary="학습 세션 시작",
    description="새로운 학습 세션을 시작합니다. 카드 목록은 /session/card에서 개별 조회합니다.",
    responses={
        200: {"description": "세션 시작 성공. 세션 ID와 카드 수 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 잘못된 파라미터 값"},
    },
)
async def start_study_session(
    request: SessionStartRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> SessionStartResponse:
    """
    새로운 학습 세션을 시작합니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `new_cards_limit`: 신규 카드 최대 수 (기본값: 10, 최대: 50)
    - `review_cards_limit`: 복습 카드 최대 수 (기본값: 20, 최대: 100)

    **카드 구성:**
    - 신규 카드: 사용 빈도순으로 정렬하여 제공
    - 복습 카드: 복습 예정일이 지난 카드 우선

    **반환 정보:**
    - `session_id`: 세션 식별용 UUID (이후 API 호출에 사용)
    - `total_cards`: 총 카드 수
    - `new_cards_count`: 신규 카드 수
    - `review_cards_count`: 복습 카드 수
    - `started_at`: 세션 시작 시간

    **다음 단계:**
    1. `/session/card`로 카드 조회 (quiz_type 지정)
    2. `/session/answer`로 정답 제출
    3. 모든 카드 완료 후 `/session/complete`로 세션 종료
    """
    return await StudySessionService.start_session(
        session=session,
        user_id=current_profile.id,
        new_cards_limit=request.new_cards_limit,
        review_cards_limit=request.review_cards_limit,
        use_profile_ratio=request.use_profile_ratio,
    )


@router.post(
    "/session/card",
    response_model=CardResponse,
    summary="다음 카드 조회",
    description="세션에서 다음 학습할 카드를 조회합니다. 퀴즈 유형을 지정하여 포맷팅된 문제를 받습니다.",
    responses={
        200: {"description": "카드 조회 성공. 포맷팅된 문제와 선택지 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "세션을 찾을 수 없음"},
        422: {"description": "유효성 검사 실패"},
    },
)
async def get_next_card(
    request: CardRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> CardResponse:
    """
    다음 학습할 카드를 조회합니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `session_id`: 세션 UUID
    - `quiz_type`: 퀴즈 유형
      - `word_to_meaning`: 영어 단어 → 한글 뜻 선택
      - `meaning_to_word`: 한글 뜻 → 영어 단어 선택
      - `cloze`: 빈칸 채우기 (예문에서 단어 맞추기)
      - `listening`: 발음 듣고 단어 선택

    **반환 정보:**
    - `card`: 포맷팅된 카드 정보
      - `id`: 카드 ID
      - `quiz_type`: 적용된 퀴즈 유형
      - `question`: 문제 (텍스트 또는 ClozeQuestion)
      - `options`: 선택지 목록 (4개)
      - 기타 카드 정보 (is_new, audio_url 등)
    - `cards_remaining`: 남은 카드 수
    - `cards_completed`: 완료한 카드 수

    **세션 완료 시:**
    - `card`가 `null`로 반환됨
    - `/session/complete`를 호출하여 세션 종료
    """
    return await StudySessionService.get_next_card(
        session=session,
        user_id=current_profile.id,
        session_id=request.session_id,
        quiz_type=request.quiz_type,
    )


@router.post(
    "/session/answer",
    response_model=AnswerResponse,
    summary="정답 제출",
    description="카드에 대한 정답을 제출합니다. FSRS가 자동으로 업데이트됩니다.",
    responses={
        200: {"description": "정답 처리 성공. 정오답 결과와 FSRS 업데이트 정보 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "세션 또는 카드를 찾을 수 없음"},
        422: {"description": "유효성 검사 실패"},
    },
)
async def submit_answer(
    request: AnswerRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> AnswerResponse:
    """
    카드에 대한 정답을 제출합니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `session_id`: 세션 UUID
    - `card_id`: 카드 ID
    - `answer`: 사용자 답변
    - `response_time_ms`: 응답 시간 (밀리초, 선택)
    - `hint_count`: 사용한 힌트 횟수 (0=미사용, 선택)
    - `revealed_answer`: 정답 공개 여부 (선택)

    **처리 내용:**
    1. 정답 확인
    2. 힌트 사용에 따른 점수 계산 (기본 100점, 힌트당 -20점)
    3. FSRS 알고리즘으로 다음 복습 일정 계산 (힌트 사용 시 Hard로 처리)
    4. 세션 통계 업데이트 (정답/오답 수)

    **반환 정보:**
    - `card_id`: 카드 ID
    - `is_correct`: 정답 여부
    - `correct_answer`: 정답
    - `user_answer`: 사용자 답변
    - `feedback`: 피드백 메시지
    - `score`: 획득 점수 (0~100)
    - `hint_penalty`: 힌트로 인한 감점
    - `next_review_date`: 다음 복습 예정일 (FSRS 계산)
    - `card_state`: 카드 상태 (NEW/LEARNING/REVIEW/RELEARNING)

    **FSRS 업데이트:**
    - 정답 (힌트 미사용): Rating 3 (Good) 적용
    - 정답 (힌트 사용): Rating 2 (Hard) 적용
    - 오답 또는 정답 공개: Rating 1 (Again) 적용
    """
    return await StudySessionService.submit_answer(
        session=session,
        user_id=current_profile.id,
        session_id=request.session_id,
        card_id=request.card_id,
        user_answer=request.answer,
        response_time_ms=request.response_time_ms,
        hint_count=request.hint_count,
        revealed_answer=request.revealed_answer,
        quiz_type=request.quiz_type,
    )


@router.post(
    "/session/complete",
    response_model=SessionCompleteResponse,
    summary="학습 세션 완료",
    description="학습 세션을 완료하고 스트릭, 일일 목표, XP를 업데이트합니다.",
    responses={
        200: {"description": "세션 완료 성공. 세션 요약, 스트릭, 일일 목표, XP 반환"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "세션을 찾을 수 없음"},
        422: {"description": "유효성 검사 실패"},
    },
)
async def complete_study_session(
    request: SessionCompleteRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> SessionCompleteResponse:
    """
    학습 세션을 완료합니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `session_id`: 세션 UUID
    - `duration_seconds`: 총 학습 시간 (초)

    **처리 내용:**
    1. 세션 상태를 COMPLETED로 변경
    2. 스트릭 업데이트 (연속 학습일)
    3. 총 학습 시간 누적
    4. 일일 목표 진행 상황 업데이트
    5. XP 계산 및 적용

    **반환 정보:**
    - `session_summary`: 세션 결과 요약
      - `total_cards`: 총 카드 수
      - `correct_count`: 정답 수
      - `wrong_count`: 오답 수
      - `accuracy_rate`: 정확도 (%)
      - `duration_seconds`: 학습 시간 (초)
    - `streak`: 스트릭 정보
      - `current_streak`: 현재 스트릭
      - `longest_streak`: 최장 스트릭
      - `is_new_record`: 신기록 여부
    - `daily_goal`: 일일 목표 상태
      - `goal`: 목표 카드 수
      - `completed`: 완료 카드 수
      - `progress_percentage`: 진행률
      - `is_achieved`: 달성 여부
    - `xp`: XP 정보
      - `base_xp`: 기본 XP (정답당 10XP)
      - `bonus_xp`: 보너스 XP (80% 이상 시 +50XP)
      - `total_xp`: 총 획득 XP
    """
    return await StudySessionService.complete_session(
        session=session,
        user_id=current_profile.id,
        session_id=request.session_id,
    )


# ============================================================
# Session Status & Abandon (Issue #54)
# ============================================================


@router.get(
    "/session/{session_id}/status",
    response_model=SessionStatusResponse,
    summary="세션 상태 조회",
    description="현재 세션의 진행 상황과 일일 목표 정보를 조회합니다.",
    responses={
        200: {"description": "세션 상태 조회 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "세션을 찾을 수 없음"},
    },
)
async def get_session_status(
    session_id: UUID = Path(description="세션 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> SessionStatusResponse:
    """
    현재 세션의 상태를 조회합니다.

    **인증 필요:** Bearer 토큰

    **파라미터:**
    - `session_id`: 세션 UUID

    **반환 정보:**
    - `session_id`: 세션 ID
    - `status`: 세션 상태 (active/completed/abandoned)
    - `total_cards`: 총 카드 수
    - `completed_cards`: 완료한 카드 수
    - `remaining_cards`: 남은 카드 수
    - `correct_count`: 정답 수
    - `wrong_count`: 오답 수
    - `started_at`: 시작 시간
    - `elapsed_seconds`: 경과 시간 (초)
    - `daily_goal`: 일일 목표 정보
      - `goal`: 목표 카드 수
      - `completed_today`: 오늘 완료한 카드 수
      - `remaining_for_goal`: 목표까지 남은 카드 수
      - `will_complete_goal`: 현재 세션 완료 시 목표 달성 여부
    """
    return await StudySessionService.get_session_status(
        session=session,
        user_id=current_profile.id,
        session_id=session_id,
    )


@router.post(
    "/session/{session_id}/abandon",
    response_model=SessionAbandonResponse,
    summary="세션 중단",
    description="학습 세션을 중단합니다. 지금까지의 진행 상황은 저장됩니다.",
    responses={
        200: {"description": "세션 중단 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "세션을 찾을 수 없음"},
        422: {"description": "유효성 검사 실패 - 이미 완료된 세션"},
    },
)
async def abandon_session(
    request: SessionAbandonRequest,
    session_id: UUID = Path(description="세션 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> SessionAbandonResponse:
    """
    학습 세션을 중단합니다.

    **인증 필요:** Bearer 토큰

    **파라미터:**
    - `session_id`: 세션 UUID

    **요청 본문:**
    - `save_progress`: 진행 상황 저장 여부 (기본값: true, 항상 true 권장)

    **반환 정보:**
    - `session_id`: 세션 ID
    - `status`: 세션 상태 (abandoned)
    - `summary`: 세션 요약
      - `total_cards`: 총 카드 수
      - `completed_cards`: 완료한 카드 수
      - `correct_count`: 정답 수
      - `wrong_count`: 오답 수
      - `duration_seconds`: 학습 시간 (초)
    - `progress_saved`: 진행 상황 저장 여부
    - `message`: 안내 메시지
    """
    return await StudySessionService.abandon_session(
        session=session,
        user_id=current_profile.id,
        session_id=session_id,
        save_progress=request.save_progress,
    )


# ============================================================
# Study Overview Endpoints
# ============================================================


@router.get(
    "/overview",
    response_model=StudyOverviewResponse,
    summary="학습 현황 개요",
    description="신규/복습 카드 수와 복습 예정 카드 목록, 일일 목표 진행 상황을 반환합니다.",
    responses={
        200: {"description": "학습 현황 조회 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_study_overview(
    limit: int = Query(default=50, ge=1, le=100, description="복습 예정 카드 최대 수 (1~100)"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> StudyOverviewResponse:
    """
    학습 현황 개요를 조회합니다.

    **인증 필요:** Bearer 토큰

    **쿼리 파라미터:**
    - `limit`: 복습 예정 카드 최대 수 (기본값: 50, 최대: 100)

    **반환 정보:**
    - `new_cards_count`: 학습 가능한 신규 카드 수
    - `review_cards_count`: 복습 예정 카드 수
    - `total_available`: 총 학습 가능 카드 수
    - `due_cards`: 복습 예정 카드 목록
      - `card_id`: 카드 ID
      - `english_word`: 영어 단어
      - `korean_meaning`: 한국어 뜻
      - `next_review_date`: 다음 복습 예정일
      - `card_state`: 카드 상태
    - `daily_goal`: 일일 목표 진행 상황
      - `goal`: 설정된 일일 목표 카드 수
      - `completed`: 오늘 완료한 카드 수
      - `progress`: 진행률 (%)
      - `is_completed`: 목표 달성 여부

    **사용 시나리오:**
    - 대시보드에서 "오늘 학습할 카드: 신규 15개 + 복습 8개" 표시
    - 세션 시작 전 학습 가능한 카드 미리보기
    - "오늘의 학습 미완료" 여부 판단
    """
    return await StudySessionService.get_overview(
        session=session,
        user_id=current_profile.id,
        limit=limit,
    )


@router.get(
    "/cards/{card_id}",
    response_model=UserCardProgressRead,
    summary="개별 카드 진행 조회",
    description="특정 카드의 FSRS 학습 진행 상세를 조회합니다.",
    responses={
        200: {"description": "카드 진행 조회 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "해당 카드의 학습 기록을 찾을 수 없음"},
    },
)
async def get_card_progress(
    card_id: int = Path(description="조회할 카드의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> UserCardProgressRead:
    """
    특정 카드의 학습 진행 상황을 조회합니다.

    **인증 필요:** Bearer 토큰

    **파라미터:**
    - `card_id`: 조회할 카드의 ID

    **반환 정보:**
    - FSRS 파라미터: stability, difficulty, interval
    - 카드 상태: NEW, LEARNING, REVIEW, RELEARNING
    - 통계: 총 복습 횟수, 정확도, 연속 정답 수
    - 일정: 다음 복습일, 마지막 복습일
    """
    progress = await UserCardProgressService.get_user_card_progress(
        session, current_profile.id, card_id
    )
    if not progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Progress not found for this card",
        )
    return progress


# ============================================================
# Wrong Answer Endpoints (Issue #53)
# ============================================================


@router.get(
    "/wrong-answers",
    response_model=WrongAnswersResponse,
    summary="오답 기록 목록 조회",
    description="사용자의 오답 기록 목록을 조회합니다.",
    responses={
        200: {"description": "오답 기록 조회 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_wrong_answers(
    limit: int = Query(default=20, ge=1, le=100, description="조회할 오답 수 (1~100)"),
    offset: int = Query(default=0, ge=0, description="페이지네이션 오프셋"),
    reviewed: bool | None = Query(
        default=None, description="복습 여부 필터 (true/false/null=전체)"
    ),
    quiz_type: str | None = Query(default=None, description="퀴즈 유형 필터"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> WrongAnswersResponse:
    """
    오답 기록 목록을 조회합니다.

    **인증 필요:** Bearer 토큰

    **쿼리 파라미터:**
    - `limit`: 조회할 오답 수 (기본값: 20)
    - `offset`: 페이지네이션 오프셋 (기본값: 0)
    - `reviewed`: 복습 여부 필터 (true=복습완료, false=미복습, null=전체)
    - `quiz_type`: 퀴즈 유형 필터 (word_to_meaning/meaning_to_word/cloze/listening)

    **반환 정보:**
    - `wrong_answers`: 오답 기록 목록
    - `total`: 전체 오답 수
    - `unreviewed_count`: 미복습 오답 수
    """
    return await WrongAnswerService.get_wrong_answers(
        session=session,
        user_id=current_profile.id,
        limit=limit,
        offset=offset,
        reviewed=reviewed,
        quiz_type=quiz_type,
    )


@router.patch(
    "/wrong-answers/{wrong_answer_id}/reviewed",
    response_model=WrongAnswerReviewedResponse,
    summary="오답 복습 완료 표시",
    description="오답 기록을 복습 완료로 표시합니다.",
    responses={
        200: {"description": "복습 완료 표시 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "오답 기록을 찾을 수 없음"},
    },
)
async def mark_wrong_answer_reviewed(
    wrong_answer_id: int = Path(description="오답 기록 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> WrongAnswerReviewedResponse:
    """
    오답 기록을 복습 완료로 표시합니다.

    **인증 필요:** Bearer 토큰

    **파라미터:**
    - `wrong_answer_id`: 오답 기록 ID

    **반환 정보:**
    - `id`: 오답 기록 ID
    - `reviewed`: 복습 완료 여부 (true)
    - `reviewed_at`: 복습 완료 시간
    """
    result = await WrongAnswerService.mark_reviewed(
        session=session,
        user_id=current_profile.id,
        wrong_answer_id=wrong_answer_id,
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Wrong answer not found",
        )
    return result


@router.post(
    "/session/start-wrong-review",
    response_model=WrongReviewSessionResponse,
    summary="오답 재학습 세션 시작",
    description="미복습 오답 카드로 재학습 세션을 시작합니다.",
    responses={
        200: {"description": "오답 재학습 세션 시작 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def start_wrong_review_session(
    request: WrongReviewSessionRequest,
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> WrongReviewSessionResponse:
    """
    미복습 오답 카드로 재학습 세션을 시작합니다.

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `limit`: 재학습할 카드 수 (기본값: 10, 최대: 50)

    **반환 정보:**
    - `session_id`: 세션 ID
    - `total_cards`: 총 카드 수
    - `cards_from_wrong_answers`: 오답 카드 기반 세션 여부 (항상 true)
    - `started_at`: 세션 시작 시간

    **다음 단계:**
    - `/session/card`로 카드 조회 (quiz_type 지정)
    - `/session/answer`로 정답 제출
    - 모든 카드 완료 후 `/session/complete`로 세션 종료
    """
    # Get unreviewed wrong answer card IDs
    card_ids = await WrongAnswerService.get_unreviewed_card_ids(
        session=session,
        user_id=current_profile.id,
        limit=request.limit,
    )

    if not card_ids:
        # Return empty session if no wrong answers
        from datetime import datetime

        return WrongReviewSessionResponse(
            session_id="00000000-0000-0000-0000-000000000000",
            total_cards=0,
            cards_from_wrong_answers=True,
            started_at=datetime.utcnow(),
        )

    # Start session with wrong answer cards
    session_response = await StudySessionService.start_session_with_cards(
        session=session,
        user_id=current_profile.id,
        card_ids=card_ids,
    )

    return WrongReviewSessionResponse(
        session_id=session_response.session_id,
        total_cards=session_response.total_cards,
        cards_from_wrong_answers=True,
        started_at=session_response.started_at,
    )


# ============================================================
# Pronunciation Evaluation (Issue #56)
# ============================================================


@router.post(
    "/pronunciation/evaluate",
    response_model=PronunciationEvaluateResponse,
    summary="발음 평가 (Mock)",
    description="사용자의 발음을 평가합니다. 현재 MVP 버전으로 Mock 데이터를 반환합니다.",
    responses={
        200: {"description": "발음 평가 완료"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "카드를 찾을 수 없음"},
        422: {"description": "card_id 또는 word 중 하나는 필수"},
    },
)
async def evaluate_pronunciation(
    request: PronunciationEvaluateRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
) -> PronunciationEvaluateResponse:
    """
    발음을 평가합니다 (MVP Mock 버전).

    **인증 필요:** Bearer 토큰

    **요청 본문:**
    - `card_id`: 평가할 단어의 카드 ID (선택)
    - `word`: 평가할 단어 (card_id 없을 경우 사용)

    **참고:**
    - 현재 MVP 버전으로 Mock 점수와 피드백을 반환합니다.
    - 추후 Azure/Google Speech API 연동 예정입니다.

    **점수 등급:**
    - 90-100: excellent (완벽해요!)
    - 75-89: good (좋아요!)
    - 60-74: fair (조금 더 연습해요)
    - 0-59: needs_practice (다시 도전해보세요)
    """
    # Validate request
    if not request.card_id and not request.word:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="card_id 또는 word 중 하나는 필수입니다.",
        )

    # If card_id provided, get card info and use service
    if request.card_id:
        card = await VocabularyCardService.get_card(session, request.card_id)
        if not card:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="카드를 찾을 수 없습니다.",
            )
        return PronunciationService.evaluate_from_card(card)

    # Otherwise, evaluate with just the word
    return PronunciationService.evaluate_pronunciation(
        card_id=None,
        word=request.word,
    )
