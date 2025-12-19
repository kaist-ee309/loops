"""
Pronunciation evaluation service (MVP Mock version).

This service provides mock pronunciation evaluation functionality.
In the future, it will be replaced with Azure/Google Speech API integration.
"""

import random

from app.models import VocabularyCard
from app.models.schemas.study import (
    PhonemeFeedback,
    PronunciationEvaluateResponse,
    PronunciationFeedback,
)


class PronunciationService:
    """Service for pronunciation evaluation operations."""

    @staticmethod
    def get_grade(score: int) -> str:
        """
        Get grade based on pronunciation score.

        Args:
            score: Pronunciation score (0-100)

        Returns:
            Grade string: excellent, good, fair, or needs_practice
        """
        if score >= 90:
            return "excellent"
        elif score >= 75:
            return "good"
        elif score >= 60:
            return "fair"
        else:
            return "needs_practice"

    @staticmethod
    def get_feedback_message(grade: str) -> str:
        """
        Get feedback message based on grade.

        Args:
            grade: Grade string (excellent, good, fair, needs_practice)

        Returns:
            Korean feedback message
        """
        messages = {
            "excellent": "완벽해요! 네이티브 수준의 발음입니다.",
            "good": "좋아요! 조금만 더 연습하면 완벽해질 거예요.",
            "fair": "괜찮아요! 강세와 발음에 조금 더 신경 써보세요.",
            "needs_practice": "다시 도전해보세요! 천천히 따라 해보세요.",
        }
        return messages.get(grade, "계속 연습해보세요!")

    @staticmethod
    def evaluate_pronunciation(
        card_id: int | None,
        word: str,
        pronunciation_ipa: str | None = None,
        native_audio_url: str | None = None,
    ) -> PronunciationEvaluateResponse:
        """
        Evaluate pronunciation (MVP Mock version).

        Generates mock score and feedback. In the future, this will integrate
        with Azure/Google Speech API for real pronunciation evaluation.

        Args:
            card_id: Optional card ID for the word
            word: The word being evaluated
            pronunciation_ipa: Optional IPA pronunciation
            native_audio_url: Optional native audio URL

        Returns:
            PronunciationEvaluateResponse with score, grade, and feedback
        """
        # Generate mock score
        score = random.randint(60, 95)
        grade = PronunciationService.get_grade(score)

        # Mock phoneme feedback
        phoneme_feedbacks = [
            PhonemeFeedback(phoneme="ə", score=random.randint(60, 90), tip="'어' 소리를 더 짧게"),
            PhonemeFeedback(
                phoneme="ʃ", score=random.randint(65, 95), tip="'sh' 소리를 더 부드럽게"
            ),
        ]

        feedback = PronunciationFeedback(
            overall=PronunciationService.get_feedback_message(grade),
            stress="강세 위치에 조금 더 신경 쓰면 좋겠어요." if score < 85 else None,
            sounds=phoneme_feedbacks if score < 80 else None,
        )

        return PronunciationEvaluateResponse(
            card_id=card_id,
            word=word,
            pronunciation_ipa=pronunciation_ipa,
            score=score,
            grade=grade,
            feedback=feedback,
            native_audio_url=native_audio_url,
            user_audio_url=None,
        )

    @staticmethod
    def evaluate_from_card(card: VocabularyCard) -> PronunciationEvaluateResponse:
        """
        Evaluate pronunciation using a vocabulary card.

        Args:
            card: VocabularyCard instance

        Returns:
            PronunciationEvaluateResponse with score, grade, and feedback
        """
        return PronunciationService.evaluate_pronunciation(
            card_id=card.id,
            word=card.english_word,
            pronunciation_ipa=card.pronunciation_ipa,
            native_audio_url=card.audio_url,
        )
