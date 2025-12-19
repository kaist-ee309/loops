from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    CardSummary,
    RelatedWordInfo,
    RelatedWordsResponse,
    VocabularyCard,
    VocabularyCardCreate,
    VocabularyCardUpdate,
)

# relation_type -> Korean label mapping
RELATION_TYPE_LABELS = {
    "etymology": "어원",
    "synonym": "유의어",
    "antonym": "반의어",
    "topic": "주제 연관",
    "collocation": "연어",
}


class VocabularyCardService:
    """Service for vocabulary card CRUD operations."""

    @staticmethod
    async def create_card(session: AsyncSession, card_data: VocabularyCardCreate) -> VocabularyCard:
        """Create a new vocabulary card."""
        card = VocabularyCard(**card_data.model_dump())
        session.add(card)
        await session.commit()
        await session.refresh(card)
        return card

    @staticmethod
    async def get_card(session: AsyncSession, card_id: int) -> VocabularyCard | None:
        """Get a vocabulary card by ID."""
        return await session.get(VocabularyCard, card_id)

    @staticmethod
    async def get_cards(
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        difficulty_level: str | None = None,
        deck_id: int | None = None,
    ) -> list[VocabularyCard]:
        """Get a list of vocabulary cards with optional filtering."""
        statement = select(VocabularyCard)

        if difficulty_level:
            statement = statement.where(VocabularyCard.difficulty_level == difficulty_level)
        if deck_id is not None:
            statement = statement.where(VocabularyCard.deck_id == deck_id)

        statement = statement.offset(skip).limit(limit)
        result = await session.exec(statement)
        return list(result.all())

    @staticmethod
    async def update_card(
        session: AsyncSession, card_id: int, card_data: VocabularyCardUpdate
    ) -> VocabularyCard | None:
        """Update a vocabulary card."""
        card = await VocabularyCardService.get_card(session, card_id)
        if not card:
            return None

        update_dict = card_data.model_dump(exclude_unset=True)
        card.sqlmodel_update(update_dict)

        session.add(card)
        await session.commit()
        await session.refresh(card)
        return card

    @staticmethod
    async def delete_card(session: AsyncSession, card_id: int) -> bool:
        """Delete a vocabulary card."""
        card = await VocabularyCardService.get_card(session, card_id)
        if not card:
            return False

        await session.delete(card)
        await session.commit()
        return True

    @staticmethod
    def get_related_words(card: VocabularyCard) -> RelatedWordsResponse:
        """
        Get related words for a vocabulary card.

        Transforms the card's related_words JSON data into a structured response.

        Args:
            card: VocabularyCard instance with related_words data

        Returns:
            RelatedWordsResponse with card summary and related words list
        """
        card_summary = CardSummary(
            id=card.id,
            english_word=card.english_word,
            korean_meaning=card.korean_meaning,
        )

        related_words: list[RelatedWordInfo] = []

        if card.related_words:
            for related in card.related_words:
                if isinstance(related, dict):
                    relation_type = related.get("relation_type", "topic")
                    related_words.append(
                        RelatedWordInfo(
                            card_id=related.get("card_id"),
                            english_word=related.get("word", ""),
                            korean_meaning=related.get("meaning", ""),
                            relation_type=relation_type,
                            relation_label=RELATION_TYPE_LABELS.get(relation_type, "기타"),
                            reason=related.get("reason", ""),
                        )
                    )

        return RelatedWordsResponse(
            card=card_summary,
            related_words=related_words,
            total_related=len(related_words),
        )
