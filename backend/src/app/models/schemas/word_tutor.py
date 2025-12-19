"""Word tutor chat schemas."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.enums import ChatRole


class TutorMessageRequest(SQLModel):
    """User message request."""

    message: str = Field(min_length=1, max_length=4000, description="사용자 질문")


class TutorMessageRead(SQLModel):
    """Persisted message for history."""

    id: UUID = Field(description="메시지 ID")
    role: ChatRole = Field(description="메시지 역할 (system/user/assistant)")
    content: str = Field(description="메시지 내용")
    suggested_questions: list[str] | None = Field(default=None, description="추천 후속 질문")
    created_at: datetime = Field(description="생성 시각 (UTC)")


class TutorStartResponse(SQLModel):
    """Start tutor chat for a card."""

    thread_id: UUID = Field(description="튜터 스레드 ID")
    starter_questions: list[str] = Field(description="시작 추천 질문 리스트")
    messages: list[TutorMessageRead] | None = Field(default=None, description="기존 대화(옵션)")


class TutorMessageResponse(SQLModel):
    """Assistant reply + follow-up suggestions."""

    thread_id: UUID = Field(description="튜터 스레드 ID")
    assistant_message: str = Field(description="AI 답변")
    follow_up_questions: list[str] = Field(description="후속 추천 질문")


class TutorHistoryResponse(SQLModel):
    """Conversation history."""

    thread_id: UUID = Field(description="튜터 스레드 ID")
    messages: list[TutorMessageRead] = Field(description="대화 히스토리")
