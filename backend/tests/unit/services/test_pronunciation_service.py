"""Tests for PronunciationService."""

from app.models import VocabularyCard
from app.services.pronunciation_service import PronunciationService


class TestPronunciationServiceGetGrade:
    """Tests for get_grade method."""

    def test_get_grade_excellent(self):
        """Test excellent grade for high scores."""
        assert PronunciationService.get_grade(90) == "excellent"
        assert PronunciationService.get_grade(95) == "excellent"
        assert PronunciationService.get_grade(100) == "excellent"

    def test_get_grade_good(self):
        """Test good grade for medium-high scores."""
        assert PronunciationService.get_grade(75) == "good"
        assert PronunciationService.get_grade(80) == "good"
        assert PronunciationService.get_grade(89) == "good"

    def test_get_grade_fair(self):
        """Test fair grade for medium scores."""
        assert PronunciationService.get_grade(60) == "fair"
        assert PronunciationService.get_grade(65) == "fair"
        assert PronunciationService.get_grade(74) == "fair"

    def test_get_grade_needs_practice(self):
        """Test needs_practice grade for low scores."""
        assert PronunciationService.get_grade(0) == "needs_practice"
        assert PronunciationService.get_grade(30) == "needs_practice"
        assert PronunciationService.get_grade(59) == "needs_practice"


class TestPronunciationServiceGetFeedbackMessage:
    """Tests for get_feedback_message method."""

    def test_get_feedback_message_excellent(self):
        """Test feedback message for excellent grade."""
        message = PronunciationService.get_feedback_message("excellent")
        assert "완벽" in message or "네이티브" in message

    def test_get_feedback_message_good(self):
        """Test feedback message for good grade."""
        message = PronunciationService.get_feedback_message("good")
        assert "좋아요" in message

    def test_get_feedback_message_fair(self):
        """Test feedback message for fair grade."""
        message = PronunciationService.get_feedback_message("fair")
        assert "괜찮아요" in message

    def test_get_feedback_message_needs_practice(self):
        """Test feedback message for needs_practice grade."""
        message = PronunciationService.get_feedback_message("needs_practice")
        assert "도전" in message or "다시" in message

    def test_get_feedback_message_unknown_grade(self):
        """Test default feedback message for unknown grade."""
        message = PronunciationService.get_feedback_message("unknown")
        assert "연습" in message


class TestPronunciationServiceEvaluatePronunciation:
    """Tests for evaluate_pronunciation method."""

    def test_evaluate_pronunciation_basic(self):
        """Test basic pronunciation evaluation."""
        result = PronunciationService.evaluate_pronunciation(
            card_id=None,
            word="hello",
        )

        assert result.word == "hello"
        assert result.card_id is None
        assert 60 <= result.score <= 95  # Mock score range
        assert result.grade in ["excellent", "good", "fair", "needs_practice"]
        assert result.feedback is not None
        assert result.feedback.overall is not None

    def test_evaluate_pronunciation_with_card_id(self):
        """Test pronunciation evaluation with card_id."""
        result = PronunciationService.evaluate_pronunciation(
            card_id=123,
            word="world",
            pronunciation_ipa="/wɜːld/",
            native_audio_url="https://example.com/audio.mp3",
        )

        assert result.card_id == 123
        assert result.word == "world"
        assert result.pronunciation_ipa == "/wɜːld/"
        assert result.native_audio_url == "https://example.com/audio.mp3"
        assert result.user_audio_url is None

    def test_evaluate_pronunciation_has_feedback_structure(self):
        """Test that feedback has expected structure."""
        result = PronunciationService.evaluate_pronunciation(
            card_id=None,
            word="test",
        )

        assert hasattr(result.feedback, "overall")
        assert result.feedback.overall is not None
        # stress and sounds may or may not be present depending on score


class TestPronunciationServiceEvaluateFromCard:
    """Tests for evaluate_from_card method."""

    def test_evaluate_from_card(self):
        """Test pronunciation evaluation from a vocabulary card."""
        # Create a mock card-like object
        card = VocabularyCard(
            id=1,
            english_word="vocabulary",
            korean_meaning="어휘",
            pronunciation_ipa="/vəˈkæbjʊləri/",
            audio_url="https://example.com/vocabulary.mp3",
        )

        result = PronunciationService.evaluate_from_card(card)

        assert result.card_id == 1
        assert result.word == "vocabulary"
        assert result.pronunciation_ipa == "/vəˈkæbjʊləri/"
        assert result.native_audio_url == "https://example.com/vocabulary.mp3"
        assert 60 <= result.score <= 95
        assert result.grade in ["excellent", "good", "fair", "needs_practice"]

    def test_evaluate_from_card_without_audio(self):
        """Test pronunciation evaluation from card without audio URL."""
        card = VocabularyCard(
            id=2,
            english_word="simple",
            korean_meaning="간단한",
            pronunciation_ipa=None,
            audio_url=None,
        )

        result = PronunciationService.evaluate_from_card(card)

        assert result.card_id == 2
        assert result.word == "simple"
        assert result.pronunciation_ipa is None
        assert result.native_audio_url is None
