"""학습 세션 관련 스키마."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.enums import CardState, QuizType


class ClozeQuestion(SQLModel):
    """빈칸 채우기 문제 스키마."""

    sentence: str = Field(
        description="빈칸이 포함된 문장 (예: 'The company signed a _____ with...')"
    )
    answer: str = Field(description="정답 단어 (예: 'contract')")
    hint: str | None = Field(default=None, description="힌트 (예: '계약')")
    audio_url: str | None = Field(default=None, description="듣기 모드용 오디오 URL")


# ============================================================
# Session Start
# ============================================================


class SessionStartRequest(SQLModel):
    """학습 세션 시작 요청 스키마."""

    new_cards_limit: int = Field(
        default=30, ge=0, le=50, description="포함할 최대 신규 카드 수 (0~50)"
    )
    review_cards_limit: int = Field(
        default=30, ge=0, le=100, description="포함할 최대 복습 카드 수 (0~100)"
    )
    use_profile_ratio: bool = Field(
        default=True,
        description="true면 프로필의 학습 비율/목표로 카드 구성을 계산합니다. false면 new_cards_limit/review_cards_limit를 그대로 사용합니다.",
    )


class SessionStartResponse(SQLModel):
    """학습 세션 시작 응답 스키마."""

    session_id: UUID = Field(description="세션 식별용 UUID")
    total_cards: int = Field(description="이 세션에 포함된 총 카드 수")
    new_cards_count: int = Field(description="신규 카드 수")
    review_cards_count: int = Field(description="복습 카드 수")
    started_at: datetime = Field(description="세션 시작 시간 (UTC)")


# ============================================================
# Session Preview
# ============================================================


class SessionPreviewRequest(SQLModel):
    """학습 세션 프리뷰 요청 스키마."""

    total_cards: int = Field(ge=1, le=150, description="총 학습할 카드 수 (1~150)")
    review_ratio: float = Field(ge=0.0, le=1.0, description="복습 카드 비율 (0.0~1.0)")


class SessionPreviewAvailable(SQLModel):
    """현재 사용 가능한 카드 수."""

    new_cards: int = Field(ge=0, description="사용 가능한 신규 카드 수")
    review_cards: int = Field(ge=0, description="사용 가능한 복습 예정 카드 수 (재학습 제외)")
    relearning_cards: int = Field(ge=0, description="사용 가능한 재학습 카드 수")


class SessionPreviewAllocation(SQLModel):
    """요청 설정에 따른 카드 배정 결과."""

    new_cards: int = Field(ge=0, description="배정될 신규 카드 수")
    review_cards: int = Field(ge=0, description="배정될 복습 카드 수 (재학습 포함)")
    total: int = Field(ge=0, description="총 배정 카드 수")


# Backward-compatible aliases (older tests / callers)
class AvailableCards(SessionPreviewAvailable):
    """Alias of SessionPreviewAvailable."""


class CardAllocation(SessionPreviewAllocation):
    """Alias of SessionPreviewAllocation."""


class SessionPreviewResponse(SQLModel):
    """학습 세션 프리뷰 응답 스키마."""

    available: SessionPreviewAvailable = Field(description="현재 사용 가능한 카드 수")
    allocation: SessionPreviewAllocation = Field(description="카드 배정 결과")
    message: str | None = Field(default=None, description="경고/안내 메시지 (카드 부족 등)")


# ============================================================
# Card Request/Response
# ============================================================


class CardRequest(SQLModel):
    """다음 카드 요청 스키마."""

    session_id: UUID = Field(description="세션 ID")
    quiz_type: QuizType = Field(description="이 카드에 적용할 퀴즈 유형")


class StudyCard(SQLModel):
    """학습 카드 스키마 (퀴즈 포맷팅 포함)."""

    id: int = Field(description="카드 고유 ID")
    english_word: str = Field(description="영어 단어")
    korean_meaning: str = Field(description="한국어 뜻")
    part_of_speech: str | None = Field(default=None, description="품사 (noun, verb 등)")
    pronunciation_ipa: str | None = Field(default=None, description="IPA 발음 기호")
    definition_en: str | None = Field(default=None, description="영어 정의")
    example_sentences: list | None = Field(
        default=None, description="예문 목록 [{sentence, translation}]"
    )
    audio_url: str | None = Field(default=None, description="오디오 URL")
    image_url: str | None = Field(default=None, description="연상 이미지 URL")
    is_new: bool = Field(description="신규 카드 여부. true=처음 학습, false=복습 카드")

    # 퀴즈 포맷팅 필드
    quiz_type: QuizType = Field(description="퀴즈 유형")
    question: str | ClozeQuestion = Field(description="문제 (문자열 또는 ClozeQuestion)")
    options: list[str] | None = Field(default=None, description="4지선다 선택지")


class CardResponse(SQLModel):
    """다음 카드 응답 스키마."""

    card: StudyCard | None = Field(description="학습 카드. None이면 모든 카드 완료")
    cards_remaining: int = Field(description="남은 카드 수")
    cards_completed: int = Field(description="완료한 카드 수")


# ============================================================
# Answer Request/Response
# ============================================================


class AnswerRequest(SQLModel):
    """정답 제출 요청 스키마."""

    session_id: UUID = Field(description="세션 ID")
    card_id: int = Field(description="카드 ID")
    answer: str = Field(description="사용자 입력 정답")
    response_time_ms: int | None = Field(default=None, ge=0, description="응답 시간 (밀리초)")

    # 힌트 관련 (Issue #52)
    hint_count: int = Field(default=0, ge=0, description="사용한 힌트 횟수 (0=미사용)")
    revealed_answer: bool = Field(default=False, description="정답보기로 정답 공개했는지 여부")

    # 퀴즈 유형 (Issue #53 - 오답 노트용)
    quiz_type: str | None = Field(
        default=None,
        description="퀴즈 유형 (word_to_meaning/meaning_to_word/cloze/listening)",
    )


class AnswerResponse(SQLModel):
    """정답 제출 응답 스키마."""

    card_id: int = Field(description="카드 ID")
    is_correct: bool = Field(description="정답 여부")
    correct_answer: str = Field(description="정답")
    user_answer: str = Field(description="사용자 입력 답")
    feedback: str | None = Field(default=None, description="피드백 메시지")

    # 점수 정보 (Issue #52)
    score: int = Field(default=100, description="획득 점수 (힌트 사용 시 감점, 0~100)")
    hint_penalty: int = Field(default=0, description="힌트 사용으로 인한 감점")

    # FSRS 업데이트 정보
    next_review_date: datetime | None = Field(description="다음 복습 예정일")
    card_state: CardState = Field(description="카드 상태 (NEW/LEARNING/REVIEW/RELEARNING)")


# ============================================================
# Session Complete
# ============================================================


class SessionCompleteRequest(SQLModel):
    """학습 세션 완료 요청 스키마."""

    session_id: UUID = Field(description="세션 ID")


class SessionSummary(SQLModel):
    """학습 세션 결과 요약 스키마."""

    total_cards: int = Field(description="학습한 총 카드 수")
    correct: int = Field(description="정답 수")
    wrong: int = Field(description="오답 수")
    accuracy: float = Field(description="정확도 (%) - (정답/총카드)*100")
    duration_seconds: int = Field(description="학습 시간 (초)")


class StreakInfo(SQLModel):
    """세션 완료 후 스트릭 정보 스키마."""

    current_streak: int = Field(description="현재 연속 학습일 수")
    longest_streak: int = Field(description="최장 연속 학습일 수 (역대 기록)")
    is_new_record: bool = Field(description="이번 세션으로 최장 기록을 갱신했는지 여부")
    streak_status: str = Field(
        description="스트릭 상태. 'continued'(유지), 'started'(새로 시작), 'broken'(끊김 후 재시작)"
    )
    message: str = Field(description="사용자에게 표시할 동기 부여 메시지")


class DailyGoalStatus(SQLModel):
    """세션 완료 후 일일 목표 상태 스키마."""

    goal: int = Field(description="설정된 일일 목표 카드 수")
    completed: int = Field(description="오늘 학습 완료한 총 카드 수 (이 세션 포함)")
    progress: float = Field(description="목표 달성률 (%) - (완료/목표)*100, 최대 100")
    is_completed: bool = Field(description="일일 목표 달성 여부")


class XPInfo(SQLModel):
    """경험치 정보 스키마."""

    base_xp: int = Field(description="기본 경험치 (정답당 10XP)")
    bonus_xp: int = Field(description="보너스 경험치 (80% 이상 시 +50XP)")
    total_xp: int = Field(description="총 획득 경험치")


class SessionCompleteResponse(SQLModel):
    """학습 세션 완료 응답 스키마."""

    session_summary: SessionSummary = Field(description="이번 세션 결과 요약")
    streak: StreakInfo = Field(description="스트릭 정보 (연속 학습일)")
    daily_goal: DailyGoalStatus = Field(description="일일 목표 달성 상태")
    xp: XPInfo = Field(description="획득 경험치 정보")


# ============================================================
# Study Overview
# ============================================================


class DueCardSummary(SQLModel):
    """복습 예정 카드 요약 스키마."""

    card_id: int = Field(description="카드 고유 ID")
    english_word: str = Field(description="영어 단어")
    korean_meaning: str = Field(description="한국어 뜻")
    next_review_date: datetime = Field(description="다음 복습 예정일")
    card_state: CardState = Field(description="카드 상태 (NEW/LEARNING/REVIEW/RELEARNING)")


class StudyOverviewResponse(SQLModel):
    """학습 현황 개요 응답 스키마."""

    new_cards_count: int = Field(description="학습 가능한 신규 카드 수")
    review_cards_count: int = Field(description="복습 예정 카드 수")
    total_available: int = Field(description="총 학습 가능 카드 수")
    due_cards: list[DueCardSummary] = Field(description="복습 예정 카드 목록")


# ============================================================
# Session Status & Abandon (Issue #54)
# ============================================================


class SessionDailyGoalInfo(SQLModel):
    """세션 상태 조회 시 일일 목표 정보."""

    goal: int = Field(description="일일 목표 카드 수")
    completed_today: int = Field(description="오늘 완료한 카드 수")
    remaining_for_goal: int = Field(description="목표까지 남은 카드 수")
    will_complete_goal: bool = Field(description="현재 세션 완료 시 목표 달성 여부")


class SessionStatusResponse(SQLModel):
    """세션 상태 조회 응답 스키마."""

    session_id: UUID = Field(description="세션 ID")
    status: str = Field(description="세션 상태 (active/completed/abandoned)")
    total_cards: int = Field(description="총 카드 수")
    completed_cards: int = Field(description="완료한 카드 수")
    remaining_cards: int = Field(description="남은 카드 수")
    correct_count: int = Field(description="정답 수")
    wrong_count: int = Field(description="오답 수")
    started_at: datetime = Field(description="세션 시작 시간")
    elapsed_seconds: int = Field(description="경과 시간 (초)")
    daily_goal: SessionDailyGoalInfo = Field(description="일일 목표 정보")


class SessionAbandonRequest(SQLModel):
    """세션 중단 요청 스키마."""

    save_progress: bool = Field(default=True, description="진행 상황 저장 여부 (항상 true 권장)")


class SessionAbandonSummary(SQLModel):
    """세션 중단 시 요약 정보."""

    total_cards: int = Field(description="총 카드 수")
    completed_cards: int = Field(description="완료한 카드 수")
    correct_count: int = Field(description="정답 수")
    wrong_count: int = Field(description="오답 수")
    duration_seconds: int = Field(description="학습 시간 (초)")


class SessionAbandonResponse(SQLModel):
    """세션 중단 응답 스키마."""

    session_id: UUID = Field(description="세션 ID")
    status: str = Field(description="세션 상태 (abandoned)")
    summary: SessionAbandonSummary = Field(description="세션 요약")
    progress_saved: bool = Field(description="진행 상황 저장 여부")
    message: str = Field(description="안내 메시지")


# ============================================================
# Pronunciation Evaluation (Issue #56)
# ============================================================


class PhonemeFeedback(SQLModel):
    """개별 음소 피드백 스키마."""

    phoneme: str = Field(description="음소 (예: 'ʃ')")
    score: int = Field(description="해당 음소 점수 (0~100)")
    tip: str = Field(description="개선 팁")


class PronunciationFeedback(SQLModel):
    """발음 피드백 스키마."""

    overall: str = Field(description="전체 피드백 메시지")
    stress: str | None = Field(default=None, description="강세 관련 피드백")
    sounds: list[PhonemeFeedback] | None = Field(default=None, description="개별 음소 피드백 목록")


class PronunciationEvaluateRequest(SQLModel):
    """발음 평가 요청 스키마."""

    card_id: int | None = Field(default=None, description="평가할 단어의 카드 ID")
    word: str | None = Field(default=None, description="평가할 단어 (card_id 없을 경우)")


class PronunciationEvaluateResponse(SQLModel):
    """발음 평가 응답 스키마."""

    card_id: int | None = Field(default=None, description="카드 ID")
    word: str = Field(description="평가한 단어")
    pronunciation_ipa: str | None = Field(default=None, description="IPA 발음 기호")

    score: int = Field(description="발음 점수 (0~100)")
    grade: str = Field(description="등급 (excellent/good/fair/needs_practice)")

    feedback: PronunciationFeedback = Field(description="피드백 정보")

    native_audio_url: str | None = Field(default=None, description="네이티브 발음 오디오 URL")
    user_audio_url: str | None = Field(default=None, description="사용자 녹음 URL (저장된 경우)")
