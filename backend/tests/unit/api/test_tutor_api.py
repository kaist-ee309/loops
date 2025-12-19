"""Tests for tutor API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from app.models.enums import ChatRole


class TestStartWordTutor:
    """Tests for start_word_tutor endpoint."""

    def test_start_word_tutor_success(self, api_client, mocker):
        """Test starting word tutor successfully."""
        from app.models import TutorStartResponse

        mock_response = TutorStartResponse(
            thread_id=uuid4(),
            starter_questions=["What is the origin of this word?", "How is this word used?"],
            messages=None,
        )

        mocker.patch(
            "app.api.tutor.WordTutorService.start",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        session_id = uuid4()
        card_id = 1

        response = api_client.post(
            f"/api/v1/study/session/{session_id}/cards/{card_id}/tutor/start"
        )

        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert len(data["starter_questions"]) >= 1

    def test_start_word_tutor_with_messages(self, api_client, mocker):
        """Test starting word tutor with include_messages=True."""
        from app.models import TutorMessageRead, TutorStartResponse

        message = TutorMessageRead(
            id=uuid4(),
            role=ChatRole.ASSISTANT,
            content="Hello! How can I help you?",
            suggested_questions=["Question 1"],
            created_at=datetime.utcnow(),
        )

        mock_response = TutorStartResponse(
            thread_id=uuid4(),
            starter_questions=["Question 1"],
            messages=[message],
        )

        mocker.patch(
            "app.api.tutor.WordTutorService.start",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        session_id = uuid4()
        card_id = 1

        response = api_client.post(
            f"/api/v1/study/session/{session_id}/cards/{card_id}/tutor/start",
            params={"include_messages": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["messages"]) == 1


class TestSendWordTutorMessage:
    """Tests for send_word_tutor_message endpoint."""

    def test_send_message_success(self, api_client, mocker):
        """Test sending a message to word tutor."""
        from app.models import TutorMessageResponse

        mock_response = TutorMessageResponse(
            thread_id=uuid4(),
            assistant_message="Great question! The word 'apple' comes from...",
            follow_up_questions=["Tell me more", "What about the pronunciation?"],
        )

        mocker.patch(
            "app.api.tutor.WordTutorService.send_message",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        session_id = uuid4()
        card_id = 1

        response = api_client.post(
            f"/api/v1/study/session/{session_id}/cards/{card_id}/tutor/message",
            json={"message": "What is the origin of this word?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "assistant_message" in data
        assert "apple" in data["assistant_message"]
        assert len(data["follow_up_questions"]) >= 1


class TestGetWordTutorHistory:
    """Tests for get_word_tutor_history endpoint."""

    def test_get_history_success(self, api_client, mocker):
        """Test getting word tutor history."""
        from app.models import TutorHistoryResponse, TutorMessageRead

        messages = [
            TutorMessageRead(
                id=uuid4(),
                role=ChatRole.USER,
                content="What is the origin?",
                suggested_questions=None,
                created_at=datetime.utcnow(),
            ),
            TutorMessageRead(
                id=uuid4(),
                role=ChatRole.ASSISTANT,
                content="The word comes from...",
                suggested_questions=["More questions"],
                created_at=datetime.utcnow(),
            ),
        ]

        mock_response = TutorHistoryResponse(
            thread_id=uuid4(),
            messages=messages,
        )

        mocker.patch(
            "app.api.tutor.WordTutorService.history",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        session_id = uuid4()
        card_id = 1

        response = api_client.get(
            f"/api/v1/study/session/{session_id}/cards/{card_id}/tutor/history"
        )

        assert response.status_code == 200
        data = response.json()
        assert "thread_id" in data
        assert len(data["messages"]) == 2

    def test_get_history_with_limit(self, api_client, mocker):
        """Test getting word tutor history with limit."""
        from app.models import TutorHistoryResponse

        mock_response = TutorHistoryResponse(
            thread_id=uuid4(),
            messages=[],
        )

        mocker.patch(
            "app.api.tutor.WordTutorService.history",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        session_id = uuid4()
        card_id = 1

        response = api_client.get(
            f"/api/v1/study/session/{session_id}/cards/{card_id}/tutor/history",
            params={"limit": 10},
        )

        assert response.status_code == 200
