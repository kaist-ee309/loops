"""Word tutor chat service (DB + LangGraph)."""

from __future__ import annotations

from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.core.exceptions import ExternalServiceError, NotFoundError, ValidationError
from app.models import StudySession, WordTutorMessage, WordTutorThread
from app.models.schemas.word_tutor import (
    TutorHistoryResponse,
    TutorMessageRead,
    TutorMessageRequest,
    TutorMessageResponse,
    TutorStartResponse,
)
from app.services.word_tutor_graph import MESSAGE_GRAPH, START_GRAPH


class WordTutorService:
    """Word tutor chat operations."""

    @staticmethod
    async def _require_openai() -> None:
        if not settings.openai_api_key:
            raise ExternalServiceError("OpenAI API key is not configured", service="openai")

    @staticmethod
    async def _validate_session_and_card(
        session: AsyncSession,
        *,
        user_id: UUID,
        session_id: UUID,
        card_id: int,
    ) -> None:
        study_session = await session.get(StudySession, session_id)
        if not study_session:
            raise NotFoundError(f"Session {session_id} not found")

        if study_session.user_id != user_id:
            raise ValidationError("Session does not belong to this user")

        if card_id not in (study_session.card_ids or []):
            raise ValidationError("Card is not in this session")

    @staticmethod
    async def _get_or_create_thread(
        session: AsyncSession,
        *,
        user_id: UUID,
        session_id: UUID,
        card_id: int,
    ) -> WordTutorThread:
        result = await session.exec(
            select(WordTutorThread).where(
                WordTutorThread.user_id == user_id,
                WordTutorThread.session_id == session_id,
                WordTutorThread.card_id == card_id,
            )
        )
        thread = result.first()
        if thread:
            return thread

        thread = WordTutorThread(user_id=user_id, session_id=session_id, card_id=card_id)
        session.add(thread)
        await session.commit()
        await session.refresh(thread)
        return thread

    @staticmethod
    def _to_read(m: WordTutorMessage) -> TutorMessageRead:
        return TutorMessageRead(
            id=m.id,
            role=m.role,
            content=m.content,
            suggested_questions=m.suggested_questions,
            created_at=m.created_at,
        )

    @staticmethod
    async def _get_messages(
        session: AsyncSession,
        *,
        thread_id: UUID,
        limit: int = 50,
    ) -> list[TutorMessageRead]:
        result = await session.exec(
            select(WordTutorMessage)
            .where(WordTutorMessage.thread_id == thread_id)
            .order_by(WordTutorMessage.created_at.asc())
            .limit(limit)
        )
        return [WordTutorService._to_read(m) for m in list(result.all())]

    @staticmethod
    async def start(
        session: AsyncSession,
        *,
        user_id: UUID,
        session_id: UUID,
        card_id: int,
        include_messages: bool = False,
    ) -> TutorStartResponse:
        await WordTutorService._require_openai()
        await WordTutorService._validate_session_and_card(
            session, user_id=user_id, session_id=session_id, card_id=card_id
        )
        thread = await WordTutorService._get_or_create_thread(
            session, user_id=user_id, session_id=session_id, card_id=card_id
        )

        out = await START_GRAPH.ainvoke(
            {"db": session, "thread_id": thread.id, "messages": []},
        )

        starter_questions = out.get("starter_questions") or []
        messages = None
        if include_messages:
            messages = await WordTutorService._get_messages(session, thread_id=thread.id)

        return TutorStartResponse(
            thread_id=thread.id,
            starter_questions=starter_questions,
            messages=messages,
        )

    @staticmethod
    async def send_message(
        session: AsyncSession,
        *,
        user_id: UUID,
        session_id: UUID,
        card_id: int,
        request: TutorMessageRequest,
    ) -> TutorMessageResponse:
        await WordTutorService._require_openai()
        await WordTutorService._validate_session_and_card(
            session, user_id=user_id, session_id=session_id, card_id=card_id
        )
        thread = await WordTutorService._get_or_create_thread(
            session, user_id=user_id, session_id=session_id, card_id=card_id
        )

        out = await MESSAGE_GRAPH.ainvoke(
            {
                "db": session,
                "thread_id": thread.id,
                "messages": [],
                "input_message": request.message,
            }
        )

        return TutorMessageResponse(
            thread_id=thread.id,
            assistant_message=out.get("assistant_answer") or "",
            follow_up_questions=out.get("follow_up_questions") or [],
        )

    @staticmethod
    async def history(
        session: AsyncSession,
        *,
        user_id: UUID,
        session_id: UUID,
        card_id: int,
        limit: int = 50,
    ) -> TutorHistoryResponse:
        await WordTutorService._validate_session_and_card(
            session, user_id=user_id, session_id=session_id, card_id=card_id
        )
        thread = await WordTutorService._get_or_create_thread(
            session, user_id=user_id, session_id=session_id, card_id=card_id
        )
        messages = await WordTutorService._get_messages(session, thread_id=thread.id, limit=limit)
        return TutorHistoryResponse(thread_id=thread.id, messages=messages)
