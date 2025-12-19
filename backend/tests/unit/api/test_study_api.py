"""Tests for Study API endpoints."""

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

from app.models import (
    AnswerResponse,
    CardResponse,
    SessionAbandonResponse,
    SessionCompleteResponse,
    SessionPreviewResponse,
    SessionStartResponse,
    SessionStatusResponse,
    StudyOverviewResponse,
    UserCardProgressRead,
    WrongAnswerReviewedResponse,
    WrongAnswersResponse,
)
from app.models.enums import CardState
from app.models.schemas.study import (
    AvailableCards,
    CardAllocation,
    DailyGoalStatus,
    DueCardSummary,
    PronunciationEvaluateResponse,
    PronunciationFeedback,
    SessionAbandonSummary,
    SessionDailyGoalInfo,
    SessionSummary,
    StreakInfo,
    StudyCard,
    XPInfo,
)


class TestSessionPreview:
    """Tests for POST /study/session/preview endpoint."""

    def test_session_preview_success(self, api_client, mocker):
        """Test successful session preview."""
        mock_response = SessionPreviewResponse(
            available=AvailableCards(
                new_cards=20,
                review_cards=15,
                relearning_cards=5,
            ),
            allocation=CardAllocation(
                new_cards=8,
                review_cards=12,
                total=20,
            ),
            message=None,
        )

        mocker.patch(
            "app.api.study.StudySessionService.preview_session",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.post(
            "/api/v1/study/session/preview",
            json={"total_cards": 20, "review_ratio": 0.6},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["allocation"]["total"] == 20
        assert data["allocation"]["new_cards"] == 8
        assert data["allocation"]["review_cards"] == 12

    def test_session_preview_requires_auth(self, unauthenticated_client):
        """Test that session preview requires authentication."""
        response = unauthenticated_client.post(
            "/api/v1/study/session/preview",
            json={"total_cards": 20, "review_ratio": 0.6},
        )
        assert response.status_code == 403


class TestSessionStart:
    """Tests for POST /study/session/start endpoint."""

    def test_session_start_success(self, api_client, mocker):
        """Test successful session start."""
        session_id = uuid4()
        mock_response = SessionStartResponse(
            session_id=session_id,
            total_cards=30,
            new_cards_count=10,
            review_cards_count=20,
            started_at=datetime(2024, 1, 15, 10, 0, 0),
        )

        mocker.patch(
            "app.api.study.StudySessionService.start_session",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.post(
            "/api/v1/study/session/start",
            json={"new_cards_limit": 10, "review_cards_limit": 20},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == str(session_id)
        assert data["total_cards"] == 30

    def test_session_start_requires_auth(self, unauthenticated_client):
        """Test that session start requires authentication."""
        response = unauthenticated_client.post(
            "/api/v1/study/session/start",
            json={"new_cards_limit": 10, "review_cards_limit": 20},
        )
        assert response.status_code == 403


class TestSessionCard:
    """Tests for POST /study/session/card endpoint."""

    def test_get_next_card_success(self, api_client, mocker):
        """Test successful next card retrieval."""
        session_id = uuid4()
        mock_response = CardResponse(
            card=StudyCard(
                id=1,
                english_word="apple",
                korean_meaning="사과",
                part_of_speech="noun",
                pronunciation_ipa="/ˈæp.əl/",
                definition_en=None,
                example_sentences=None,
                audio_url=None,
                image_url=None,
                is_new=True,
                quiz_type="word_to_meaning",
                question="apple",
                options=["사과", "바나나", "오렌지", "포도"],
            ),
            cards_remaining=9,
            cards_completed=1,
        )

        mocker.patch(
            "app.api.study.StudySessionService.get_next_card",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.post(
            "/api/v1/study/session/card",
            json={"session_id": str(session_id), "quiz_type": "word_to_meaning"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["card"]["id"] == 1
        assert data["cards_remaining"] == 9

    def test_get_next_card_requires_auth(self, unauthenticated_client):
        """Test that get next card requires authentication."""
        session_id = uuid4()
        response = unauthenticated_client.post(
            "/api/v1/study/session/card",
            json={"session_id": str(session_id), "quiz_type": "word_to_meaning"},
        )
        assert response.status_code == 403


class TestSessionAnswer:
    """Tests for POST /study/session/answer endpoint."""

    def test_submit_answer_success(self, api_client, mocker):
        """Test successful answer submission."""
        session_id = uuid4()
        mock_response = AnswerResponse(
            card_id=1,
            is_correct=True,
            correct_answer="사과",
            user_answer="사과",
            feedback="정답입니다!",
            score=100,
            hint_penalty=0,
            next_review_date=datetime(2024, 1, 20),
            card_state="LEARNING",
        )

        mocker.patch(
            "app.api.study.StudySessionService.submit_answer",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.post(
            "/api/v1/study/session/answer",
            json={
                "session_id": str(session_id),
                "card_id": 1,
                "answer": "사과",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["is_correct"] is True
        assert data["score"] == 100

    def test_submit_answer_requires_auth(self, unauthenticated_client):
        """Test that submit answer requires authentication."""
        session_id = uuid4()
        response = unauthenticated_client.post(
            "/api/v1/study/session/answer",
            json={
                "session_id": str(session_id),
                "card_id": 1,
                "answer": "사과",
            },
        )
        assert response.status_code == 403


class TestSessionComplete:
    """Tests for POST /study/session/complete endpoint."""

    def test_complete_session_success(self, api_client, mocker):
        """Test successful session completion."""
        session_id = uuid4()
        mock_response = SessionCompleteResponse(
            session_summary=SessionSummary(
                total_cards=20,
                correct=18,
                wrong=2,
                accuracy=90.0,
                duration_seconds=600,
            ),
            streak=StreakInfo(
                current_streak=5,
                longest_streak=10,
                is_new_record=False,
                streak_status="continued",
                message="5일 연속 학습 중!",
            ),
            daily_goal=DailyGoalStatus(
                goal=20,
                completed=20,
                progress=100.0,
                is_completed=True,
            ),
            xp=XPInfo(
                base_xp=180,
                bonus_xp=50,
                total_xp=230,
            ),
        )

        mocker.patch(
            "app.api.study.StudySessionService.complete_session",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.post(
            "/api/v1/study/session/complete",
            json={"session_id": str(session_id)},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["session_summary"]["accuracy"] == 90.0
        assert data["xp"]["total_xp"] == 230

    def test_complete_session_requires_auth(self, unauthenticated_client):
        """Test that session complete requires authentication."""
        session_id = uuid4()
        response = unauthenticated_client.post(
            "/api/v1/study/session/complete",
            json={"session_id": str(session_id)},
        )
        assert response.status_code == 403


class TestSessionStatus:
    """Tests for GET /study/session/{session_id}/status endpoint."""

    def test_get_session_status_success(self, api_client, mocker):
        """Test successful session status retrieval."""
        session_id = uuid4()
        mock_response = SessionStatusResponse(
            session_id=session_id,
            status="active",
            total_cards=20,
            completed_cards=10,
            remaining_cards=10,
            correct_count=8,
            wrong_count=2,
            started_at=datetime(2024, 1, 15, 10, 0, 0),
            elapsed_seconds=300,
            daily_goal=SessionDailyGoalInfo(
                goal=20,
                completed_today=10,
                remaining_for_goal=10,
                will_complete_goal=True,
            ),
        )

        mocker.patch(
            "app.api.study.StudySessionService.get_session_status",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get(f"/api/v1/study/session/{session_id}/status")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["completed_cards"] == 10

    def test_get_session_status_requires_auth(self, unauthenticated_client):
        """Test that session status requires authentication."""
        session_id = uuid4()
        response = unauthenticated_client.get(f"/api/v1/study/session/{session_id}/status")
        assert response.status_code == 403


class TestSessionAbandon:
    """Tests for POST /study/session/{session_id}/abandon endpoint."""

    def test_abandon_session_success(self, api_client, mocker):
        """Test successful session abandonment."""
        session_id = uuid4()
        mock_response = SessionAbandonResponse(
            session_id=session_id,
            status="abandoned",
            summary=SessionAbandonSummary(
                total_cards=20,
                completed_cards=10,
                correct_count=8,
                wrong_count=2,
                duration_seconds=300,
            ),
            progress_saved=True,
            message="세션이 중단되었습니다. 진행 상황이 저장되었습니다.",
        )

        mocker.patch(
            "app.api.study.StudySessionService.abandon_session",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.post(
            f"/api/v1/study/session/{session_id}/abandon",
            json={"save_progress": True},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "abandoned"
        assert data["progress_saved"] is True

    def test_abandon_session_requires_auth(self, unauthenticated_client):
        """Test that session abandon requires authentication."""
        session_id = uuid4()
        response = unauthenticated_client.post(
            f"/api/v1/study/session/{session_id}/abandon",
            json={"save_progress": True},
        )
        assert response.status_code == 403


class TestStudyOverview:
    """Tests for GET /study/overview endpoint."""

    def test_get_overview_success(self, api_client, mocker):
        """Test successful study overview retrieval."""
        mock_response = StudyOverviewResponse(
            new_cards_count=15,
            review_cards_count=8,
            total_available=23,
            due_cards=[
                DueCardSummary(
                    card_id=1,
                    english_word="apple",
                    korean_meaning="사과",
                    next_review_date=datetime(2024, 1, 15),
                    card_state=CardState.REVIEW,
                ),
            ],
        )

        mocker.patch(
            "app.api.study.StudySessionService.get_overview",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/study/overview")

        assert response.status_code == 200
        data = response.json()
        assert data["new_cards_count"] == 15
        assert data["total_available"] == 23

    def test_get_overview_with_limit(self, api_client, mocker):
        """Test overview with custom limit."""
        mock_response = StudyOverviewResponse(
            new_cards_count=15,
            review_cards_count=8,
            total_available=23,
            due_cards=[],
        )

        mocker.patch(
            "app.api.study.StudySessionService.get_overview",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/study/overview?limit=10")

        assert response.status_code == 200

    def test_get_overview_requires_auth(self, unauthenticated_client):
        """Test that study overview requires authentication."""
        response = unauthenticated_client.get("/api/v1/study/overview")
        assert response.status_code == 403


class TestCardProgress:
    """Tests for GET /study/cards/{card_id} endpoint."""

    def test_get_card_progress_success(self, api_client, mocker, mock_profile):
        """Test successful card progress retrieval."""
        mock_progress = UserCardProgressRead(
            id=1,
            user_id=mock_profile.id,
            card_id=1,
            card_state=CardState.REVIEW,
            stability=5.0,
            difficulty=0.3,
            scheduled_days=3,
            interval=3,
            repetitions=10,
            total_reviews=10,
            correct_count=8,
            lapses=1,
            elapsed_days=3,
            last_review_date=datetime(2024, 1, 12),
            next_review_date=datetime(2024, 1, 15),
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 12),
        )

        mocker.patch(
            "app.api.study.UserCardProgressService.get_user_card_progress",
            new_callable=AsyncMock,
            return_value=mock_progress,
        )

        response = api_client.get("/api/v1/study/cards/1")

        assert response.status_code == 200
        data = response.json()
        assert data["card_state"] == "REVIEW"
        assert data["stability"] == 5.0

    def test_get_card_progress_not_found(self, api_client, mocker):
        """Test 404 when card progress not found."""
        mocker.patch(
            "app.api.study.UserCardProgressService.get_user_card_progress",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.get("/api/v1/study/cards/999")

        assert response.status_code == 404

    def test_get_card_progress_requires_auth(self, unauthenticated_client):
        """Test that card progress requires authentication."""
        response = unauthenticated_client.get("/api/v1/study/cards/1")
        assert response.status_code == 403


class TestWrongAnswers:
    """Tests for GET /study/wrong-answers endpoint."""

    def test_get_wrong_answers_success(self, api_client, mocker):
        """Test successful wrong answers retrieval."""
        # WrongAnswersResponse uses list of dicts directly
        mock_response = WrongAnswersResponse(
            wrong_answers=[],
            total=1,
            unreviewed_count=1,
        )

        mocker.patch(
            "app.api.study.WrongAnswerService.get_wrong_answers",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get("/api/v1/study/wrong-answers")

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["unreviewed_count"] == 1

    def test_get_wrong_answers_with_filters(self, api_client, mocker):
        """Test wrong answers with filters."""
        mock_response = WrongAnswersResponse(
            wrong_answers=[],
            total=0,
            unreviewed_count=0,
        )

        mocker.patch(
            "app.api.study.WrongAnswerService.get_wrong_answers",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.get(
            "/api/v1/study/wrong-answers?reviewed=false&quiz_type=word_to_meaning"
        )

        assert response.status_code == 200

    def test_get_wrong_answers_requires_auth(self, unauthenticated_client):
        """Test that wrong answers requires authentication."""
        response = unauthenticated_client.get("/api/v1/study/wrong-answers")
        assert response.status_code == 403


class TestMarkWrongAnswerReviewed:
    """Tests for PATCH /study/wrong-answers/{wrong_answer_id}/reviewed endpoint."""

    def test_mark_reviewed_success(self, api_client, mocker):
        """Test successful marking as reviewed."""
        mock_response = WrongAnswerReviewedResponse(
            id=1,
            reviewed=True,
            reviewed_at=datetime(2024, 1, 15, 10, 0, 0),
        )

        mocker.patch(
            "app.api.study.WrongAnswerService.mark_reviewed",
            new_callable=AsyncMock,
            return_value=mock_response,
        )

        response = api_client.patch("/api/v1/study/wrong-answers/1/reviewed")

        assert response.status_code == 200
        data = response.json()
        assert data["reviewed"] is True

    def test_mark_reviewed_not_found(self, api_client, mocker):
        """Test 404 when wrong answer not found."""
        mocker.patch(
            "app.api.study.WrongAnswerService.mark_reviewed",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.patch("/api/v1/study/wrong-answers/999/reviewed")

        assert response.status_code == 404

    def test_mark_reviewed_requires_auth(self, unauthenticated_client):
        """Test that mark reviewed requires authentication."""
        response = unauthenticated_client.patch("/api/v1/study/wrong-answers/1/reviewed")
        assert response.status_code == 403


class TestStartWrongReviewSession:
    """Tests for POST /study/session/start-wrong-review endpoint."""

    def test_start_wrong_review_success(self, api_client, mocker):
        """Test successful wrong review session start."""
        session_id = uuid4()
        mocker.patch(
            "app.api.study.WrongAnswerService.get_unreviewed_card_ids",
            new_callable=AsyncMock,
            return_value=[1, 2, 3],
        )

        mock_session_response = SessionStartResponse(
            session_id=session_id,
            total_cards=3,
            new_cards_count=0,
            review_cards_count=3,
            started_at=datetime(2024, 1, 15, 10, 0, 0),
        )

        mocker.patch(
            "app.api.study.StudySessionService.start_session_with_cards",
            new_callable=AsyncMock,
            return_value=mock_session_response,
        )

        response = api_client.post(
            "/api/v1/study/session/start-wrong-review",
            json={"limit": 10},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["cards_from_wrong_answers"] is True
        assert data["total_cards"] == 3

    def test_start_wrong_review_no_wrong_answers(self, api_client, mocker):
        """Test wrong review when no wrong answers available."""
        mocker.patch(
            "app.api.study.WrongAnswerService.get_unreviewed_card_ids",
            new_callable=AsyncMock,
            return_value=[],
        )

        response = api_client.post(
            "/api/v1/study/session/start-wrong-review",
            json={"limit": 10},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total_cards"] == 0

    def test_start_wrong_review_requires_auth(self, unauthenticated_client):
        """Test that wrong review session requires authentication."""
        response = unauthenticated_client.post(
            "/api/v1/study/session/start-wrong-review",
            json={"limit": 10},
        )
        assert response.status_code == 403


class TestPronunciationEvaluate:
    """Tests for POST /study/pronunciation/evaluate endpoint."""

    def test_evaluate_pronunciation_with_card_id(self, api_client, mocker):
        """Test pronunciation evaluation with card_id."""
        from app.models import VocabularyCard

        mock_card = VocabularyCard(
            id=1,
            english_word="apple",
            korean_meaning="사과",
            part_of_speech="noun",
            difficulty_level="beginner",
        )

        mock_response = PronunciationEvaluateResponse(
            card_id=1,
            word="apple",
            pronunciation_ipa="/ˈæp.əl/",
            score=85,
            grade="good",
            feedback=PronunciationFeedback(
                overall="좋아요!",
                stress=None,
                sounds=None,
            ),
            native_audio_url=None,
            user_audio_url=None,
        )

        mocker.patch(
            "app.api.study.VocabularyCardService.get_card",
            new_callable=AsyncMock,
            return_value=mock_card,
        )

        mocker.patch(
            "app.api.study.PronunciationService.evaluate_from_card",
            return_value=mock_response,
        )

        response = api_client.post(
            "/api/v1/study/pronunciation/evaluate",
            json={"card_id": 1},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 85
        assert data["grade"] == "good"

    def test_evaluate_pronunciation_with_word(self, api_client, mocker):
        """Test pronunciation evaluation with word only."""
        mock_response = PronunciationEvaluateResponse(
            card_id=None,
            word="hello",
            pronunciation_ipa="/həˈloʊ/",
            score=90,
            grade="excellent",
            feedback=PronunciationFeedback(
                overall="완벽해요!",
                stress=None,
                sounds=None,
            ),
            native_audio_url=None,
            user_audio_url=None,
        )

        mocker.patch(
            "app.api.study.PronunciationService.evaluate_pronunciation",
            return_value=mock_response,
        )

        response = api_client.post(
            "/api/v1/study/pronunciation/evaluate",
            json={"word": "hello"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 90

    def test_evaluate_pronunciation_card_not_found(self, api_client, mocker):
        """Test 404 when card not found."""
        mocker.patch(
            "app.api.study.VocabularyCardService.get_card",
            new_callable=AsyncMock,
            return_value=None,
        )

        response = api_client.post(
            "/api/v1/study/pronunciation/evaluate",
            json={"card_id": 999},
        )

        assert response.status_code == 404

    def test_evaluate_pronunciation_missing_params(self, api_client):
        """Test 422 when neither card_id nor word provided."""
        response = api_client.post(
            "/api/v1/study/pronunciation/evaluate",
            json={},
        )

        assert response.status_code == 422

    def test_evaluate_pronunciation_requires_auth(self, unauthenticated_client):
        """Test that pronunciation evaluation requires authentication."""
        response = unauthenticated_client.post(
            "/api/v1/study/pronunciation/evaluate",
            json={"word": "hello"},
        )
        assert response.status_code == 403
