"""사용자 선택 덱 관련 스키마."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class UserSelectedDeckCreate(SQLModel):
    """사용자 선택 덱 생성 스키마."""

    user_id: UUID = Field(description="사용자 ID (UUID)")
    deck_id: int = Field(description="덱 ID")


class UserSelectedDeckRead(SQLModel):
    """사용자 선택 덱 조회 응답 스키마."""

    id: int = Field(description="선택 기록 고유 ID")
    user_id: UUID = Field(description="사용자 ID (UUID)")
    deck_id: int = Field(description="덱 ID")
    created_at: datetime = Field(description="선택 시간 (UTC)")
    updated_at: datetime | None = Field(default=None, description="최종 수정 시간 (UTC)")


class SelectDecksRequest(SQLModel):
    """학습 덱 선택 요청 스키마."""

    select_all: bool = Field(
        description="전체 덱 선택 여부. true면 모든 공개 덱에서 학습, false면 deck_ids에 지정된 덱만"
    )
    deck_ids: list[int] | None = Field(
        default=None,
        description="선택할 덱 ID 목록. select_all=false일 때 필수. 예: [1, 2, 3]",
    )


class SelectDecksResponse(SQLModel):
    """학습 덱 선택 응답 스키마."""

    select_all: bool = Field(description="전체 덱 선택 여부")
    selected_deck_ids: list[int] = Field(
        description="선택된 덱 ID 목록 (select_all=true면 빈 배열)"
    )


class SelectedDeckInfo(SQLModel):
    """선택된 덱 정보 스키마."""

    id: int = Field(description="덱 고유 ID")
    name: str = Field(description="덱 이름")
    total_cards: int = Field(description="덱 내 총 카드 수")
    progress_percent: float = Field(description="학습 진행률 (%)")


class DisplayItem(SQLModel):
    """코스명 표시용 항목."""

    type: str = Field(description="항목 타입: category(카테고리) | deck(덱)")
    name: str = Field(description="표시 이름")
    count: int = Field(description="해당 항목의 덱/카드 수")


class CategorySelectionState(SQLModel):
    """카테고리별 선택 상태."""

    category_id: str = Field(description="카테고리 ID")
    category_name: str = Field(description="카테고리 이름")
    total_decks: int = Field(description="카테고리 내 전체 덱 수")
    selected_decks: int = Field(description="선택된 덱 수")
    selection_state: str = Field(description="선택 상태: all | partial | none")


class SelectedDecksSummary(SQLModel):
    """선택된 덱 요약 정보."""

    course_name: str = Field(description="규칙에 따라 생성된 코스명")
    total_selected_decks: int = Field(description="선택된 총 덱 수")
    total_selected_cards: int = Field(description="선택된 덱의 총 카드 수")
    display_items: list[DisplayItem] = Field(description="UI 표시용 요약 항목")
    category_states: list[CategorySelectionState] = Field(
        description="카테고리별 선택 상태 (indeterminate UI용)"
    )


class GetSelectedDecksResponse(SQLModel):
    """선택된 덱 조회 응답 스키마."""

    select_all: bool = Field(description="전체 덱 선택 여부")
    deck_ids: list[int] = Field(description="선택된 덱 ID 목록 (select_all=true면 빈 배열)")
    decks: list[SelectedDeckInfo] = Field(
        description="선택된 덱의 상세 정보 목록 (select_all=true면 빈 배열)"
    )
    summary: SelectedDecksSummary | None = Field(
        default=None,
        description="선택된 덱 요약 정보 (select_all=true면 null)",
    )
