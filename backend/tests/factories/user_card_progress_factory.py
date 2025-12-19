"""Factory for UserCardProgress model."""

from datetime import datetime
from uuid import uuid4

import factory

from app.models import CardState, UserCardProgress
from tests.factories.base import AsyncSQLModelFactory


class UserCardProgressFactory(AsyncSQLModelFactory):
    """Factory for creating UserCardProgress instances."""

    class Meta:
        model = UserCardProgress

    id = factory.Sequence(lambda n: n + 1)

    user_id = factory.LazyFunction(uuid4)
    card_id = factory.Sequence(lambda n: n + 1)

    # FSRS Algorithm Parameters
    interval = 0
    repetitions = 0

    # Statistics
    total_reviews = 0
    correct_count = 0

    # FSRS Extended Parameters
    stability = 0.0
    difficulty = 5.0
    scheduled_days = 0
    lapses = 0
    elapsed_days = 0

    # Timestamps
    next_review_date = factory.LazyFunction(datetime.utcnow)
    last_review_date = None

    # State
    card_state = CardState.NEW

    # History
    quality_history = None

    class Params:
        """Factory parameters for common scenarios."""

        learning = factory.Trait(
            card_state=CardState.LEARNING,
            repetitions=1,
            total_reviews=1,
            stability=1.0,
            difficulty=5.0,
            last_review_date=factory.LazyFunction(datetime.utcnow),
        )

        review = factory.Trait(
            card_state=CardState.REVIEW,
            repetitions=3,
            total_reviews=5,
            correct_count=4,
            stability=10.0,
            difficulty=4.5,
            interval=7,
            scheduled_days=7,
            last_review_date=factory.LazyFunction(datetime.utcnow),
            quality_history=[3, 3, 4, 3, 3],
        )

        relearning = factory.Trait(
            card_state=CardState.RELEARNING,
            repetitions=5,
            total_reviews=8,
            correct_count=5,
            lapses=2,
            stability=2.0,
            difficulty=6.0,
            last_review_date=factory.LazyFunction(datetime.utcnow),
        )

        due_for_review = factory.Trait(
            card_state=CardState.REVIEW,
            repetitions=3,
            total_reviews=5,
            correct_count=4,
            stability=10.0,
            next_review_date=factory.LazyAttribute(
                lambda o: datetime(2024, 1, 1, 0, 0, 0)  # Past date
            ),
        )
