from datetime import datetime

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.models.tables.deck import DeckBase


class DeckCreate(DeckBase):
    """덱 생성 스키마."""

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        """덱 이름이 비어있지 않은지 검증합니다."""
        if not v or not v.strip():
            raise ValueError("Deck name cannot be empty or whitespace")
        return v.strip()

    @field_validator("difficulty_level")
    @classmethod
    def difficulty_level_valid(cls, v: str | None) -> str | None:
        """난이도가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_levels = {"beginner", "intermediate", "advanced"}
        v = v.lower().strip()
        if v not in allowed_levels:
            raise ValueError(f"Difficulty level must be one of: {', '.join(allowed_levels)}")
        return v


class DeckRead(DeckBase):
    """덱 조회 응답 스키마."""

    id: int = Field(description="덱 고유 ID")
    creator_id: int | None = Field(default=None, description="덱 생성자 ID (없으면 시스템 생성)")
    created_at: datetime = Field(description="덱 생성 시간 (UTC)")
    updated_at: datetime | None = Field(default=None, description="덱 최종 수정 시간 (UTC)")


class DeckUpdate(SQLModel):
    """덱 수정 스키마. 부분 업데이트 지원."""

    name: str | None = Field(default=None, max_length=255, description="덱 이름")
    description: str | None = Field(default=None, description="덱 설명")
    category: str | None = Field(default=None, max_length=100, description="카테고리")
    difficulty_level: str | None = Field(
        default=None,
        max_length=50,
        description="난이도 (beginner, intermediate, advanced)",
    )
    is_public: bool | None = Field(default=None, description="공개 여부")
    is_official: bool | None = Field(default=None, description="공식 덱 여부")

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str | None) -> str | None:
        """덱 이름이 비어있지 않은지 검증합니다."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Deck name cannot be empty or whitespace")
        return v.strip()

    @field_validator("difficulty_level")
    @classmethod
    def difficulty_level_valid(cls, v: str | None) -> str | None:
        """난이도가 허용된 값인지 검증합니다."""
        if v is None:
            return v
        allowed_levels = {"beginner", "intermediate", "advanced"}
        v = v.lower().strip()
        if v not in allowed_levels:
            raise ValueError(f"Difficulty level must be one of: {', '.join(allowed_levels)}")
        return v


class DeckWithProgressRead(SQLModel):
    """덱 목록 조회 응답 스키마 (학습 진행 정보 포함)."""

    id: int = Field(description="덱 고유 ID")
    name: str = Field(description="덱 이름")
    description: str | None = Field(default=None, description="덱 설명")
    total_cards: int = Field(description="덱 내 총 카드 수")
    learned_cards: int = Field(description="학습 완료 카드 수 (REVIEW 상태)")
    learning_cards: int = Field(description="학습 중인 카드 수 (LEARNING/RELEARNING 상태)")
    new_cards: int = Field(description="미학습 카드 수 (NEW 상태)")
    progress_percent: float = Field(description="학습 진행률 (%) - (학습 완료 / 총 카드) * 100")


class DecksListResponse(SQLModel):
    """덱 목록 응답 스키마 (페이지네이션 포함)."""

    decks: list[DeckWithProgressRead] = Field(description="덱 목록")
    total: int = Field(description="전체 덱 수 (필터링 적용 후)")
    skip: int = Field(description="건너뛴 레코드 수")
    limit: int = Field(description="반환된 최대 레코드 수")


class DeckDetailRead(SQLModel):
    """덱 상세 조회 응답 스키마 (전체 정보 + 학습 진행 포함)."""

    # From DeckRead
    id: int = Field(description="덱 고유 ID")
    name: str = Field(description="덱 이름")
    description: str | None = Field(default=None, description="덱 설명")
    category: str | None = Field(default=None, description="카테고리")
    difficulty_level: str | None = Field(
        default=None, description="난이도 (beginner, intermediate, advanced)"
    )
    is_public: bool = Field(description="공개 여부")
    is_official: bool = Field(description="공식 덱 여부 (운영자가 만든 덱)")
    creator_id: int | None = Field(default=None, description="덱 생성자 ID")
    created_at: datetime = Field(description="덱 생성 시간 (UTC)")
    updated_at: datetime | None = Field(default=None, description="덱 최종 수정 시간 (UTC)")
    # From progress calculation
    total_cards: int = Field(description="덱 내 총 카드 수")
    learned_cards: int = Field(description="학습 완료 카드 수 (REVIEW 상태)")
    learning_cards: int = Field(description="학습 중인 카드 수 (LEARNING/RELEARNING 상태)")
    new_cards: int = Field(description="미학습 카드 수 (NEW 상태)")
    progress_percent: float = Field(description="학습 진행률 (%)")


# ============================================================
# Category Schemas
# ============================================================


class CategoryInfo(SQLModel):
    """카테고리 기본 정보 스키마."""

    id: str = Field(description="카테고리 ID (예: exam, textbook)")
    name: str = Field(description="카테고리 이름 (예: 시험, 교과서)")
    description: str = Field(description="카테고리 설명")
    icon: str = Field(description="카테고리 아이콘 (이모지)")


class CategoryWithStats(CategoryInfo):
    """카테고리 정보 + 통계 스키마."""

    total_decks: int = Field(description="해당 카테고리의 전체 덱 수")
    selected_decks: int = Field(description="해당 카테고리에서 선택된 덱 수")
    selection_state: str = Field(
        description="선택 상태: all(전체 선택), partial(일부 선택), none(미선택)"
    )


class CategoriesResponse(SQLModel):
    """카테고리 목록 응답 스키마."""

    categories: list[CategoryWithStats] = Field(description="카테고리 목록")


class CategoryDetail(SQLModel):
    """카테고리 상세 정보 스키마 (통계 제외)."""

    id: str = Field(description="카테고리 ID")
    name: str = Field(description="카테고리 이름")
    description: str = Field(description="카테고리 설명")


class DeckInCategory(SQLModel):
    """카테고리 내 덱 정보 스키마."""

    id: int = Field(description="덱 고유 ID")
    name: str = Field(description="덱 이름")
    description: str | None = Field(default=None, description="덱 설명")
    total_cards: int = Field(description="덱 내 총 카드 수")
    is_selected: bool = Field(description="해당 덱이 사용자에게 선택되었는지 여부")


class CategoryDecksResponse(SQLModel):
    """카테고리별 덱 목록 응답 스키마."""

    category: CategoryDetail = Field(description="카테고리 정보")
    decks: list[DeckInCategory] = Field(description="해당 카테고리의 덱 목록")
    total_decks: int = Field(description="해당 카테고리의 전체 덱 수")
    selected_decks: int = Field(description="해당 카테고리에서 선택된 덱 수")
