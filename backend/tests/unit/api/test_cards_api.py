"""Tests for Cards API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock

from app.models import CardSummary, RelatedWordInfo, RelatedWordsResponse, VocabularyCard


def make_card(
    id: int = 1, english_word: str = "test", korean_meaning: str = "테스트"
) -> VocabularyCard:
    """Create a VocabularyCard instance for testing."""
    return VocabularyCard(
        id=id,
        english_word=english_word,
        korean_meaning=korean_meaning,
        part_of_speech="noun",
        pronunciation_ipa="/test/",
        definition_en="a test word",
        example_sentences=[],
        difficulty_level="beginner",
        cefr_level="A1",
        deck_id=None,
        frequency_rank=1,
        image_url=None,
        related_words=[],
        cloze_sentences=[],
        tags=[],
        audio_url=None,
        created_at=datetime(2024, 1, 15),
        updated_at=None,
    )


class TestCreateCard:
    """Tests for POST /cards endpoint."""

    def test_create_card_success(self, api_client, mocker):
        """Test successful card creation."""
        mock_card = make_card()

        mocker.patch(
            "app.api.cards.VocabularyCardService.create_card",
            new_callable=AsyncMock,
            return_value=mock_card,
        )

        response = api_client.post(
            "/api/v1/cards",
            json={
                "english_word": "test",
                "korean_meaning": "테스트",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["english_word"] == "test"
        assert data["korean_meaning"] == "테스트"


class TestGetCards:
    """Tests for GET /cards endpoint."""

    def test_get_cards_success(self, api_client, mocker):
        """Test successful retrieval of cards list."""
        mock_cards = [
            make_card(id=i + 1, english_word=f"word{i}", korean_meaning=f"뜻{i}") for i in range(3)
        ]

        mocker.patch(
            "app.api.cards.VocabularyCardService.get_cards",
            new_callable=AsyncMock,
            return_value=mock_cards,
        )

        response = api_client.get("/api/v1/cards")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["english_word"] == "word0"

    def test_get_cards_with_pagination(self, api_client, mocker):
        """Test cards list with pagination parameters."""
        mocker.patch(
            "app.api.cards.VocabularyCardService.get_cards",
            new_callable=AsyncMock,
            return_value=[],
        )

        response = api_client.get("/api/v1/cards?skip=10&limit=20")

        assert response.status_code == 200

    def test_get_cards_with_filters(self, api_client, mocker):
        """Test cards list with filters."""
        mocker.patch(
            "app.api.cards.VocabularyCardService.get_cards",
            new_callable=AsyncMock,
            return_value=[],
        )

        response = api_client.get("/api/v1/cards?difficulty_level=A1&deck_id=1")

        assert response.status_code == 200


class TestGetCard:
    """Tests for GET /cards/{card_id} endpoint."""

    def test_get_card_success(self, api_client, mocker):
        """Test successful retrieval of single card."""
        mock_card = make_card()

        mocker.patch(
            "app.api.cards.VocabularyCardService.get_card",
            new_callable=AsyncMock,
            return_value=mock_card,
        )

        response = api_client.get("/api/v1/cards/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["english_word"] == "test"

    def test_get_card_not_found(self, api_client, mocker):
        """Test 404 when card not found."""
        mocker.patch(
            "app.api.cards.VocabularyCardService.get_card",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.get("/api/v1/cards/999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestUpdateCard:
    """Tests for PATCH /cards/{card_id} endpoint."""

    def test_update_card_success(self, api_client, mocker):
        """Test successful card update."""
        mock_card = make_card(english_word="updated", korean_meaning="업데이트됨")

        mocker.patch(
            "app.api.cards.VocabularyCardService.update_card",
            new_callable=AsyncMock,
            return_value=mock_card,
        )

        response = api_client.patch(
            "/api/v1/cards/1",
            json={"english_word": "updated"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["english_word"] == "updated"

    def test_update_card_not_found(self, api_client, mocker):
        """Test 404 when updating non-existent card."""
        mocker.patch(
            "app.api.cards.VocabularyCardService.update_card",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.patch(
            "/api/v1/cards/999",
            json={"english_word": "updated"},
        )

        assert response.status_code == 404


class TestDeleteCard:
    """Tests for DELETE /cards/{card_id} endpoint."""

    def test_delete_card_success(self, api_client, mocker):
        """Test successful card deletion."""
        mocker.patch(
            "app.api.cards.VocabularyCardService.delete_card",
            new_callable=AsyncMock,
            return_value=True,
        )

        response = api_client.delete("/api/v1/cards/1")

        assert response.status_code == 204

    def test_delete_card_not_found(self, api_client, mocker):
        """Test 404 when deleting non-existent card."""
        mocker.patch(
            "app.api.cards.VocabularyCardService.delete_card",
            new_callable=AsyncMock,
            return_value=False,
        )

        response = api_client.delete("/api/v1/cards/999")

        assert response.status_code == 404


class TestGetRelatedWords:
    """Tests for GET /cards/{card_id}/related endpoint."""

    def test_get_related_words_success(self, api_client, mocker):
        """Test successful retrieval of related words."""
        mock_card = make_card()

        mock_response = RelatedWordsResponse(
            card=CardSummary(id=1, english_word="test", korean_meaning="테스트"),
            related_words=[
                RelatedWordInfo(
                    card_id=2,
                    english_word="testing",
                    korean_meaning="테스팅",
                    relation_type="etymology",
                    relation_label="어원",
                    reason="Same root word",
                )
            ],
            total_related=1,
        )

        mocker.patch(
            "app.api.cards.VocabularyCardService.get_card",
            new_callable=AsyncMock,
            return_value=mock_card,
        )
        mocker.patch(
            "app.api.cards.VocabularyCardService.get_related_words",
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/cards/1/related")

        assert response.status_code == 200
        data = response.json()
        assert data["total_related"] == 1
        assert len(data["related_words"]) == 1

    def test_get_related_words_card_not_found(self, api_client, mocker):
        """Test 404 when card not found for related words."""
        mocker.patch(
            "app.api.cards.VocabularyCardService.get_card",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.get("/api/v1/cards/999/related")

        assert response.status_code == 404


class TestCardsAPIAuth:
    """Tests for authentication requirements on cards endpoints."""

    def test_create_card_requires_auth(self, unauthenticated_client):
        """Test that card creation requires authentication."""
        response = unauthenticated_client.post(
            "/api/v1/cards",
            json={"english_word": "test", "korean_meaning": "테스트"},
        )
        assert response.status_code == 403

    def test_get_cards_requires_auth(self, unauthenticated_client):
        """Test that cards list requires authentication."""
        response = unauthenticated_client.get("/api/v1/cards")
        assert response.status_code == 403

    def test_get_card_requires_auth(self, unauthenticated_client):
        """Test that single card retrieval requires authentication."""
        response = unauthenticated_client.get("/api/v1/cards/1")
        assert response.status_code == 403

    def test_update_card_requires_auth(self, unauthenticated_client):
        """Test that card update requires authentication."""
        response = unauthenticated_client.patch(
            "/api/v1/cards/1",
            json={"english_word": "updated"},
        )
        assert response.status_code == 403

    def test_delete_card_requires_auth(self, unauthenticated_client):
        """Test that card deletion requires authentication."""
        response = unauthenticated_client.delete("/api/v1/cards/1")
        assert response.status_code == 403
