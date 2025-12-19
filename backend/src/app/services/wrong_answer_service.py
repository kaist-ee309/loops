"""Wrong answer service for managing wrong answer records."""

from datetime import UTC, datetime
from uuid import UUID

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import (
    VocabularyCard,
    WrongAnswer,
    WrongAnswerCardInfo,
    WrongAnswerRead,
    WrongAnswerReviewedResponse,
    WrongAnswersResponse,
)


class WrongAnswerService:
    """Service for wrong answer operations."""

    @staticmethod
    async def create_wrong_answer(
        session: AsyncSession,
        user_id: UUID,
        card_id: int,
        session_id: UUID | None,
        user_answer: str,
        correct_answer: str,
        quiz_type: str,
    ) -> WrongAnswer:
        """Create a wrong answer record."""
        wrong_answer = WrongAnswer(
            user_id=user_id,
            card_id=card_id,
            session_id=session_id,
            user_answer=user_answer,
            correct_answer=correct_answer,
            quiz_type=quiz_type,
        )
        session.add(wrong_answer)
        await session.commit()
        await session.refresh(wrong_answer)
        return wrong_answer

    @staticmethod
    async def get_wrong_answers(
        session: AsyncSession,
        user_id: UUID,
        limit: int = 20,
        offset: int = 0,
        reviewed: bool | None = None,
        quiz_type: str | None = None,
    ) -> WrongAnswersResponse:
        """Get wrong answer list for a user."""
        # Base query
        query = (
            select(WrongAnswer, VocabularyCard)
            .join(VocabularyCard, VocabularyCard.id == WrongAnswer.card_id)
            .where(WrongAnswer.user_id == user_id)
        )

        # Apply filters
        if reviewed is not None:
            query = query.where(WrongAnswer.reviewed == reviewed)
        if quiz_type is not None:
            query = query.where(WrongAnswer.quiz_type == quiz_type)

        # Get total count
        count_query = select(func.count(WrongAnswer.id)).where(WrongAnswer.user_id == user_id)
        if reviewed is not None:
            count_query = count_query.where(WrongAnswer.reviewed == reviewed)
        if quiz_type is not None:
            count_query = count_query.where(WrongAnswer.quiz_type == quiz_type)

        total_result = await session.exec(count_query)
        total = total_result.one()

        # Get unreviewed count
        unreviewed_query = select(func.count(WrongAnswer.id)).where(
            WrongAnswer.user_id == user_id,
            WrongAnswer.reviewed == False,  # noqa: E712
        )
        unreviewed_result = await session.exec(unreviewed_query)
        unreviewed_count = unreviewed_result.one()

        # Get paginated results
        query = query.order_by(WrongAnswer.created_at.desc()).offset(offset).limit(limit)
        result = await session.exec(query)
        rows = list(result.all())

        # Build response
        wrong_answers = []
        for wrong_answer, card in rows:
            wrong_answers.append(
                WrongAnswerRead(
                    id=wrong_answer.id,
                    card=WrongAnswerCardInfo(
                        id=card.id,
                        english_word=card.english_word,
                        korean_meaning=card.korean_meaning,
                    ),
                    user_answer=wrong_answer.user_answer,
                    correct_answer=wrong_answer.correct_answer,
                    quiz_type=wrong_answer.quiz_type,
                    created_at=wrong_answer.created_at,
                    reviewed=wrong_answer.reviewed,
                    reviewed_at=wrong_answer.reviewed_at,
                )
            )

        return WrongAnswersResponse(
            wrong_answers=wrong_answers,
            total=total,
            unreviewed_count=unreviewed_count,
        )

    @staticmethod
    async def mark_reviewed(
        session: AsyncSession,
        user_id: UUID,
        wrong_answer_id: int,
    ) -> WrongAnswerReviewedResponse | None:
        """Mark a wrong answer as reviewed."""
        # Get wrong answer
        query = select(WrongAnswer).where(
            WrongAnswer.id == wrong_answer_id,
            WrongAnswer.user_id == user_id,
        )
        result = await session.exec(query)
        wrong_answer = result.one_or_none()

        if not wrong_answer:
            return None

        # Update reviewed status (use naive datetime to match DB schema)
        now = datetime.now(UTC).replace(tzinfo=None)
        wrong_answer.reviewed = True
        wrong_answer.reviewed_at = now
        session.add(wrong_answer)
        await session.commit()

        return WrongAnswerReviewedResponse(
            id=wrong_answer.id,
            reviewed=wrong_answer.reviewed,
            reviewed_at=wrong_answer.reviewed_at,
        )

    @staticmethod
    async def get_unreviewed_card_ids(
        session: AsyncSession,
        user_id: UUID,
        limit: int = 10,
    ) -> list[int]:
        """Get unique card IDs from unreviewed wrong answers."""
        # Use subquery to get most recent wrong answer per card, then select distinct card_ids
        subquery = (
            select(
                WrongAnswer.card_id,
                func.max(WrongAnswer.created_at).label("latest_created"),
            )
            .where(
                WrongAnswer.user_id == user_id,
                WrongAnswer.reviewed == False,  # noqa: E712
            )
            .group_by(WrongAnswer.card_id)
            .order_by(func.max(WrongAnswer.created_at).desc())
            .limit(limit)
        )
        result = await session.exec(subquery)
        rows = list(result.all())
        return [row[0] for row in rows]
