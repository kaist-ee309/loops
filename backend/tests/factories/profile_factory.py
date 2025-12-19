"""Factory for Profile model."""

from datetime import date
from uuid import uuid4

import factory

from app.models import Profile
from tests.factories.base import AsyncSQLModelFactory


class ProfileFactory(AsyncSQLModelFactory):
    """Factory for creating Profile instances."""

    class Meta:
        model = Profile

    id = factory.LazyFunction(uuid4)

    # Learning preferences
    select_all_decks = True
    daily_goal = 20

    # Review ratio settings
    review_ratio_mode = "normal"
    custom_review_ratio = 0.75
    min_new_ratio = 0.25

    # Review scope
    review_scope = "selected_decks_only"

    # User settings
    timezone = "UTC"
    theme = "auto"
    notification_enabled = True

    # UI customization
    highlight_color = "#4CAF50"

    # Streak tracking
    current_streak = 0
    longest_streak = 0
    last_study_date = None

    # Study statistics
    total_study_time_minutes = 0

    class Params:
        """Factory parameters for common scenarios."""

        with_streak = factory.Trait(
            current_streak=5,
            longest_streak=10,
            last_study_date=factory.LazyFunction(lambda: date.today()),
        )

        custom_review_mode = factory.Trait(
            review_ratio_mode="custom",
            custom_review_ratio=0.8,
        )

        all_learned_scope = factory.Trait(
            review_scope="all_learned",
        )
