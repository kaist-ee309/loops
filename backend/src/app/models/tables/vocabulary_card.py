from datetime import datetime
from typing import Any

from sqlmodel import JSON, Column, Field, SQLModel

from app.models.base import TimestampMixin


class VocabularyCardBase(SQLModel):
    """Base VocabularyCard model with shared fields."""

    english_word: str = Field(max_length=255, index=True)
    korean_meaning: str = Field(max_length=255)
    part_of_speech: str | None = Field(default=None, max_length=50)  # noun, verb, adjective, etc.

    # Pronunciation
    pronunciation_ipa: str | None = Field(default=None, max_length=255)  # /ˈkɒntrækt/

    # Definition
    definition_en: str | None = Field(default=None)  # English definition

    # Entry type
    word_type: str | None = Field(
        default="word", max_length=50, index=True
    )  # word, phrase, idiom, collocation

    # Categorization
    difficulty_level: str | None = Field(
        default=None, max_length=50, index=True
    )  # beginner, intermediate, advanced
    cefr_level: str | None = Field(default=None, max_length=10)  # A1-C2
    category: str | None = Field(
        default=None, max_length=50
    )  # DB-6: e.g., "business", "travel", "academic"

    # Word frequency and selection (DB-5)
    frequency_rank: int | None = Field(
        default=None, index=True
    )  # Lower rank = more common word (1=most common)

    # Audio (DB-9)
    audio_url: str | None = Field(
        default=None, max_length=500
    )  # Path or URL to pronunciation audio

    # Deck Organization
    deck_id: int | None = Field(default=None, foreign_key="decks.id", index=True)

    # Metadata
    is_verified: bool = Field(default=False)  # Verified card status


class VocabularyCard(VocabularyCardBase, TimestampMixin, table=True):
    """VocabularyCard database model."""

    __tablename__ = "vocabulary_cards"

    id: int | None = Field(default=None, primary_key=True, nullable=False)

    # JSONB fields for complex data
    # Format: [{"en": "...", "ko": "...", "context": "business"}, ...]
    example_sentences: dict[str, Any] | list[Any] | None = Field(
        default=None, sa_column=Column(JSON)
    )

    # Format: ["business", "IT", "TOEIC"]
    tags: dict[str, Any] | list[Any] | None = Field(default=None, sa_column=Column(JSON))

    # Pre-generated cloze sentences for quiz mode
    # Format: [{"sentence": "The company signed a _____ with...", "answer": "contract", "hint": "계약"}, ...]
    cloze_sentences: dict[str, Any] | list[Any] | None = Field(default=None, sa_column=Column(JSON))

    # Related words for association network (Issue #51)
    # Format: [{"word": "renovate", "meaning": "혁신하다", "relation_type": "etymology", "reason": "같은 어원 nov-"}, ...]
    related_words: dict[str, Any] | list[Any] | None = Field(default=None, sa_column=Column(JSON))

    # Image association learning (Gemini-generated)
    image_url: str | None = Field(default=None, max_length=500)
    image_storage_path: str | None = Field(default=None, max_length=500)
    image_prompt: str | None = Field(default=None)
    image_model: str | None = Field(default=None, max_length=100)
    image_status: str | None = Field(default=None, max_length=20)  # pending|ready|failed
    image_error: str | None = Field(default=None)
    image_generated_at: datetime | None = Field(default=None)
