"""Tests for VocabularyCardService."""

from app.models import VocabularyCardCreate, VocabularyCardUpdate
from app.services.vocabulary_card_service import VocabularyCardService
from tests.factories.deck_factory import DeckFactory
from tests.factories.vocabulary_card_factory import VocabularyCardFactory


class TestVocabularyCardServiceCRUD:
    """Tests for VocabularyCard CRUD operations."""

    async def test_create_card(self, db_session):
        """Test creating a new vocabulary card."""
        card_data = VocabularyCardCreate(
            english_word="apple",
            korean_meaning="사과",
            part_of_speech="noun",
            cefr_level="A1",
            difficulty_level="beginner",
        )

        card = await VocabularyCardService.create_card(db_session, card_data)

        assert card is not None
        assert card.id is not None
        assert card.english_word == "apple"
        assert card.korean_meaning == "사과"
        assert card.cefr_level == "A1"
        assert card.difficulty_level == "beginner"

    async def test_get_card_by_id(self, db_session):
        """Test getting a card by ID."""
        created_card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="banana",
            korean_meaning="바나나",
        )

        retrieved_card = await VocabularyCardService.get_card(db_session, created_card.id)

        assert retrieved_card is not None
        assert retrieved_card.id == created_card.id
        assert retrieved_card.english_word == "banana"

    async def test_get_card_not_found(self, db_session):
        """Test getting a non-existent card returns None."""
        result = await VocabularyCardService.get_card(db_session, 99999)

        assert result is None

    async def test_get_cards_list(self, db_session):
        """Test getting a list of cards."""
        # Create multiple cards
        for i in range(5):
            await VocabularyCardFactory.create_async(
                db_session,
                english_word=f"word_{i}",
            )

        cards = await VocabularyCardService.get_cards(db_session, skip=0, limit=10)

        assert len(cards) == 5

    async def test_get_cards_with_pagination(self, db_session):
        """Test pagination in card list."""
        # Create 10 cards
        for i in range(10):
            await VocabularyCardFactory.create_async(
                db_session,
                english_word=f"word_{i}",
            )

        # Get first page
        first_page = await VocabularyCardService.get_cards(db_session, skip=0, limit=5)
        assert len(first_page) == 5

        # Get second page
        second_page = await VocabularyCardService.get_cards(db_session, skip=5, limit=5)
        assert len(second_page) == 5

        # Ensure no overlap
        first_page_ids = {c.id for c in first_page}
        second_page_ids = {c.id for c in second_page}
        assert first_page_ids.isdisjoint(second_page_ids)

    async def test_get_cards_filter_by_difficulty(self, db_session):
        """Test filtering cards by difficulty level."""
        # Create cards with different difficulties
        await VocabularyCardFactory.create_async(
            db_session, english_word="easy", difficulty_level="beginner"
        )
        await VocabularyCardFactory.create_async(
            db_session, english_word="medium", difficulty_level="intermediate"
        )
        await VocabularyCardFactory.create_async(
            db_session, english_word="hard", difficulty_level="advanced"
        )

        beginner_cards = await VocabularyCardService.get_cards(
            db_session, difficulty_level="beginner"
        )

        assert len(beginner_cards) == 1
        assert beginner_cards[0].difficulty_level == "beginner"

    async def test_get_cards_filter_by_deck(self, db_session):
        """Test filtering cards by deck_id."""
        # Create a deck and cards
        deck = await DeckFactory.create_async(db_session)

        await VocabularyCardFactory.create_async(
            db_session, english_word="in_deck", deck_id=deck.id
        )
        await VocabularyCardFactory.create_async(db_session, english_word="no_deck", deck_id=None)

        deck_cards = await VocabularyCardService.get_cards(db_session, deck_id=deck.id)

        assert len(deck_cards) == 1
        assert deck_cards[0].english_word == "in_deck"

    async def test_update_card(self, db_session):
        """Test updating a vocabulary card."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="original",
            korean_meaning="원래",
        )

        update_data = VocabularyCardUpdate(
            english_word="updated",
            korean_meaning="업데이트됨",
        )

        updated_card = await VocabularyCardService.update_card(db_session, card.id, update_data)

        assert updated_card is not None
        assert updated_card.english_word == "updated"
        assert updated_card.korean_meaning == "업데이트됨"

    async def test_update_card_partial(self, db_session):
        """Test partial update of a vocabulary card."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="original",
            korean_meaning="원래",
            cefr_level="A1",
        )

        update_data = VocabularyCardUpdate(cefr_level="B1")

        updated_card = await VocabularyCardService.update_card(db_session, card.id, update_data)

        assert updated_card is not None
        assert updated_card.english_word == "original"  # Unchanged
        assert updated_card.korean_meaning == "원래"  # Unchanged
        assert updated_card.cefr_level == "B1"  # Updated

    async def test_update_card_not_found(self, db_session):
        """Test updating a non-existent card returns None."""
        update_data = VocabularyCardUpdate(english_word="updated")

        result = await VocabularyCardService.update_card(db_session, 99999, update_data)

        assert result is None

    async def test_delete_card(self, db_session):
        """Test deleting a vocabulary card."""
        card = await VocabularyCardFactory.create_async(db_session)
        card_id = card.id

        result = await VocabularyCardService.delete_card(db_session, card_id)

        assert result is True

        # Verify deletion
        deleted_card = await VocabularyCardService.get_card(db_session, card_id)
        assert deleted_card is None

    async def test_delete_card_not_found(self, db_session):
        """Test deleting a non-existent card returns False."""
        result = await VocabularyCardService.delete_card(db_session, 99999)

        assert result is False


class TestGetRelatedWords:
    """Tests for get_related_words method."""

    async def test_get_related_words_with_data(self, db_session):
        """Test getting related words from card with related_words data."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="happy",
            korean_meaning="행복한",
            related_words=[
                {
                    "card_id": 123,
                    "word": "joyful",
                    "meaning": "즐거운",
                    "relation_type": "synonym",
                    "reason": "Similar positive emotion",
                },
                {
                    "card_id": None,
                    "word": "sad",
                    "meaning": "슬픈",
                    "relation_type": "antonym",
                    "reason": "Opposite emotion",
                },
            ],
        )

        result = VocabularyCardService.get_related_words(card)

        assert result.card.english_word == "happy"
        assert result.total_related == 2
        assert len(result.related_words) == 2

        # Check synonym
        synonym = next(r for r in result.related_words if r.relation_type == "synonym")
        assert synonym.english_word == "joyful"
        assert synonym.korean_meaning == "즐거운"
        assert synonym.relation_label == "유의어"
        assert synonym.card_id == 123

        # Check antonym
        antonym = next(r for r in result.related_words if r.relation_type == "antonym")
        assert antonym.english_word == "sad"
        assert antonym.relation_label == "반의어"
        assert antonym.card_id is None

    async def test_get_related_words_empty(self, db_session):
        """Test getting related words from card with no related_words."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="lonely",
            korean_meaning="외로운",
            related_words=None,
        )

        result = VocabularyCardService.get_related_words(card)

        assert result.card.english_word == "lonely"
        assert result.total_related == 0
        assert len(result.related_words) == 0

    async def test_get_related_words_unknown_relation_type(self, db_session):
        """Test related words with unknown relation_type gets '기타' label."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="test",
            korean_meaning="테스트",
            related_words=[
                {
                    "word": "related",
                    "meaning": "관련된",
                    "relation_type": "unknown_type",
                    "reason": "Some reason",
                }
            ],
        )

        result = VocabularyCardService.get_related_words(card)

        assert result.total_related == 1
        assert result.related_words[0].relation_label == "기타"

    async def test_get_related_words_all_relation_types(self, db_session):
        """Test all known relation types have correct labels."""
        card = await VocabularyCardFactory.create_async(
            db_session,
            english_word="word",
            korean_meaning="단어",
            related_words=[
                {"word": "w1", "meaning": "m1", "relation_type": "etymology", "reason": "r"},
                {"word": "w2", "meaning": "m2", "relation_type": "synonym", "reason": "r"},
                {"word": "w3", "meaning": "m3", "relation_type": "antonym", "reason": "r"},
                {"word": "w4", "meaning": "m4", "relation_type": "topic", "reason": "r"},
                {"word": "w5", "meaning": "m5", "relation_type": "collocation", "reason": "r"},
            ],
        )

        result = VocabularyCardService.get_related_words(card)

        assert result.total_related == 5

        labels = {r.relation_type: r.relation_label for r in result.related_words}
        assert labels["etymology"] == "어원"
        assert labels["synonym"] == "유의어"
        assert labels["antonym"] == "반의어"
        assert labels["topic"] == "주제 연관"
        assert labels["collocation"] == "연어"
