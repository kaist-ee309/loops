"""Tests for DeckService."""

from app.models import CardState
from app.services.deck_service import DeckService
from tests.factories.deck_factory import DeckFactory
from tests.factories.profile_factory import ProfileFactory
from tests.factories.user_card_progress_factory import UserCardProgressFactory
from tests.factories.vocabulary_card_factory import VocabularyCardFactory


class TestGetDecksList:
    """Tests for get_decks_list method."""

    async def test_get_decks_public(self, db_session):
        """Test getting public decks."""
        profile = await ProfileFactory.create_async(db_session)

        # Create public decks
        for i in range(3):
            await DeckFactory.create_async(db_session, name=f"Public Deck {i}", is_public=True)

        result = await DeckService.get_decks_list(db_session, profile.id)

        assert result.total == 3
        assert len(result.decks) == 3

    async def test_get_decks_user_created(self, db_session):
        """Test getting user-created private decks."""
        profile = await ProfileFactory.create_async(db_session)
        other_profile = await ProfileFactory.create_async(db_session)

        # Create user's private deck
        await DeckFactory.create_async(
            db_session,
            name="My Private Deck",
            is_public=False,
            creator_id=profile.id,
        )

        # Create another user's private deck (should not be visible)
        await DeckFactory.create_async(
            db_session,
            name="Other User's Deck",
            is_public=False,
            creator_id=other_profile.id,
        )

        result = await DeckService.get_decks_list(db_session, profile.id)

        # Should only see own deck
        assert result.total == 1
        assert result.decks[0].name == "My Private Deck"

    async def test_get_decks_pagination(self, db_session):
        """Test deck list pagination."""
        profile = await ProfileFactory.create_async(db_session)

        # Create 15 decks
        for i in range(15):
            await DeckFactory.create_async(db_session, name=f"Deck {i}", is_public=True)

        # Get first page
        first_page = await DeckService.get_decks_list(db_session, profile.id, skip=0, limit=10)
        assert len(first_page.decks) == 10
        assert first_page.total == 15

        # Get second page
        second_page = await DeckService.get_decks_list(db_session, profile.id, skip=10, limit=10)
        assert len(second_page.decks) == 5
        assert second_page.total == 15


class TestCalculateDeckProgress:
    """Tests for calculate_deck_progress method."""

    async def test_deck_progress_empty_deck(self, db_session):
        """Test progress calculation for empty deck."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session)
        # No cards in deck

        progress = await DeckService.calculate_deck_progress(db_session, profile.id, deck.id)

        assert progress["total_cards"] == 0
        assert progress["learned_cards"] == 0
        assert progress["learning_cards"] == 0
        assert progress["new_cards"] == 0
        assert progress["progress_percent"] == 0.0

    async def test_deck_progress_all_new(self, db_session):
        """Test progress when all cards are new (no progress)."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session)

        # Create cards without any progress
        for _ in range(5):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        progress = await DeckService.calculate_deck_progress(db_session, profile.id, deck.id)

        assert progress["total_cards"] == 5
        assert progress["new_cards"] == 5
        assert progress["learned_cards"] == 0
        assert progress["learning_cards"] == 0
        assert progress["progress_percent"] == 0.0

    async def test_deck_progress_mixed_states(self, db_session):
        """Test progress with cards in various states."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session)

        # Create cards with different states
        # 2 new cards (no progress)
        for _ in range(2):
            await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        # 2 learning cards
        for _ in range(2):
            card = await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                card_state=CardState.LEARNING,
            )

        # 3 learned (review) cards
        for _ in range(3):
            card = await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                card_state=CardState.REVIEW,
            )

        # 1 relearning card
        card = await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile.id,
            card_id=card.id,
            card_state=CardState.RELEARNING,
        )

        progress = await DeckService.calculate_deck_progress(db_session, profile.id, deck.id)

        assert progress["total_cards"] == 8
        assert progress["new_cards"] == 2
        assert progress["learning_cards"] == 3  # 2 LEARNING + 1 RELEARNING
        assert progress["learned_cards"] == 3
        assert progress["progress_percent"] == 37.5  # 3/8 * 100

    async def test_deck_progress_all_learned(self, db_session):
        """Test progress when all cards are mastered."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session)

        # Create all learned cards
        for _ in range(5):
            card = await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)
            await UserCardProgressFactory.create_async(
                db_session,
                user_id=profile.id,
                card_id=card.id,
                card_state=CardState.REVIEW,
            )

        progress = await DeckService.calculate_deck_progress(db_session, profile.id, deck.id)

        assert progress["total_cards"] == 5
        assert progress["learned_cards"] == 5
        assert progress["new_cards"] == 0
        assert progress["progress_percent"] == 100.0

    async def test_deck_progress_user_isolation(self, db_session):
        """Test that progress is calculated per-user."""
        profile1 = await ProfileFactory.create_async(db_session)
        profile2 = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session)

        # Create card in deck
        card = await VocabularyCardFactory.create_async(db_session, deck_id=deck.id)

        # Only user1 has learned it
        await UserCardProgressFactory.create_async(
            db_session,
            user_id=profile1.id,
            card_id=card.id,
            card_state=CardState.REVIEW,
        )

        # User1 should see it as learned
        progress1 = await DeckService.calculate_deck_progress(db_session, profile1.id, deck.id)
        assert progress1["learned_cards"] == 1
        assert progress1["new_cards"] == 0

        # User2 should see it as new
        progress2 = await DeckService.calculate_deck_progress(db_session, profile2.id, deck.id)
        assert progress2["learned_cards"] == 0
        assert progress2["new_cards"] == 1


class TestGetDeckById:
    """Tests for get_deck_by_id method."""

    async def test_get_existing_deck(self, db_session):
        """Test getting an existing deck."""
        deck = await DeckFactory.create_async(db_session, name="Test Deck")

        result = await DeckService.get_deck_by_id(db_session, deck.id)

        assert result is not None
        assert result.id == deck.id
        assert result.name == "Test Deck"

    async def test_get_nonexistent_deck(self, db_session):
        """Test getting a non-existent deck."""
        result = await DeckService.get_deck_by_id(db_session, 99999)

        assert result is None


class TestCheckDeckAccess:
    """Tests for check_deck_access method."""

    async def test_access_public_deck(self, db_session):
        """Test access to public deck."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session, is_public=True)

        result = await DeckService.check_deck_access(deck, profile.id)

        assert result is True

    async def test_access_own_private_deck(self, db_session):
        """Test access to own private deck."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session, is_public=False, creator_id=profile.id)

        result = await DeckService.check_deck_access(deck, profile.id)

        assert result is True

    async def test_no_access_to_others_private_deck(self, db_session):
        """Test no access to other's private deck."""
        profile = await ProfileFactory.create_async(db_session)
        other_profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(
            db_session, is_public=False, creator_id=other_profile.id
        )

        result = await DeckService.check_deck_access(deck, profile.id)

        assert result is False


class TestUpdateSelectedDecks:
    """Tests for update_selected_decks method."""

    async def test_update_select_all(self, db_session):
        """Test updating to select all decks."""
        profile = await ProfileFactory.create_async(db_session)

        success, deck_ids, error = await DeckService.update_selected_decks(
            db_session, profile.id, select_all=True, deck_ids=None
        )

        assert success is True
        assert deck_ids == []
        assert error is None

    async def test_update_select_specific_decks(self, db_session):
        """Test updating to select specific decks."""
        profile = await ProfileFactory.create_async(db_session)
        deck1 = await DeckFactory.create_async(db_session, is_public=True)
        deck2 = await DeckFactory.create_async(db_session, is_public=True)

        success, deck_ids, error = await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[deck1.id, deck2.id]
        )

        assert success is True
        assert set(deck_ids) == {deck1.id, deck2.id}
        assert error is None

    async def test_update_select_empty_deck_ids_error(self, db_session):
        """Test error when select_all=false but no deck_ids."""
        profile = await ProfileFactory.create_async(db_session)

        success, deck_ids, error = await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[]
        )

        assert success is False
        assert "deck_ids must be provided" in error

    async def test_update_select_nonexistent_deck_error(self, db_session):
        """Test error when deck_id doesn't exist."""
        profile = await ProfileFactory.create_async(db_session)

        success, deck_ids, error = await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[99999]
        )

        assert success is False
        assert "not found" in error


class TestGetSelectedDecksCategoryStates:
    """Additional tests for get_selected_decks (category state cases)."""

    async def test_get_selected_decks_select_all(self, db_session):
        """Test getting selected decks when select_all is True."""
        profile = await ProfileFactory.create_async(db_session)

        result = await DeckService.get_selected_decks(db_session, profile.id, select_all_decks=True)

        assert result.select_all is True
        assert result.deck_ids == []
        assert result.decks == []
        assert result.summary is None

    async def test_get_selected_decks_specific(self, db_session):
        """Test getting specific selected decks."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session, is_public=True)

        # Select the deck
        await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[deck.id]
        )

        result = await DeckService.get_selected_decks(
            db_session, profile.id, select_all_decks=False
        )

        assert result.select_all is False
        assert deck.id in result.deck_ids
        assert len(result.decks) == 1
        assert result.summary is not None


class TestGenerateCourseName:
    """Tests for _generate_course_name method."""

    def test_generate_course_name_no_selection(self):
        """Test course name with no selection."""
        course_name, display_items = DeckService._generate_course_name([], [])

        assert course_name == "선택된 단어장 없음"
        assert display_items == []

    def test_generate_course_name_single_category(self):
        """Test course name with single fully selected category."""
        fully_selected = [{"id": "exam", "name": "시험", "count": 5}]

        course_name, display_items = DeckService._generate_course_name([], fully_selected)

        assert course_name == "시험"
        assert len(display_items) == 1
        assert display_items[0].type == "category"

    def test_generate_course_name_multiple_categories(self):
        """Test course name with multiple fully selected categories."""
        fully_selected = [
            {"id": "exam", "name": "시험", "count": 5},
            {"id": "textbook", "name": "교과서", "count": 3},
        ]

        course_name, display_items = DeckService._generate_course_name([], fully_selected)

        assert course_name == "시험, 교과서"
        assert len(display_items) == 2

    def test_generate_course_name_many_categories(self):
        """Test course name with more than 3 fully selected categories."""

        fully_selected = [
            {"id": "exam", "name": "시험", "count": 5},
            {"id": "textbook", "name": "교과서", "count": 3},
            {"id": "daily", "name": "일상", "count": 2},
            {"id": "business", "name": "비즈니스", "count": 4},
        ]

        course_name, display_items = DeckService._generate_course_name([], fully_selected)

        assert "외 3개" in course_name
        assert len(display_items) == 4

    def test_generate_course_name_single_deck(self, db_session):
        """Test course name with a single deck selected."""
        from app.models import Deck

        # Create mock deck
        deck = Deck(id=1, name="테스트 덱", is_public=True)

        course_name, display_items = DeckService._generate_course_name([deck], [])

        assert course_name == "테스트 덱"
        assert len(display_items) == 1
        assert display_items[0].type == "deck"
        assert display_items[0].name == "테스트 덱"

    def test_generate_course_name_multiple_decks(self, db_session):
        """Test course name with multiple decks selected."""
        from app.models import Deck

        deck1 = Deck(id=1, name="덱 1", is_public=True)
        deck2 = Deck(id=2, name="덱 2", is_public=True)
        deck3 = Deck(id=3, name="덱 3", is_public=True)

        course_name, display_items = DeckService._generate_course_name([deck1, deck2, deck3], [])

        assert "덱 1 외 2개" in course_name
        assert len(display_items) == 3

    def test_generate_course_name_mixed_categories_and_decks(self, db_session):
        """Test course name with full categories and partial deck selections."""
        from app.models import Deck

        # Decks that belong to a category (not fully selected)
        deck1 = Deck(id=1, name="시험 덱 1", category="exam", is_public=True)
        # Deck from a different category (partial selection)
        deck2 = Deck(id=2, name="일상 덱 1", category="daily", is_public=True)

        fully_selected = [{"id": "business", "name": "비즈니스", "count": 3}]

        course_name, display_items = DeckService._generate_course_name(
            [deck1, deck2], fully_selected
        )

        # Both decks are partial (not in fully selected category)
        assert "외" in course_name
        assert len(display_items) == 3  # 1 category + 2 decks


class TestGetCategories:
    """Tests for get_categories method."""

    async def test_get_categories_returns_list(self, db_session):
        """Test that get_categories returns a list."""
        profile = await ProfileFactory.create_async(db_session)

        # Create some decks in different categories
        await DeckFactory.create_async(db_session, is_public=True, category="exam")
        await DeckFactory.create_async(db_session, is_public=True, category="daily")

        result = await DeckService.get_categories(db_session, profile.id)

        assert isinstance(result, list)
        # Check that exam and daily categories are included
        category_ids = [cat.id for cat in result]
        assert "exam" in category_ids
        assert "daily" in category_ids

    async def test_get_categories_with_selected_decks(self, db_session):
        """Test category selection state with selected decks."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session, is_public=True, category="exam")

        # Select the deck
        await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[deck.id]
        )

        result = await DeckService.get_categories(db_session, profile.id)

        exam_cat = next((c for c in result if c.id == "exam"), None)
        assert exam_cat is not None
        assert exam_cat.selected_decks >= 1


class TestGetCategoryDecks:
    """Tests for get_category_decks method."""

    async def test_get_category_decks_valid_category(self, db_session):
        """Test getting decks for a valid category."""
        profile = await ProfileFactory.create_async(db_session)
        await DeckFactory.create_async(db_session, is_public=True, category="exam")

        category_detail, decks_list, total, selected = await DeckService.get_category_decks(
            db_session, profile.id, "exam"
        )

        assert category_detail is not None
        assert category_detail.id == "exam"
        assert len(decks_list) >= 1
        assert total >= 1

    async def test_get_category_decks_invalid_category(self, db_session):
        """Test getting decks for an invalid category."""
        profile = await ProfileFactory.create_async(db_session)

        category_detail, decks_list, total, selected = await DeckService.get_category_decks(
            db_session, profile.id, "nonexistent_category"
        )

        assert category_detail is None
        assert decks_list == []
        assert total == 0
        assert selected == 0

    async def test_get_category_decks_with_selected(self, db_session):
        """Test getting category decks with some selected."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session, is_public=True, category="exam")

        # Select the deck
        await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[deck.id]
        )

        category_detail, decks_list, total, selected = await DeckService.get_category_decks(
            db_session, profile.id, "exam"
        )

        assert selected >= 1
        # Check that deck is marked as selected
        deck_info = next((d for d in decks_list if d.id == deck.id), None)
        assert deck_info is not None
        assert deck_info.is_selected is True


class TestSelectAllCategoryDecks:
    """Tests for select_all_category_decks method."""

    async def test_select_all_valid_category(self, db_session):
        """Test selecting all decks in a valid category."""
        profile = await ProfileFactory.create_async(db_session)
        await DeckFactory.create_async(db_session, is_public=True, category="exam")
        await DeckFactory.create_async(db_session, is_public=True, category="exam")

        success, total, added, error = await DeckService.select_all_category_decks(
            db_session, profile.id, "exam"
        )

        assert success is True
        assert total >= 2
        assert added >= 2
        assert error is None

    async def test_select_all_invalid_category(self, db_session):
        """Test selecting all decks in an invalid category."""
        profile = await ProfileFactory.create_async(db_session)

        success, total, added, error = await DeckService.select_all_category_decks(
            db_session, profile.id, "nonexistent_category"
        )

        assert success is False
        assert error is not None
        assert "not found" in error

    async def test_select_all_already_selected(self, db_session):
        """Test selecting all when some are already selected."""
        profile = await ProfileFactory.create_async(db_session)
        deck1 = await DeckFactory.create_async(db_session, is_public=True, category="exam")
        await DeckFactory.create_async(db_session, is_public=True, category="exam")

        # Select first deck
        await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[deck1.id]
        )

        # Select all in category
        success, total, added, error = await DeckService.select_all_category_decks(
            db_session, profile.id, "exam"
        )

        assert success is True
        assert added >= 1  # At least one new deck was added


class TestDeselectAllCategoryDecks:
    """Tests for deselect_all_category_decks method."""

    async def test_deselect_all_valid_category(self, db_session):
        """Test deselecting all decks in a valid category."""
        profile = await ProfileFactory.create_async(db_session)
        deck = await DeckFactory.create_async(db_session, is_public=True, category="exam")

        # First select the deck
        await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[deck.id]
        )

        # Now deselect all in category
        success, removed, error = await DeckService.deselect_all_category_decks(
            db_session, profile.id, "exam"
        )

        assert success is True
        assert removed >= 1
        assert error is None

    async def test_deselect_all_invalid_category(self, db_session):
        """Test deselecting all decks in an invalid category."""
        profile = await ProfileFactory.create_async(db_session)

        success, removed, error = await DeckService.deselect_all_category_decks(
            db_session, profile.id, "nonexistent_category"
        )

        assert success is False
        assert error is not None
        assert "not found" in error

    async def test_deselect_all_none_selected(self, db_session):
        """Test deselecting all when none are selected."""
        profile = await ProfileFactory.create_async(db_session)
        await DeckFactory.create_async(db_session, is_public=True, category="exam")

        success, removed, error = await DeckService.deselect_all_category_decks(
            db_session, profile.id, "exam"
        )

        assert success is True
        assert removed == 0
        assert error is None


class TestGetSelectedDecks:
    """Tests for get_selected_decks method."""

    async def test_get_selected_decks_with_category_states(self, db_session):
        """Test getting selected decks includes category states."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=False)

        # Create decks in a category
        deck1 = await DeckFactory.create_async(
            db_session, is_public=True, category="exam", name="TOEFL Deck"
        )
        await DeckFactory.create_async(
            db_session, is_public=True, category="exam", name="IELTS Deck"
        )

        # Select only deck1
        await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[deck1.id]
        )

        result = await DeckService.get_selected_decks(
            db_session, profile.id, select_all_decks=False
        )

        # Should have category states showing partial selection
        assert result is not None
        assert len(result.decks) >= 1

    async def test_get_selected_decks_with_all_selected_category(self, db_session):
        """Test category shows 'all' when all decks selected."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=False)

        # Create all decks in one category
        await DeckFactory.create_async(db_session, is_public=True, category="exam")

        # Select all decks in that category
        await DeckService.select_all_category_decks(db_session, profile.id, "exam")

        result = await DeckService.get_selected_decks(
            db_session, profile.id, select_all_decks=False
        )

        # Check result is valid
        assert result is not None
        assert len(result.decks) >= 1

    async def test_get_selected_decks_empty_no_selected(self, db_session):
        """Test getting selected decks when none are selected."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=False)

        # Don't select any decks

        result = await DeckService.get_selected_decks(
            db_session, profile.id, select_all_decks=False
        )

        assert result is not None
        assert len(result.decks) == 0

    async def test_get_selected_decks_select_all_mode(self, db_session):
        """Test get_selected_decks in select_all mode returns early."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=True)

        result = await DeckService.get_selected_decks(db_session, profile.id, select_all_decks=True)

        assert result is not None
        assert result.select_all is True
        assert len(result.decks) == 0


class TestGetCategoriesSelectionState:
    """Additional tests for get_categories selection_state edge cases."""

    async def test_get_categories_with_partial_selection(self, db_session):
        """Test category shows partial selection state."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=False)

        # Create multiple decks in same category
        deck1 = await DeckFactory.create_async(db_session, is_public=True, category="exam")
        await DeckFactory.create_async(db_session, is_public=True, category="exam")
        await DeckFactory.create_async(db_session, is_public=True, category="exam")

        # Select only one
        await DeckService.update_selected_decks(
            db_session, profile.id, select_all=False, deck_ids=[deck1.id]
        )

        result = await DeckService.get_categories(db_session, profile.id)

        exam_cat = next((c for c in result if c.id == "exam"), None)
        assert exam_cat is not None
        assert exam_cat.selection_state == "partial"

    async def test_get_categories_with_no_selection(self, db_session):
        """Test category shows none selection state when no decks selected."""
        profile = await ProfileFactory.create_async(db_session, select_all_decks=False)

        # Create decks but don't select any
        await DeckFactory.create_async(db_session, is_public=True, category="exam")

        result = await DeckService.get_categories(db_session, profile.id)

        exam_cat = next((c for c in result if c.id == "exam"), None)
        assert exam_cat is not None
        assert exam_cat.selection_state == "none"
