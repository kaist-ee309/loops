"""Tests for Decks API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock

from app.models import Deck, DecksListResponse


def make_deck(id: int = 1, name: str = "Test Deck") -> Deck:
    """Create a Deck instance for testing."""
    return Deck(
        id=id,
        name=name,
        description="Test description",
        category="exam",
        difficulty_level="beginner",
        is_public=True,
        is_official=True,
        creator_id=None,
        created_at=datetime(2024, 1, 15),
        updated_at=None,
    )


class TestGetDecksList:
    """Tests for GET /decks endpoint."""

    def test_get_decks_list_success(self, api_client, mocker):
        """Test successful retrieval of decks list."""
        mock_response = DecksListResponse(
            decks=[
                {
                    "id": 1,
                    "name": "Deck 1",
                    "description": "First deck",
                    "total_cards": 100,
                    "learned_cards": 50,
                    "learning_cards": 20,
                    "new_cards": 30,
                    "progress_percent": 50.0,
                },
                {
                    "id": 2,
                    "name": "Deck 2",
                    "description": "Second deck",
                    "total_cards": 80,
                    "learned_cards": 0,
                    "learning_cards": 0,
                    "new_cards": 80,
                    "progress_percent": 0.0,
                },
            ],
            total=2,
            skip=0,
            limit=10,
        )

        mocker.patch(
            "app.api.decks.DeckService.get_decks_list",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/decks")

        assert response.status_code == 200
        data = response.json()
        assert len(data["decks"]) == 2
        assert data["total"] == 2

    def test_get_decks_list_with_pagination(self, api_client, mocker):
        """Test decks list with pagination parameters."""
        mock_response = DecksListResponse(
            decks=[],
            total=0,
            skip=10,
            limit=20,
        )

        mocker.patch(
            "app.api.decks.DeckService.get_decks_list",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/decks?skip=10&limit=20")

        assert response.status_code == 200

    def test_get_decks_list_requires_auth(self, unauthenticated_client):
        """Test that decks list requires authentication."""
        response = unauthenticated_client.get("/api/v1/decks")
        assert response.status_code == 403


class TestGetDeckDetail:
    """Tests for GET /decks/{deck_id} endpoint."""

    def test_get_deck_detail_success(self, api_client, mocker):
        """Test successful retrieval of deck detail."""
        mock_deck = make_deck()
        mock_progress = {
            "total_cards": 100,
            "learned_cards": 50,
            "learning_cards": 20,
            "new_cards": 30,
            "progress_percent": 50.0,
        }

        mocker.patch(
            "app.api.decks.DeckService.get_deck_by_id",
            new_callable=AsyncMock,
            return_value=mock_deck,
        )
        mocker.patch(
            "app.api.decks.DeckService.check_deck_access",
            new_callable=AsyncMock,
            return_value=True,
        )
        mocker.patch(
            "app.api.decks.DeckService.calculate_deck_progress",
            new_callable=AsyncMock,
            return_value=mock_progress,
        )

        response = api_client.get("/api/v1/decks/1")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Test Deck"
        assert data["total_cards"] == 100

    def test_get_deck_detail_not_found(self, api_client, mocker):
        """Test 404 when deck not found."""
        mocker.patch(
            "app.api.decks.DeckService.get_deck_by_id",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.get("/api/v1/decks/999")

        assert response.status_code == 404

    def test_get_deck_detail_access_denied(self, api_client, mocker):
        """Test 403 when access denied to private deck."""
        mock_deck = make_deck()
        mock_deck.is_public = False

        mocker.patch(
            "app.api.decks.DeckService.get_deck_by_id",
            new_callable=AsyncMock,
            return_value=mock_deck,
        )
        mocker.patch(
            "app.api.decks.DeckService.check_deck_access",
            new_callable=AsyncMock,
            return_value=False,
        )

        response = api_client.get("/api/v1/decks/1")

        assert response.status_code == 403

    def test_get_deck_detail_requires_auth(self, unauthenticated_client):
        """Test that deck detail requires authentication."""
        response = unauthenticated_client.get("/api/v1/decks/1")
        assert response.status_code == 403


class TestUpdateSelectedDecks:
    """Tests for PUT /decks/selected-decks endpoint."""

    def test_update_selected_decks_select_all(self, api_client, mocker):
        """Test selecting all decks."""
        mocker.patch(
            "app.api.decks.DeckService.update_selected_decks",
            new_callable=AsyncMock,
            return_value=(True, [], None),
        )

        response = api_client.put(
            "/api/v1/decks/selected-decks",
            json={"select_all": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["select_all"] is True

    def test_update_selected_decks_specific_decks(self, api_client, mocker):
        """Test selecting specific decks."""
        mocker.patch(
            "app.api.decks.DeckService.update_selected_decks",
            new_callable=AsyncMock,
            return_value=(True, [1, 2, 3], None),
        )

        response = api_client.put(
            "/api/v1/decks/selected-decks",
            json={"select_all": False, "deck_ids": [1, 2, 3]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["select_all"] is False
        assert data["selected_deck_ids"] == [1, 2, 3]

    def test_update_selected_decks_not_found(self, api_client, mocker):
        """Test 404 when deck not found."""
        mocker.patch(
            "app.api.decks.DeckService.update_selected_decks",
            new_callable=AsyncMock,
            return_value=(False, [], "Deck with id 999 not found"),
        )

        response = api_client.put(
            "/api/v1/decks/selected-decks",
            json={"select_all": False, "deck_ids": [999]},
        )

        assert response.status_code == 404

    def test_update_selected_decks_bad_request(self, api_client, mocker):
        """Test 400 when deck_ids is empty but select_all is false."""
        mocker.patch(
            "app.api.decks.DeckService.update_selected_decks",
            new_callable=AsyncMock,
            return_value=(False, [], "deck_ids is required when select_all is false"),
        )

        response = api_client.put(
            "/api/v1/decks/selected-decks",
            json={"select_all": False, "deck_ids": []},
        )

        assert response.status_code == 400

    def test_update_selected_decks_requires_auth(self, unauthenticated_client):
        """Test that update selected decks requires authentication."""
        response = unauthenticated_client.put(
            "/api/v1/decks/selected-decks",
            json={"select_all": True},
        )
        assert response.status_code == 403


class TestGetSelectedDecks:
    """Tests for GET /decks/selected-decks endpoint."""

    def test_get_selected_decks_success(self, api_client, mocker):
        """Test successful retrieval of selected decks."""
        from app.models.schemas.user_selected_deck import GetSelectedDecksResponse

        mock_response = GetSelectedDecksResponse(
            select_all=False,
            deck_ids=[1, 2],
            decks=[
                {"id": 1, "name": "Deck 1", "total_cards": 100, "progress_percent": 50.0},
                {"id": 2, "name": "Deck 2", "total_cards": 80, "progress_percent": 0.0},
            ],
            summary={
                "course_name": "Mixed Course",
                "total_selected_decks": 2,
                "total_selected_cards": 180,
                "display_items": [],
                "category_states": [],
            },
        )

        mocker.patch(
            "app.api.decks.DeckService.get_selected_decks",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/decks/selected-decks")

        assert response.status_code == 200
        data = response.json()
        assert data["select_all"] is False
        assert len(data["deck_ids"]) == 2

    def test_get_selected_decks_requires_auth(self, unauthenticated_client):
        """Test that get selected decks requires authentication."""
        response = unauthenticated_client.get("/api/v1/decks/selected-decks")
        assert response.status_code == 403


class TestGetCategories:
    """Tests for GET /decks/categories endpoint."""

    def test_get_categories_success(self, api_client, mocker):
        """Test successful retrieval of categories."""
        from app.models import CategoryWithStats

        mock_categories = [
            CategoryWithStats(
                id="exam",
                name="Exam",
                description="Exam related decks",
                icon="icon",
                total_decks=5,
                selected_decks=2,
                selection_state="partial",
            ),
            CategoryWithStats(
                id="textbook",
                name="Textbook",
                description="Textbook decks",
                icon="icon",
                total_decks=3,
                selected_decks=0,
                selection_state="none",
            ),
        ]

        mocker.patch(
            "app.api.decks.DeckService.get_categories",
            new_callable=AsyncMock,
            return_value=mock_categories,
        )

        response = api_client.get("/api/v1/decks/categories")

        assert response.status_code == 200
        data = response.json()
        assert len(data["categories"]) == 2
        assert data["categories"][0]["id"] == "exam"

    def test_get_categories_requires_auth(self, unauthenticated_client):
        """Test that get categories requires authentication."""
        response = unauthenticated_client.get("/api/v1/decks/categories")
        assert response.status_code == 403


class TestGetCategoryDecks:
    """Tests for GET /decks/categories/{category_id} endpoint."""

    def test_get_category_decks_success(self, api_client, mocker):
        """Test successful retrieval of category decks."""
        mock_category_detail = {
            "id": "exam",
            "name": "Exam",
            "description": "Exam decks",
        }
        mock_decks = [
            {
                "id": 1,
                "name": "Deck 1",
                "description": "First",
                "total_cards": 100,
                "is_selected": True,
            },
            {
                "id": 2,
                "name": "Deck 2",
                "description": "Second",
                "total_cards": 80,
                "is_selected": False,
            },
        ]

        mocker.patch(
            "app.api.decks.DeckService.get_category_decks",
            new_callable=AsyncMock,
            return_value=(mock_category_detail, mock_decks, 2, 1),
        )

        response = api_client.get("/api/v1/decks/categories/exam")

        assert response.status_code == 200
        data = response.json()
        assert data["category"]["id"] == "exam"
        assert len(data["decks"]) == 2
        assert data["total_decks"] == 2
        assert data["selected_decks"] == 1

    def test_get_category_decks_not_found(self, api_client, mocker):
        """Test 404 when category not found."""
        mocker.patch(
            "app.api.decks.DeckService.get_category_decks",
            new_callable=AsyncMock,
            return_value=(None, [], 0, 0),
        )

        response = api_client.get("/api/v1/decks/categories/invalid")

        assert response.status_code == 404

    def test_get_category_decks_requires_auth(self, unauthenticated_client):
        """Test that get category decks requires authentication."""
        response = unauthenticated_client.get("/api/v1/decks/categories/exam")
        assert response.status_code == 403


class TestSelectAllCategoryDecks:
    """Tests for PUT /decks/categories/{category_id}/select-all endpoint."""

    def test_select_all_category_decks_success(self, api_client, mocker):
        """Test successful selection of all category decks."""
        mocker.patch(
            "app.api.decks.DeckService.select_all_category_decks",
            new_callable=AsyncMock,
            return_value=(True, 5, 3, None),
        )

        response = api_client.put("/api/v1/decks/categories/exam/select-all")

        assert response.status_code == 200
        data = response.json()
        assert data["category_id"] == "exam"
        assert data["total_decks"] == 5
        assert data["added_decks"] == 3

    def test_select_all_category_decks_not_found(self, api_client, mocker):
        """Test 404 when category not found."""
        mocker.patch(
            "app.api.decks.DeckService.select_all_category_decks",
            new_callable=AsyncMock,
            return_value=(False, 0, 0, "Category not found"),
        )

        response = api_client.put("/api/v1/decks/categories/invalid/select-all")

        assert response.status_code == 404

    def test_select_all_category_decks_requires_auth(self, unauthenticated_client):
        """Test that select all category decks requires authentication."""
        response = unauthenticated_client.put("/api/v1/decks/categories/exam/select-all")
        assert response.status_code == 403


class TestDeselectAllCategoryDecks:
    """Tests for DELETE /decks/categories/{category_id}/select-all endpoint."""

    def test_deselect_all_category_decks_success(self, api_client, mocker):
        """Test successful deselection of all category decks."""
        mocker.patch(
            "app.api.decks.DeckService.deselect_all_category_decks",
            new_callable=AsyncMock,
            return_value=(True, 5, None),
        )

        response = api_client.delete("/api/v1/decks/categories/exam/select-all")

        assert response.status_code == 200
        data = response.json()
        assert data["category_id"] == "exam"
        assert data["removed_decks"] == 5

    def test_deselect_all_category_decks_not_found(self, api_client, mocker):
        """Test 404 when category not found."""
        mocker.patch(
            "app.api.decks.DeckService.deselect_all_category_decks",
            new_callable=AsyncMock,
            return_value=(False, 0, "Category not found"),
        )

        response = api_client.delete("/api/v1/decks/categories/invalid/select-all")

        assert response.status_code == 404

    def test_deselect_all_category_decks_requires_auth(self, unauthenticated_client):
        """Test that deselect all category decks requires authentication."""
        response = unauthenticated_client.delete("/api/v1/decks/categories/exam/select-all")
        assert response.status_code == 403
