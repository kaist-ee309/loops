"""Factory for WrongAnswer model."""

from uuid import uuid4

import factory

from app.models import QuizType, WrongAnswer
from tests.factories.base import AsyncSQLModelFactory


class WrongAnswerFactory(AsyncSQLModelFactory):
    """Factory for creating WrongAnswer instances."""

    class Meta:
        model = WrongAnswer

    id = factory.Sequence(lambda n: n + 1)

    user_id = factory.LazyFunction(uuid4)
    card_id = factory.Sequence(lambda n: n + 1)
    session_id = factory.LazyFunction(uuid4)

    user_answer = factory.Faker("word")
    correct_answer = factory.Faker("word")
    quiz_type = QuizType.WORD_TO_MEANING.value

    # Review state
    reviewed = False
    reviewed_at = None

    class Params:
        """Factory parameters for common scenarios."""

        reviewed_answer = factory.Trait(
            reviewed=True,
            reviewed_at=factory.LazyFunction(lambda: __import__("datetime").datetime.utcnow()),
        )

        cloze = factory.Trait(
            quiz_type=QuizType.CLOZE.value,
            user_answer="wrong",
            correct_answer="correct",
        )

        meaning_to_word = factory.Trait(
            quiz_type=QuizType.MEANING_TO_WORD.value,
        )

        listening = factory.Trait(
            quiz_type=QuizType.LISTENING.value,
        )
