"""
단어 카드 관련 API 엔드포인트.

영어 단어 카드의 생성, 조회, 수정, 삭제를 처리합니다.
"""

import io
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import StreamingResponse
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.dependencies import CurrentActiveProfile
from app.database import get_session
from app.models import (
    RelatedWordsResponse,
    VocabularyCardCreate,
    VocabularyCardRead,
    VocabularyCardUpdate,
)
from app.services.tts_service import TTSService
from app.services.vocabulary_card_service import VocabularyCardService

TAG = "cards"
TAG_METADATA = {
    "name": TAG,
    "description": "단어 카드 관련 API. 영어 단어 카드의 생성, 조회, 수정, 삭제를 처리합니다.",
}

router = APIRouter(prefix="/cards", tags=[TAG])


@router.post(
    "",
    response_model=VocabularyCardRead,
    status_code=status.HTTP_201_CREATED,
    summary="단어 카드 생성",
    description="새로운 영어 단어 카드를 생성합니다.",
    responses={
        201: {"description": "단어 카드 생성 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        422: {"description": "유효성 검사 실패 - 필수 필드 누락 또는 형식 오류"},
    },
)
async def create_vocabulary_card(
    card_data: VocabularyCardCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_profile: CurrentActiveProfile,
):
    """
    새로운 단어 카드를 생성합니다.

    **인증 필요:** Bearer 토큰

    **필수 필드:**
    - `english_word`: 영어 단어
    - `korean_meaning`: 한국어 뜻

    **선택 필드:**
    - `part_of_speech`: 품사
    - `pronunciation_ipa`: IPA 발음 기호
    - `definition_en`: 영어 정의
    - `example_sentences`: 예문 목록
    - `difficulty_level`: 난이도 (1~10)
    - `cefr_level`: CEFR 레벨 (A1~C2)
    - `deck_id`: 소속 덱 ID
    """
    card = await VocabularyCardService.create_card(session, card_data)
    return card


@router.get(
    "",
    response_model=list[VocabularyCardRead],
    summary="단어 카드 목록 조회",
    description="단어 카드 목록을 조회합니다. 난이도와 덱으로 필터링할 수 있습니다.",
    responses={
        200: {"description": "단어 카드 목록 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
    },
)
async def get_vocabulary_cards(
    skip: int = Query(default=0, ge=0, description="건너뛸 레코드 수 (페이지네이션용)"),
    limit: int = Query(default=100, ge=1, le=100, description="반환할 최대 레코드 수 (1~100)"),
    difficulty_level: str | None = Query(default=None, description="난이도 필터 (예: 'A1', 'B2')"),
    deck_id: int | None = Query(default=None, description="특정 덱의 카드만 조회"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
):
    """
    단어 카드 목록을 조회합니다.

    **인증 필요:** Bearer 토큰

    **쿼리 파라미터:**
    - `skip`: 건너뛸 레코드 수 (기본값: 0)
    - `limit`: 반환할 최대 레코드 수 (기본값: 100, 최대: 100)
    - `difficulty_level`: CEFR 레벨로 필터링 (선택)
    - `deck_id`: 특정 덱의 카드만 조회 (선택)

    **페이지네이션 예시:**
    - 1페이지: `skip=0&limit=20`
    - 2페이지: `skip=20&limit=20`
    """
    cards = await VocabularyCardService.get_cards(
        session,
        skip=skip,
        limit=limit,
        difficulty_level=difficulty_level,
        deck_id=deck_id,
    )
    return cards


@router.get(
    "/{card_id}",
    response_model=VocabularyCardRead,
    summary="단어 카드 상세 조회",
    description="특정 단어 카드의 상세 정보를 조회합니다.",
    responses={
        200: {"description": "단어 카드 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "단어 카드를 찾을 수 없음"},
    },
)
async def get_vocabulary_card(
    card_id: int = Path(description="조회할 카드의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
):
    """
    특정 단어 카드를 조회합니다.

    **인증 필요:** Bearer 토큰

    **파라미터:**
    - `card_id`: 조회할 카드의 ID

    **반환 정보:**
    - 영어 단어, 한국어 뜻, 발음
    - 품사, 정의, 예문
    - 난이도, CEFR 레벨
    - 생성/수정 시간
    """
    card = await VocabularyCardService.get_card(session, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found",
        )
    return card


@router.get(
    "/{card_id}/audio",
    summary="단어 카드 발음 오디오 생성",
    description="TTS를 사용하여 단어 카드의 발음 오디오를 실시간으로 생성하여 제공합니다.",
    responses={
        200: {"description": "오디오 스트림 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "단어 카드를 찾을 수 없음"},
        429: {"description": "레이트 리밋 초과"},
        503: {"description": "TTS 외부 서비스 오류"},
    },
)
async def get_vocabulary_card_audio(
    card_id: int = Path(description="조회할 카드의 고유 ID"),
    audio_format: Literal["mp3", "ogg"] = Query(
        default="mp3",
        alias="format",
        description="오디오 포맷 (mp3 또는 ogg)",
    ),
    voice: str | None = Query(default=None, description="TTS 보이스 (기본: 서버 설정)"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
):
    card = await VocabularyCardService.get_card(session, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found",
        )

    audio_bytes = await TTSService.generate_audio(
        profile_id=current_profile.id,
        text=card.english_word,
        audio_format=audio_format,
        voice=voice,
    )

    media_type = "audio/mpeg" if audio_format == "mp3" else "audio/ogg"
    response = StreamingResponse(io.BytesIO(audio_bytes), media_type=media_type)
    response.headers["Cache-Control"] = "public, max-age=86400"
    response.headers["Content-Disposition"] = f'inline; filename="card-{card_id}.{audio_format}"'
    return response


@router.patch(
    "/{card_id}",
    response_model=VocabularyCardRead,
    summary="단어 카드 수정",
    description="단어 카드 정보를 수정합니다. 부분 업데이트를 지원합니다.",
    responses={
        200: {"description": "단어 카드 수정 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "단어 카드를 찾을 수 없음"},
        422: {"description": "유효성 검사 실패 - 잘못된 데이터 형식"},
    },
)
async def update_vocabulary_card(
    card_data: VocabularyCardUpdate,
    card_id: int = Path(description="수정할 카드의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
):
    """
    단어 카드를 수정합니다.

    **인증 필요:** Bearer 토큰

    **부분 업데이트:** 변경하고 싶은 필드만 전송하면 됩니다.

    **수정 가능한 필드:**
    - `english_word`: 영어 단어
    - `korean_meaning`: 한국어 뜻
    - `part_of_speech`: 품사
    - `pronunciation_ipa`: IPA 발음 기호
    - `definition_en`: 영어 정의
    - `example_sentences`: 예문 목록
    - `difficulty_level`: 난이도 (1~10)
    - `cefr_level`: CEFR 레벨 (A1~C2)
    """
    card = await VocabularyCardService.update_card(session, card_id, card_data)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found",
        )
    return card


@router.delete(
    "/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="단어 카드 삭제",
    description="단어 카드를 삭제합니다.",
    responses={
        204: {"description": "단어 카드 삭제 성공 (응답 본문 없음)"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "단어 카드를 찾을 수 없음"},
    },
)
async def delete_vocabulary_card(
    card_id: int = Path(description="삭제할 카드의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
):
    """
    단어 카드를 삭제합니다.

    **인증 필요:** Bearer 토큰

    **주의사항:**
    - 이 작업은 되돌릴 수 없습니다
    - 관련된 학습 진행 기록도 함께 영향받을 수 있습니다
    """
    success = await VocabularyCardService.delete_card(session, card_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found",
        )
    return None


@router.get(
    "/{card_id}/related",
    response_model=RelatedWordsResponse,
    summary="연관 단어 조회",
    description="특정 단어 카드의 연관 단어(연상 네트워크) 정보를 조회합니다.",
    responses={
        200: {"description": "연관 단어 정보 반환 성공"},
        401: {"description": "인증 실패 - 유효한 토큰이 필요함"},
        404: {"description": "단어 카드를 찾을 수 없음"},
    },
)
async def get_related_words(
    card_id: int = Path(description="조회할 카드의 고유 ID"),
    session: Annotated[AsyncSession, Depends(get_session)] = None,
    current_profile: CurrentActiveProfile = None,
) -> RelatedWordsResponse:
    """
    특정 단어 카드의 연관 단어를 조회합니다.

    **인증 필요:** Bearer 토큰

    **반환 정보:**
    - `card`: 기준 카드 정보 (id, english_word, korean_meaning)
    - `related_words`: 연관 단어 목록
      - `card_id`: 연관 단어 카드 ID (DB에 존재하는 경우)
      - `english_word`: 영어 단어
      - `korean_meaning`: 한국어 뜻
      - `relation_type`: 연관 유형 (etymology/synonym/antonym/topic/collocation)
      - `relation_label`: 연관 유형 한글 라벨
      - `reason`: 연관 이유 설명
    - `total_related`: 연관 단어 총 개수

    **relation_type 종류:**
    - `etymology`: 어원 (같은 어근/접두사/접미사)
    - `synonym`: 유의어 (비슷한 의미)
    - `antonym`: 반의어 (반대 의미)
    - `topic`: 주제 연관 (같은 분야/상황)
    - `collocation`: 연어 (자주 함께 쓰이는 단어)
    """
    card = await VocabularyCardService.get_card(session, card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocabulary card not found",
        )

    return VocabularyCardService.get_related_words(card)
