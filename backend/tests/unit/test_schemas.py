"""Tests for Pydantic schemas."""

import pytest
from pydantic import ValidationError


class TestVocabularyCardSchemas:
    """Tests for vocabulary card schemas."""

    def test_card_create_validation(self):
        """Test VocabularyCardCreate validation."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        # Valid card
        card = VocabularyCardCreate(
            english_word="apple",
            korean_meaning="사과",
        )
        assert card.english_word == "apple"

    def test_card_create_requires_english_word(self):
        """Test that english_word is required."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        with pytest.raises(ValidationError):
            VocabularyCardCreate(korean_meaning="사과")

    def test_card_read_schema(self):
        """Test VocabularyCardRead schema."""
        from datetime import datetime

        from app.models.schemas.vocabulary_card import VocabularyCardRead

        card = VocabularyCardRead(
            id=1,
            english_word="apple",
            korean_meaning="사과",
            created_at=datetime.utcnow(),
        )
        assert card.id == 1
        assert card.english_word == "apple"

    def test_card_create_empty_english_word_raises_error(self):
        """Test that empty english_word raises ValidationError."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        with pytest.raises(ValidationError) as exc_info:
            VocabularyCardCreate(english_word="   ", korean_meaning="사과")
        assert "empty or whitespace" in str(exc_info.value).lower()

    def test_card_create_invalid_cefr_level_raises_error(self):
        """Test that invalid CEFR level raises ValidationError."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        with pytest.raises(ValidationError) as exc_info:
            VocabularyCardCreate(
                english_word="apple",
                korean_meaning="사과",
                cefr_level="X1",
            )
        assert "cefr level" in str(exc_info.value).lower()

    def test_card_create_valid_cefr_level(self):
        """Test that valid CEFR level is accepted."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        card = VocabularyCardCreate(
            english_word="apple",
            korean_meaning="사과",
            cefr_level="b1",  # lowercase should be normalized to uppercase
        )
        assert card.cefr_level == "B1"

    def test_card_create_invalid_difficulty_level_raises_error(self):
        """Test that invalid difficulty level raises ValidationError."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        with pytest.raises(ValidationError) as exc_info:
            VocabularyCardCreate(
                english_word="apple",
                korean_meaning="사과",
                difficulty_level="expert",
            )
        assert "difficulty level" in str(exc_info.value).lower()

    def test_card_create_valid_difficulty_level(self):
        """Test that valid difficulty level is accepted."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        card = VocabularyCardCreate(
            english_word="apple",
            korean_meaning="사과",
            difficulty_level="BEGINNER",  # uppercase should be normalized
        )
        assert card.difficulty_level == "beginner"

    def test_card_create_invalid_word_type_raises_error(self):
        """Test that invalid word_type raises ValidationError."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        with pytest.raises(ValidationError) as exc_info:
            VocabularyCardCreate(
                english_word="apple",
                korean_meaning="사과",
                word_type="invalid_type",
            )
        assert "word type" in str(exc_info.value).lower()

    def test_card_create_word_type_default_to_word(self):
        """Test that None word_type defaults to 'word'."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        card = VocabularyCardCreate(
            english_word="apple",
            korean_meaning="사과",
            word_type=None,
        )
        assert card.word_type == "word"

    def test_card_create_valid_word_type(self):
        """Test that valid word_type is accepted."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        for word_type in ["word", "phrase", "idiom", "collocation"]:
            card = VocabularyCardCreate(
                english_word="apple",
                korean_meaning="사과",
                word_type=word_type.upper(),
            )
            assert card.word_type == word_type

    def test_card_create_tags_cleaned(self):
        """Test that tags are cleaned (empty strings removed)."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        card = VocabularyCardCreate(
            english_word="apple",
            korean_meaning="사과",
            tags=["fruit", "", "  ", "food"],
        )
        assert card.tags == ["fruit", "food"]

    def test_card_create_tags_all_empty_returns_none(self):
        """Test that all empty tags returns None."""
        from app.models.schemas.vocabulary_card import VocabularyCardCreate

        card = VocabularyCardCreate(
            english_word="apple",
            korean_meaning="사과",
            tags=["", "  ", ""],
        )
        assert card.tags is None

    def test_card_update_empty_english_word_raises_error(self):
        """Test VocabularyCardUpdate with empty english_word."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        with pytest.raises(ValidationError) as exc_info:
            VocabularyCardUpdate(english_word="   ")
        assert "empty or whitespace" in str(exc_info.value).lower()

    def test_card_update_none_english_word_allowed(self):
        """Test VocabularyCardUpdate allows None for english_word."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        update = VocabularyCardUpdate(english_word=None)
        assert update.english_word is None

    def test_card_update_invalid_cefr_level_raises_error(self):
        """Test VocabularyCardUpdate with invalid CEFR level."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        with pytest.raises(ValidationError) as exc_info:
            VocabularyCardUpdate(cefr_level="Z9")
        assert "cefr level" in str(exc_info.value).lower()

    def test_card_update_valid_cefr_level(self):
        """Test VocabularyCardUpdate with valid CEFR level."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        update = VocabularyCardUpdate(cefr_level="c2")
        assert update.cefr_level == "C2"

    def test_card_update_invalid_difficulty_level_raises_error(self):
        """Test VocabularyCardUpdate with invalid difficulty level."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        with pytest.raises(ValidationError) as exc_info:
            VocabularyCardUpdate(difficulty_level="super_hard")
        assert "difficulty level" in str(exc_info.value).lower()

    def test_card_update_valid_difficulty_level(self):
        """Test VocabularyCardUpdate with valid difficulty level."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        update = VocabularyCardUpdate(difficulty_level="ADVANCED")
        assert update.difficulty_level == "advanced"

    def test_card_update_invalid_word_type_raises_error(self):
        """Test VocabularyCardUpdate with invalid word_type."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        with pytest.raises(ValidationError) as exc_info:
            VocabularyCardUpdate(word_type="sentence")
        assert "word type" in str(exc_info.value).lower()

    def test_card_update_valid_word_type(self):
        """Test VocabularyCardUpdate with valid word_type."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        update = VocabularyCardUpdate(word_type="IDIOM")
        assert update.word_type == "idiom"

    def test_card_update_none_word_type_stays_none(self):
        """Test VocabularyCardUpdate None word_type stays None."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        update = VocabularyCardUpdate(word_type=None)
        assert update.word_type is None

    def test_card_update_tags_cleaned(self):
        """Test VocabularyCardUpdate tags are cleaned."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        update = VocabularyCardUpdate(tags=["tag1", "", "  ", "tag2"])
        assert update.tags == ["tag1", "tag2"]

    def test_card_update_tags_all_empty_returns_none(self):
        """Test VocabularyCardUpdate all empty tags returns None."""
        from app.models.schemas.vocabulary_card import VocabularyCardUpdate

        update = VocabularyCardUpdate(tags=["", "   "])
        assert update.tags is None


class TestProfileSchemas:
    """Tests for profile schemas."""

    def test_profile_update_validation(self):
        """Test ProfileUpdate validation."""
        from app.models.schemas.profile import ProfileUpdate

        # Valid update with partial fields
        update = ProfileUpdate(daily_goal=30)
        assert update.daily_goal == 30

    def test_profile_config_read(self):
        """Test ProfileConfigRead schema."""
        from app.models.schemas.profile import ProfileConfigRead

        config = ProfileConfigRead(
            select_all_decks=True,
            daily_goal=20,
            review_ratio_mode="normal",
            custom_review_ratio=0.75,
            min_new_ratio=0.25,
            review_scope="selected_decks_only",
            timezone="UTC",
            theme="auto",
            notification_enabled=True,
            highlight_color="#4CAF50",
        )
        assert config.daily_goal == 20
        assert config.theme == "auto"

    def test_profile_update_invalid_theme_raises_error(self):
        """Test ProfileUpdate with invalid theme raises error."""
        from app.models.schemas.profile import ProfileUpdate

        with pytest.raises(ValidationError) as exc_info:
            ProfileUpdate(theme="invalid_theme")
        assert "theme must be one of" in str(exc_info.value).lower()

    def test_profile_update_valid_theme(self):
        """Test ProfileUpdate with valid theme values."""
        from app.models.schemas.profile import ProfileUpdate

        for theme in ["light", "dark", "auto"]:
            update = ProfileUpdate(theme=theme)
            assert update.theme == theme

    def test_profile_update_none_theme_allowed(self):
        """Test ProfileUpdate allows None theme."""
        from app.models.schemas.profile import ProfileUpdate

        update = ProfileUpdate(theme=None)
        assert update.theme is None

    def test_profile_update_invalid_review_ratio_mode_raises_error(self):
        """Test ProfileUpdate with invalid review_ratio_mode raises error."""
        from app.models.schemas.profile import ProfileUpdate

        with pytest.raises(ValidationError) as exc_info:
            ProfileUpdate(review_ratio_mode="invalid_mode")
        assert "review ratio mode must be one of" in str(exc_info.value).lower()

    def test_profile_update_valid_review_ratio_mode(self):
        """Test ProfileUpdate with valid review_ratio_mode values."""
        from app.models.schemas.profile import ProfileUpdate

        for mode in ["normal", "custom"]:
            update = ProfileUpdate(review_ratio_mode=mode)
            assert update.review_ratio_mode == mode

    def test_profile_update_none_review_ratio_mode_allowed(self):
        """Test ProfileUpdate allows None review_ratio_mode."""
        from app.models.schemas.profile import ProfileUpdate

        update = ProfileUpdate(review_ratio_mode=None)
        assert update.review_ratio_mode is None

    def test_profile_update_invalid_review_scope_raises_error(self):
        """Test ProfileUpdate with invalid review_scope raises error."""
        from app.models.schemas.profile import ProfileUpdate

        with pytest.raises(ValidationError) as exc_info:
            ProfileUpdate(review_scope="invalid_scope")
        assert "review scope must be one of" in str(exc_info.value).lower()

    def test_profile_update_valid_review_scope(self):
        """Test ProfileUpdate with valid review_scope values."""
        from app.models.schemas.profile import ProfileUpdate

        for scope in ["selected_decks_only", "all_learned"]:
            update = ProfileUpdate(review_scope=scope)
            assert update.review_scope == scope

    def test_profile_update_none_review_scope_allowed(self):
        """Test ProfileUpdate allows None review_scope."""
        from app.models.schemas.profile import ProfileUpdate

        update = ProfileUpdate(review_scope=None)
        assert update.review_scope is None

    def test_profile_config_update_invalid_theme_raises_error(self):
        """Test ProfileConfigUpdate with invalid theme raises error."""
        from app.models.schemas.profile import ProfileConfigUpdate

        with pytest.raises(ValidationError) as exc_info:
            ProfileConfigUpdate(theme="neon")
        assert "theme must be one of" in str(exc_info.value).lower()

    def test_profile_config_update_valid_theme(self):
        """Test ProfileConfigUpdate with valid theme values."""
        from app.models.schemas.profile import ProfileConfigUpdate

        for theme in ["light", "dark", "auto"]:
            update = ProfileConfigUpdate(theme=theme)
            assert update.theme == theme

    def test_profile_config_update_none_theme_allowed(self):
        """Test ProfileConfigUpdate allows None theme."""
        from app.models.schemas.profile import ProfileConfigUpdate

        update = ProfileConfigUpdate(theme=None)
        assert update.theme is None

    def test_profile_config_update_invalid_review_ratio_mode_raises_error(self):
        """Test ProfileConfigUpdate with invalid review_ratio_mode raises error."""
        from app.models.schemas.profile import ProfileConfigUpdate

        with pytest.raises(ValidationError) as exc_info:
            ProfileConfigUpdate(review_ratio_mode="auto")
        assert "review ratio mode must be one of" in str(exc_info.value).lower()

    def test_profile_config_update_valid_review_ratio_mode(self):
        """Test ProfileConfigUpdate with valid review_ratio_mode values."""
        from app.models.schemas.profile import ProfileConfigUpdate

        for mode in ["normal", "custom"]:
            update = ProfileConfigUpdate(review_ratio_mode=mode)
            assert update.review_ratio_mode == mode

    def test_profile_config_update_none_review_ratio_mode_allowed(self):
        """Test ProfileConfigUpdate allows None review_ratio_mode."""
        from app.models.schemas.profile import ProfileConfigUpdate

        update = ProfileConfigUpdate(review_ratio_mode=None)
        assert update.review_ratio_mode is None

    def test_profile_config_update_invalid_review_scope_raises_error(self):
        """Test ProfileConfigUpdate with invalid review_scope raises error."""
        from app.models.schemas.profile import ProfileConfigUpdate

        with pytest.raises(ValidationError) as exc_info:
            ProfileConfigUpdate(review_scope="everywhere")
        assert "review scope must be one of" in str(exc_info.value).lower()

    def test_profile_config_update_valid_review_scope(self):
        """Test ProfileConfigUpdate with valid review_scope values."""
        from app.models.schemas.profile import ProfileConfigUpdate

        for scope in ["selected_decks_only", "all_learned"]:
            update = ProfileConfigUpdate(review_scope=scope)
            assert update.review_scope == scope

    def test_profile_config_update_none_review_scope_allowed(self):
        """Test ProfileConfigUpdate allows None review_scope."""
        from app.models.schemas.profile import ProfileConfigUpdate

        update = ProfileConfigUpdate(review_scope=None)
        assert update.review_scope is None


class TestDeckSchemas:
    """Tests for deck schemas."""

    def test_deck_create_validation(self):
        """Test DeckCreate validation."""
        from app.models.schemas.deck import DeckCreate

        deck = DeckCreate(
            name="Test Deck",
            description="A test deck",
            category="exam",
            is_public=True,
        )
        assert deck.name == "Test Deck"
        assert deck.is_public is True

    def test_deck_create_requires_name(self):
        """Test that name is required."""
        from app.models.schemas.deck import DeckCreate

        with pytest.raises(ValidationError):
            DeckCreate(description="No name provided")

    def test_deck_create_empty_name_raises_error(self):
        """Test DeckCreate with empty name raises error."""
        from app.models.schemas.deck import DeckCreate

        with pytest.raises(ValidationError) as exc_info:
            DeckCreate(name="   ", description="Empty name deck")
        assert "empty or whitespace" in str(exc_info.value).lower()

    def test_deck_create_name_stripped(self):
        """Test DeckCreate name is stripped."""
        from app.models.schemas.deck import DeckCreate

        deck = DeckCreate(name="  Test Deck  ")
        assert deck.name == "Test Deck"

    def test_deck_create_invalid_difficulty_level_raises_error(self):
        """Test DeckCreate with invalid difficulty level raises error."""
        from app.models.schemas.deck import DeckCreate

        with pytest.raises(ValidationError) as exc_info:
            DeckCreate(name="Test Deck", difficulty_level="expert")
        assert "difficulty level must be one of" in str(exc_info.value).lower()

    def test_deck_create_valid_difficulty_level(self):
        """Test DeckCreate with valid difficulty levels."""
        from app.models.schemas.deck import DeckCreate

        for level in ["beginner", "intermediate", "advanced"]:
            deck = DeckCreate(name="Test Deck", difficulty_level=level.upper())
            assert deck.difficulty_level == level

    def test_deck_create_none_difficulty_level_allowed(self):
        """Test DeckCreate allows None difficulty level."""
        from app.models.schemas.deck import DeckCreate

        deck = DeckCreate(name="Test Deck", difficulty_level=None)
        assert deck.difficulty_level is None

    def test_deck_update_empty_name_raises_error(self):
        """Test DeckUpdate with empty name raises error."""
        from app.models.schemas.deck import DeckUpdate

        with pytest.raises(ValidationError) as exc_info:
            DeckUpdate(name="   ")
        assert "empty or whitespace" in str(exc_info.value).lower()

    def test_deck_update_none_name_allowed(self):
        """Test DeckUpdate allows None name."""
        from app.models.schemas.deck import DeckUpdate

        update = DeckUpdate(name=None)
        assert update.name is None

    def test_deck_update_name_stripped(self):
        """Test DeckUpdate name is stripped."""
        from app.models.schemas.deck import DeckUpdate

        update = DeckUpdate(name="  Updated Name  ")
        assert update.name == "Updated Name"

    def test_deck_update_invalid_difficulty_level_raises_error(self):
        """Test DeckUpdate with invalid difficulty level raises error."""
        from app.models.schemas.deck import DeckUpdate

        with pytest.raises(ValidationError) as exc_info:
            DeckUpdate(difficulty_level="super_hard")
        assert "difficulty level must be one of" in str(exc_info.value).lower()

    def test_deck_update_valid_difficulty_level(self):
        """Test DeckUpdate with valid difficulty levels."""
        from app.models.schemas.deck import DeckUpdate

        for level in ["beginner", "intermediate", "advanced"]:
            update = DeckUpdate(difficulty_level=level.upper())
            assert update.difficulty_level == level

    def test_deck_update_none_difficulty_level_allowed(self):
        """Test DeckUpdate allows None difficulty level."""
        from app.models.schemas.deck import DeckUpdate

        update = DeckUpdate(difficulty_level=None)
        assert update.difficulty_level is None


class TestStudySchemas:
    """Tests for study-related schemas."""

    def test_session_preview_request(self):
        """Test SessionPreviewRequest schema."""
        from app.models.schemas.study import SessionPreviewRequest

        request = SessionPreviewRequest(
            total_cards=20,
            review_ratio=0.5,
        )
        assert request.total_cards == 20
        assert request.review_ratio == 0.5

    def test_cloze_question_schema(self):
        """Test ClozeQuestion schema."""
        from app.models.schemas.study import ClozeQuestion

        cloze = ClozeQuestion(
            sentence="I like ______ very much.",
            answer="apple",
            hint="과일",
        )
        assert cloze.sentence == "I like ______ very much."
        assert cloze.answer == "apple"


class TestWrongAnswerSchemas:
    """Tests for wrong answer schemas."""

    def test_wrong_answer_read(self):
        """Test WrongAnswerRead schema."""
        from datetime import datetime

        from app.models.schemas.wrong_answer import WrongAnswerCardInfo, WrongAnswerRead

        card_info = WrongAnswerCardInfo(
            id=1,
            english_word="apple",
            korean_meaning="사과",
        )

        wa = WrongAnswerRead(
            id=1,
            card=card_info,
            user_answer="wrong",
            correct_answer="사과",
            quiz_type="word_to_meaning",
            created_at=datetime.utcnow(),
            reviewed=False,
        )
        assert wa.user_answer == "wrong"
        assert wa.quiz_type == "word_to_meaning"
        assert wa.card.english_word == "apple"
