"""Wrong answer related schemas."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class WrongAnswerCardInfo(SQLModel):
    """Wrong answer card info schema."""

    id: int = Field(description="카드 ID")
    english_word: str = Field(description="영어 단어")
    korean_meaning: str = Field(description="한국어 뜻")


class WrongAnswerRead(SQLModel):
    """Wrong answer read schema."""

    id: int = Field(description="오답 기록 ID")
    card: WrongAnswerCardInfo = Field(description="카드 정보")
    user_answer: str = Field(description="사용자가 입력한 답")
    correct_answer: str = Field(description="정답")
    quiz_type: str = Field(description="퀴즈 유형")
    created_at: datetime = Field(description="오답 발생 시간")
    reviewed: bool = Field(description="복습 완료 여부")
    reviewed_at: datetime | None = Field(default=None, description="복습 완료 시간")


class WrongAnswersResponse(SQLModel):
    """Wrong answers list response schema."""

    wrong_answers: list[WrongAnswerRead] = Field(description="오답 목록")
    total: int = Field(description="전체 오답 수")
    unreviewed_count: int = Field(description="미복습 오답 수")


class WrongAnswerReviewedResponse(SQLModel):
    """Wrong answer reviewed response schema."""

    id: int = Field(description="오답 기록 ID")
    reviewed: bool = Field(description="복습 완료 여부")
    reviewed_at: datetime | None = Field(description="복습 완료 시간")


class WrongReviewSessionRequest(SQLModel):
    """Wrong review session start request schema."""

    limit: int = Field(default=10, ge=1, le=50, description="재학습할 카드 수 (1~50)")


class WrongReviewSessionResponse(SQLModel):
    """Wrong review session start response schema."""

    session_id: UUID = Field(description="세션 ID")
    total_cards: int = Field(description="총 카드 수")
    cards_from_wrong_answers: bool = Field(default=True, description="오답 카드 기반 세션 여부")
    started_at: datetime = Field(description="세션 시작 시간")
