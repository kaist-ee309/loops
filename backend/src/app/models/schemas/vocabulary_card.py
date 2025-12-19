from typing import Any

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.models.tables.vocabulary_card import VocabularyCardBase


class VocabularyCardCreate(VocabularyCardBase):
    """단어 카드 생성 스키마."""

    example_sentences: list[dict[str, str]] | None = Field(
        default=None,
        description='예문 목록. 각 항목은 {sentence, translation} 형태. 예: [{"sentence": "I need to study.", "translation": "나는 공부해야 해요."}]',
    )
    tags: list[str] | None = Field(
        default=None,
        description='태그 목록 (분류용). 예: ["동사", "일상회화"]',
    )

    @field_validator("english_word", "korean_meaning")
    @classmethod
    def not_empty(cls, v: str) -> str:
        """필수 문자열 필드가 비어있지 않은지 검증합니다."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("cefr_level")
    @classmethod
    def cefr_level_valid(cls, v: str | None) -> str | None:
        """CEFR 레벨이 유효한지 검증합니다."""
        if v is None:
            return v
        allowed_levels = {"A1", "A2", "B1", "B2", "C1", "C2"}
        v = v.upper().strip()
        if v not in allowed_levels:
            raise ValueError(f"CEFR level must be one of: {', '.join(allowed_levels)}")
        return v

    @field_validator("difficulty_level")
    @classmethod
    def difficulty_level_valid(cls, v: str | None) -> str | None:
        """난이도가 유효한지 검증합니다."""
        if v is None:
            return v
        allowed_levels = {"beginner", "intermediate", "advanced"}
        v = v.lower().strip()
        if v not in allowed_levels:
            raise ValueError(f"Difficulty level must be one of: {', '.join(allowed_levels)}")
        return v

    @field_validator("word_type")
    @classmethod
    def word_type_valid(cls, v: str | None) -> str | None:
        """word_type이 유효한지 검증합니다."""
        if v is None:
            return "word"
        allowed_types = {"word", "phrase", "idiom", "collocation"}
        v = v.lower().strip()
        if v not in allowed_types:
            raise ValueError(f"Word type must be one of: {', '.join(allowed_types)}")
        return v

    @field_validator("tags")
    @classmethod
    def tags_not_empty(cls, v: list[str] | None) -> list[str] | None:
        """태그가 빈 문자열이 아닌지 검증합니다."""
        if v is None:
            return v
        cleaned = [tag.strip() for tag in v if tag and tag.strip()]
        return cleaned if cleaned else None


class VocabularyCardRead(VocabularyCardBase):
    """단어 카드 조회 응답 스키마."""

    id: int = Field(description="카드 고유 ID")
    category: str | None = Field(default=None, description="카테고리 (예: 동사, 명사)")
    frequency_rank: int | None = Field(
        default=None, description="사용 빈도 순위 (낮을수록 자주 사용)"
    )
    audio_url: str | None = Field(default=None, description="발음 오디오 파일 URL")
    image_url: str | None = Field(default=None, description="연상 이미지 URL")
    image_status: str | None = Field(
        default=None, description="이미지 생성 상태 (pending/ready/failed)"
    )
    image_model: str | None = Field(default=None, description="이미지 생성 모델 ID")
    image_generated_at: Any | None = Field(default=None, description="이미지 생성 시간 (UTC)")
    image_error: str | None = Field(default=None, description="이미지 생성 실패 메시지")
    example_sentences: list[dict[str, str]] | None = Field(
        default=None, description="예문 목록 [{sentence, translation}]"
    )
    tags: list[str] | None = Field(default=None, description="태그 목록")
    created_at: Any = Field(description="카드 생성 시간 (UTC)")
    updated_at: Any | None = Field(default=None, description="카드 최종 수정 시간 (UTC)")


class VocabularyCardUpdate(SQLModel):
    """단어 카드 수정 스키마. 부분 업데이트 지원."""

    english_word: str | None = Field(default=None, max_length=255, description="영어 단어")
    korean_meaning: str | None = Field(default=None, max_length=255, description="한국어 뜻")
    part_of_speech: str | None = Field(
        default=None, max_length=50, description="품사 (noun, verb 등)"
    )
    word_type: str | None = Field(
        default=None,
        max_length=50,
        description="항목 유형 (word, phrase, idiom, collocation)",
    )
    pronunciation_ipa: str | None = Field(default=None, max_length=255, description="IPA 발음 기호")
    definition_en: str | None = Field(default=None, description="영어 정의")
    example_sentences: list[dict[str, str]] | None = Field(
        default=None, description="예문 목록 [{sentence, translation}]"
    )
    difficulty_level: str | None = Field(
        default=None,
        max_length=50,
        description="난이도 (beginner, intermediate, advanced)",
    )
    cefr_level: str | None = Field(default=None, max_length=10, description="CEFR 레벨 (A1~C2)")
    category: str | None = Field(default=None, max_length=50, description="카테고리")
    frequency_rank: int | None = Field(default=None, ge=0, description="사용 빈도 순위")
    audio_url: str | None = Field(default=None, max_length=500, description="발음 오디오 URL")
    image_url: str | None = Field(default=None, max_length=500, description="연상 이미지 URL")
    image_status: str | None = Field(default=None, max_length=20, description="이미지 생성 상태")
    image_model: str | None = Field(default=None, max_length=100, description="이미지 생성 모델 ID")
    image_prompt: str | None = Field(default=None, description="이미지 생성 프롬프트")
    image_storage_path: str | None = Field(
        default=None, max_length=500, description="스토리지 경로"
    )
    image_error: str | None = Field(default=None, description="이미지 생성 실패 메시지")
    tags: list[str] | None = Field(default=None, description="태그 목록")
    deck_id: int | None = Field(default=None, gt=0, description="소속 덱 ID")
    is_verified: bool | None = Field(default=None, description="검증 완료 여부")

    @field_validator("english_word", "korean_meaning")
    @classmethod
    def not_empty(cls, v: str | None) -> str | None:
        """문자열 필드가 비어있지 않은지 검증합니다."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Field cannot be empty or whitespace")
        return v.strip()

    @field_validator("cefr_level")
    @classmethod
    def cefr_level_valid(cls, v: str | None) -> str | None:
        """CEFR 레벨이 유효한지 검증합니다."""
        if v is None:
            return v
        allowed_levels = {"A1", "A2", "B1", "B2", "C1", "C2"}
        v = v.upper().strip()
        if v not in allowed_levels:
            raise ValueError(f"CEFR level must be one of: {', '.join(allowed_levels)}")
        return v

    @field_validator("difficulty_level")
    @classmethod
    def difficulty_level_valid(cls, v: str | None) -> str | None:
        """난이도가 유효한지 검증합니다."""
        if v is None:
            return v
        allowed_levels = {"beginner", "intermediate", "advanced"}
        v = v.lower().strip()
        if v not in allowed_levels:
            raise ValueError(f"Difficulty level must be one of: {', '.join(allowed_levels)}")
        return v

    @field_validator("word_type")
    @classmethod
    def word_type_valid(cls, v: str | None) -> str | None:
        """word_type이 유효한지 검증합니다."""
        if v is None:
            return v
        allowed_types = {"word", "phrase", "idiom", "collocation"}
        v = v.lower().strip()
        if v not in allowed_types:
            raise ValueError(f"Word type must be one of: {', '.join(allowed_types)}")
        return v

    @field_validator("tags")
    @classmethod
    def tags_not_empty(cls, v: list[str] | None) -> list[str] | None:
        """태그가 빈 문자열이 아닌지 검증합니다."""
        if v is None:
            return v
        cleaned = [tag.strip() for tag in v if tag and tag.strip()]
        return cleaned if cleaned else None


# ============================================================
# Related Words Schemas (Issue #51)
# ============================================================


class RelatedWordInfo(SQLModel):
    """연관 단어 정보 스키마."""

    card_id: int | None = Field(default=None, description="연관 단어 카드 ID (DB에 존재하는 경우)")
    english_word: str = Field(description="영어 단어")
    korean_meaning: str = Field(description="한국어 뜻")
    relation_type: str = Field(
        description="연관 유형: etymology(어원) | synonym(유의어) | antonym(반의어) | topic(주제) | collocation(연어)"
    )
    relation_label: str = Field(description="연관 유형 한글 라벨")
    reason: str = Field(description="연관 이유 설명")


class CardSummary(SQLModel):
    """카드 요약 정보 스키마."""

    id: int = Field(description="카드 고유 ID")
    english_word: str = Field(description="영어 단어")
    korean_meaning: str = Field(description="한국어 뜻")


class RelatedWordsResponse(SQLModel):
    """연관 단어 조회 응답 스키마."""

    card: CardSummary = Field(description="기준 카드 정보")
    related_words: list[RelatedWordInfo] = Field(description="연관 단어 목록")
    total_related: int = Field(description="연관 단어 총 개수")
