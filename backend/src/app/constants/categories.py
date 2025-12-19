"""
Category metadata for deck categorization.

These categories are used to group decks for better organization and navigation.
"""

from typing import TypedDict


class CategoryMetadata(TypedDict):
    """Category metadata structure."""

    name: str
    description: str
    icon: str


# Category metadata dictionary
CATEGORIES: dict[str, CategoryMetadata] = {
    "exam": {
        "name": "시험",
        "description": "TOEFL, TOEIC, IELTS 등 시험 대비 단어장",
        "icon": "📝",
    },
    "textbook": {
        "name": "교과서",
        "description": "학교 교과서 기반 단어장",
        "icon": "📚",
    },
    "situation": {
        "name": "상황별",
        "description": "여행, 비즈니스 등 상황별 단어장",
        "icon": "💬",
    },
    "business": {
        "name": "비즈니스",
        "description": "업무, 회의, 이메일 등 비즈니스 영어",
        "icon": "💼",
    },
    "daily": {
        "name": "일상",
        "description": "일상생활에서 자주 쓰는 표현",
        "icon": "🏠",
    },
    "academic": {
        "name": "학술",
        "description": "논문, 학술 자료에서 사용하는 단어",
        "icon": "🎓",
    },
}


def get_category_metadata(category_id: str) -> CategoryMetadata | None:
    """Get category metadata by ID."""
    return CATEGORIES.get(category_id)


def get_all_category_ids() -> list[str]:
    """Get all category IDs."""
    return list(CATEGORIES.keys())
