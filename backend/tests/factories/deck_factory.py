"""Factory for Deck model."""

from uuid import uuid4

import factory

from app.models import Deck
from tests.factories.base import AsyncSQLModelFactory


class DeckFactory(AsyncSQLModelFactory):
    """Factory for creating Deck instances."""

    class Meta:
        model = Deck

    id = factory.Sequence(lambda n: n + 1)

    name = factory.Faker("sentence", nb_words=3)
    description = factory.Faker("paragraph")
    category = factory.Faker("random_element", elements=["business", "toeic", "academic", "daily"])
    difficulty_level = factory.Faker(
        "random_element", elements=["beginner", "intermediate", "advanced"]
    )

    is_public = True
    is_official = False
    creator_id = None

    class Params:
        """Factory parameters for common scenarios."""

        official = factory.Trait(
            is_official=True,
            is_public=True,
            creator_id=None,
        )

        private = factory.Trait(
            is_public=False,
            creator_id=factory.LazyFunction(uuid4),
        )

        user_created = factory.Trait(
            is_official=False,
            is_public=True,
            creator_id=factory.LazyFunction(uuid4),
        )
