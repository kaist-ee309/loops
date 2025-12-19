"""Factory for StudySession model."""

from datetime import datetime
from uuid import uuid4

import factory

from app.models import SessionStatus, StudySession
from tests.factories.base import AsyncSQLModelFactory


class StudySessionFactory(AsyncSQLModelFactory):
    """Factory for creating StudySession instances."""

    class Meta:
        model = StudySession

    id = factory.LazyFunction(uuid4)
    user_id = factory.LazyFunction(uuid4)

    # Session settings
    new_cards_limit = 10
    review_cards_limit = 20

    # Session state
    status = SessionStatus.ACTIVE

    # Card list
    card_ids = factory.LazyFunction(list)

    # Progress
    current_index = 0

    # Results
    correct_count = 0
    wrong_count = 0
    new_cards_count = 0
    review_cards_count = 0

    # Timestamps
    started_at = factory.LazyFunction(datetime.utcnow)
    completed_at = None

    class Params:
        """Factory parameters for common scenarios."""

        with_cards = factory.Trait(
            card_ids=[1, 2, 3, 4, 5],
            new_cards_limit=3,
            review_cards_limit=2,
        )

        in_progress = factory.Trait(
            status=SessionStatus.ACTIVE,
            card_ids=[1, 2, 3, 4, 5],
            current_index=2,
            correct_count=1,
            wrong_count=1,
            new_cards_count=1,
            review_cards_count=1,
        )

        completed = factory.Trait(
            status=SessionStatus.COMPLETED,
            card_ids=[1, 2, 3, 4, 5],
            current_index=5,
            correct_count=4,
            wrong_count=1,
            new_cards_count=3,
            review_cards_count=2,
            completed_at=factory.LazyFunction(datetime.utcnow),
        )

        abandoned = factory.Trait(
            status=SessionStatus.ABANDONED,
            card_ids=[1, 2, 3, 4, 5],
            current_index=2,
            correct_count=1,
            wrong_count=1,
            completed_at=factory.LazyFunction(datetime.utcnow),
        )
