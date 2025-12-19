"""Factory for UserSelectedDeck model."""

from uuid import uuid4

import factory

from app.models import UserSelectedDeck
from tests.factories.base import AsyncSQLModelFactory


class UserSelectedDeckFactory(AsyncSQLModelFactory):
    """Factory for creating UserSelectedDeck instances."""

    class Meta:
        model = UserSelectedDeck

    id = factory.Sequence(lambda n: n + 1)
    user_id = factory.LazyFunction(uuid4)
    deck_id = factory.Sequence(lambda n: n + 1)
