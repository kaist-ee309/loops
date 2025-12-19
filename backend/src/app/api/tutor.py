"""Word tutor chat endpoints (study-session scoped)."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models import (
    TutorHistoryResponse,
    TutorMessageRequest,
    TutorMessageResponse,
    TutorStartResponse,
)
from app.services.word_tutor_service import WordTutorService

TAG = "tutor"
TAG_METADATA = {
    "name": TAG,
    "description": """단어 튜터 챗봇 API.\n\n학습 세션 내 특정 카드(단어) 학습 직후, AI 튜터에게 질문하고 답변과 후속 질문 추천을 받습니다.""",
}

router = APIRouter(prefix="/study", tags=[TAG])


@router.post(
    "/session/{session_id}/cards/{card_id}/tutor/start",
    response_model=TutorStartResponse,
    summary="단어 튜터 챗 시작",
)
async def start_word_tutor(
    session_id: UUID = Path(description="학습 세션 ID"),
    card_id: int = Path(description="카드 ID"),
    include_messages: bool = Query(default=False, description="기존 대화 포함 여부"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> TutorStartResponse:
    return await WordTutorService.start(
        session=session,
        user_id=current_profile.id,
        session_id=session_id,
        card_id=card_id,
        include_messages=include_messages,
    )


@router.post(
    "/session/{session_id}/cards/{card_id}/tutor/message",
    response_model=TutorMessageResponse,
    summary="단어 튜터 챗 메시지 전송",
)
async def send_word_tutor_message(
    request: TutorMessageRequest,
    session_id: UUID = Path(description="학습 세션 ID"),
    card_id: int = Path(description="카드 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> TutorMessageResponse:
    return await WordTutorService.send_message(
        session=session,
        user_id=current_profile.id,
        session_id=session_id,
        card_id=card_id,
        request=request,
    )


@router.get(
    "/session/{session_id}/cards/{card_id}/tutor/history",
    response_model=TutorHistoryResponse,
    summary="단어 튜터 챗 히스토리 조회",
)
async def get_word_tutor_history(
    session_id: UUID = Path(description="학습 세션 ID"),
    card_id: int = Path(description="카드 ID"),
    limit: int = Query(default=50, ge=1, le=200, description="최대 메시지 수"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> TutorHistoryResponse:
    return await WordTutorService.history(
        session=session,
        user_id=current_profile.id,
        session_id=session_id,
        card_id=card_id,
        limit=limit,
    )
