"""
Deck service for calculating deck progress statistics.
"""

from uuid import UUID

from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.constants.categories import get_all_category_ids, get_category_metadata
from app.models import (
    CategoryDetail,
    CategorySelectionState,
    CategoryWithStats,
    Deck,
    DeckInCategory,
    DecksListResponse,
    DeckWithProgressRead,
    DisplayItem,
    GetSelectedDecksResponse,
    SelectedDeckInfo,
    SelectedDecksSummary,
    UserCardProgress,
    UserSelectedDeck,
    VocabularyCard,
)
from app.models.enums import CardState


class DeckService:
    """Service for deck-related operations."""

    @staticmethod
    async def get_decks_list(
        session: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 10,
    ) -> DecksListResponse:
        """
        Get list of all accessible decks with progress information.

        Returns public decks and user's own decks with learning progress statistics.
        """
        # Query for accessible decks (public or created by user)
        decks_query = (
            select(Deck)
            .where((Deck.is_public == True) | (Deck.creator_id == user_id))  # noqa: E712
            .offset(skip)
            .limit(limit)
        )
        result = await session.exec(decks_query)
        decks = list(result.all())

        # Count total accessible decks
        count_query = select(func.count(Deck.id)).where(
            (Deck.is_public == True) | (Deck.creator_id == user_id)  # noqa: E712
        )
        result = await session.exec(count_query)
        total_count = result.one()

        # Calculate progress for each deck
        decks_with_progress = []
        for deck in decks:
            progress = await DeckService.calculate_deck_progress(session, user_id, deck.id)
            deck_dict = {
                "id": deck.id,
                "name": deck.name,
                "description": deck.description,
                **progress,
            }
            decks_with_progress.append(DeckWithProgressRead(**deck_dict))

        return DecksListResponse(
            decks=decks_with_progress,
            total=total_count,
            skip=skip,
            limit=limit,
        )

    @staticmethod
    async def get_deck_by_id(
        session: AsyncSession,
        deck_id: int,
    ) -> Deck | None:
        """Get a deck by its ID."""
        deck_query = select(Deck).where(Deck.id == deck_id)
        result = await session.exec(deck_query)
        return result.one_or_none()

    @staticmethod
    async def check_deck_access(
        deck: Deck,
        user_id: UUID,
    ) -> bool:
        """Check if user has access to a deck (public or own deck)."""
        return deck.is_public or deck.creator_id == user_id

    @staticmethod
    async def calculate_deck_progress(
        session: AsyncSession,
        user_id: UUID,
        deck_id: int,
    ) -> dict:
        """
        Calculate deck learning progress for a user.

        Returns:
            {
                "total_cards": int,
                "learned_cards": int,  # REVIEW state
                "learning_cards": int,  # LEARNING/RELEARNING
                "new_cards": int,  # Not in UserCardProgress
                "progress_percent": float
            }
        """
        # Count total cards in deck
        total_cards_query = select(func.count(VocabularyCard.id)).where(
            VocabularyCard.deck_id == deck_id
        )
        result = await session.exec(total_cards_query)
        total_cards = result.one()

        # Handle empty deck
        if total_cards == 0:
            return {
                "total_cards": 0,
                "learned_cards": 0,
                "learning_cards": 0,
                "new_cards": 0,
                "progress_percent": 0.0,
            }

        # Count cards by state using JOIN
        # Count REVIEW (learned) cards
        learned_query = (
            select(func.count(UserCardProgress.id))
            .select_from(VocabularyCard)
            .join(
                UserCardProgress,
                (VocabularyCard.id == UserCardProgress.card_id)
                & (UserCardProgress.user_id == user_id),
            )
            .where(
                VocabularyCard.deck_id == deck_id,
                UserCardProgress.card_state == CardState.REVIEW,
            )
        )
        result = await session.exec(learned_query)
        learned_cards = result.one()

        # Count LEARNING + RELEARNING cards
        learning_query = (
            select(func.count(UserCardProgress.id))
            .select_from(VocabularyCard)
            .join(
                UserCardProgress,
                (VocabularyCard.id == UserCardProgress.card_id)
                & (UserCardProgress.user_id == user_id),
            )
            .where(
                VocabularyCard.deck_id == deck_id,
                UserCardProgress.card_state.in_([CardState.LEARNING, CardState.RELEARNING]),
            )
        )
        result = await session.exec(learning_query)
        learning_cards = result.one()

        # Count cards with progress (any state)
        cards_with_progress_query = (
            select(func.count(UserCardProgress.id))
            .select_from(VocabularyCard)
            .join(
                UserCardProgress,
                (VocabularyCard.id == UserCardProgress.card_id)
                & (UserCardProgress.user_id == user_id),
            )
            .where(VocabularyCard.deck_id == deck_id)
        )
        result = await session.exec(cards_with_progress_query)
        cards_with_progress = result.one()

        # Calculate new cards (cards without any progress)
        new_cards = total_cards - cards_with_progress

        # Calculate progress percentage (learned / total * 100)
        progress_percent = (learned_cards / total_cards * 100) if total_cards > 0 else 0.0

        return {
            "total_cards": total_cards,
            "learned_cards": learned_cards,
            "learning_cards": learning_cards,
            "new_cards": new_cards,
            "progress_percent": round(progress_percent, 1),
        }

    @staticmethod
    async def update_selected_decks(
        session: AsyncSession,
        user_id: UUID,
        select_all: bool,
        deck_ids: list[int] | None,
    ) -> tuple[bool, list[int], str | None]:
        """
        Update user's selected decks.

        Args:
            session: Database session
            user_id: User's profile ID
            select_all: Whether to select all decks
            deck_ids: List of deck IDs to select (when select_all is False)

        Returns:
            Tuple of (success, selected_deck_ids, error_message)
        """
        # Clear existing selections
        delete_stmt = delete(UserSelectedDeck).where(UserSelectedDeck.user_id == user_id)
        await session.exec(delete_stmt)

        selected_deck_ids: list[int] = []

        # If select_all=false, validate and add specific decks
        if not select_all:
            if not deck_ids:
                return False, [], "deck_ids must be provided when select_all is false"

            # Validate all deck IDs exist and are accessible
            for deck_id in deck_ids:
                deck_query = select(Deck).where(
                    Deck.id == deck_id,
                    (Deck.is_public == True) | (Deck.creator_id == user_id),  # noqa: E712
                )
                result = await session.exec(deck_query)
                deck = result.one_or_none()

                if not deck:
                    return False, [], f"Deck with id {deck_id} not found or not accessible"

            # Add selected decks to user_selected_decks table
            for deck_id in deck_ids:
                selected_deck = UserSelectedDeck(
                    user_id=user_id,
                    deck_id=deck_id,
                )
                session.add(selected_deck)

            selected_deck_ids = deck_ids

        await session.commit()
        return True, selected_deck_ids, None

    @staticmethod
    async def get_selected_decks(
        session: AsyncSession,
        user_id: UUID,
        select_all_decks: bool,
    ) -> GetSelectedDecksResponse:
        """
        Get user's selected decks with summary.

        Args:
            session: Database session
            user_id: User's profile ID
            select_all_decks: Profile's select_all_decks setting

        Returns:
            GetSelectedDecksResponse with deck details and summary
        """
        deck_ids: list[int] = []
        decks: list[SelectedDeckInfo] = []
        summary: SelectedDecksSummary | None = None

        if select_all_decks:
            return GetSelectedDecksResponse(
                select_all=True,
                deck_ids=[],
                decks=[],
                summary=None,
            )

        # Get selected deck IDs from user_selected_decks table
        selected_query = select(UserSelectedDeck).where(UserSelectedDeck.user_id == user_id)
        result = await session.exec(selected_query)
        selected_decks_records = list(result.all())
        deck_ids = [sd.deck_id for sd in selected_decks_records]
        selected_deck_ids_set = set(deck_ids)

        # Get deck details with progress for each selected deck
        total_selected_cards = 0
        deck_objects: list[Deck] = []

        for deck_id in deck_ids:
            deck_query = select(Deck).where(Deck.id == deck_id)
            result = await session.exec(deck_query)
            deck = result.one_or_none()

            if deck:
                deck_objects.append(deck)
                progress = await DeckService.calculate_deck_progress(session, user_id, deck_id)
                total_selected_cards += progress["total_cards"]

                deck_info = SelectedDeckInfo(
                    id=deck.id,
                    name=deck.name,
                    total_cards=progress["total_cards"],
                    progress_percent=progress["progress_percent"],
                )
                decks.append(deck_info)

        # Build category states
        category_states: list[CategorySelectionState] = []
        fully_selected_categories: list[dict] = []

        for category_id in get_all_category_ids():
            metadata = get_category_metadata(category_id)
            if not metadata:
                continue

            # Count total decks in this category
            total_query = select(func.count(Deck.id)).where(
                Deck.category == category_id,
                (Deck.is_public == True) | (Deck.creator_id == user_id),  # noqa: E712
            )
            result = await session.exec(total_query)
            total_decks = result.one() or 0

            if total_decks == 0:
                continue

            # Get deck IDs in this category
            decks_in_cat_query = select(Deck.id).where(
                Deck.category == category_id,
                (Deck.is_public == True) | (Deck.creator_id == user_id),  # noqa: E712
            )
            result = await session.exec(decks_in_cat_query)
            category_deck_ids = set(result.all())

            # Count selected decks in this category
            selected_in_category = category_deck_ids & selected_deck_ids_set
            selected_count = len(selected_in_category)

            # Calculate selection_state
            if selected_count == total_decks:
                selection_state = "all"
                fully_selected_categories.append(
                    {
                        "id": category_id,
                        "name": metadata["name"],
                        "count": total_decks,
                    }
                )
            elif selected_count > 0:
                selection_state = "partial"
            else:
                selection_state = "none"

            category_states.append(
                CategorySelectionState(
                    category_id=category_id,
                    category_name=metadata["name"],
                    total_decks=total_decks,
                    selected_decks=selected_count,
                    selection_state=selection_state,
                )
            )

        # Generate course name and display items
        course_name, display_items = DeckService._generate_course_name(
            deck_objects, fully_selected_categories
        )

        summary = SelectedDecksSummary(
            course_name=course_name,
            total_selected_decks=len(deck_ids),
            total_selected_cards=total_selected_cards,
            display_items=display_items,
            category_states=category_states,
        )

        return GetSelectedDecksResponse(
            select_all=False,
            deck_ids=deck_ids,
            decks=decks,
            summary=summary,
        )

    @staticmethod
    def _generate_course_name(
        selected_decks: list[Deck],
        fully_selected_categories: list[dict],
    ) -> tuple[str, list[DisplayItem]]:
        """
        Generate course name based on selected decks and categories.

        Rules:
        1. Only full category selections:
           - 1-3 categories: list names (e.g., "시험, 교과서")
           - 4+ categories: "First category 외 N개"
        2. Single deck selected: deck name
        3. Multiple decks: "First deck name 외 N개"
        """
        display_items: list[DisplayItem] = []

        # Partial decks (not belonging to fully selected categories)
        fully_selected_cat_ids = {cat["id"] for cat in fully_selected_categories}
        partial_decks = [
            deck for deck in selected_decks if deck.category not in fully_selected_cat_ids
        ]

        # Only full category selections
        if len(fully_selected_categories) > 0 and len(partial_decks) == 0:
            for cat in fully_selected_categories:
                display_items.append(
                    DisplayItem(
                        type="category",
                        name=cat["name"],
                        count=cat["count"],
                    )
                )

            if len(fully_selected_categories) <= 3:
                course_name = ", ".join([cat["name"] for cat in fully_selected_categories])
            else:
                first_cat = fully_selected_categories[0]["name"]
                course_name = f"{first_cat} 외 {len(fully_selected_categories) - 1}개"

        # Single deck selected
        elif len(selected_decks) == 1:
            deck = selected_decks[0]
            display_items.append(
                DisplayItem(
                    type="deck",
                    name=deck.name,
                    count=1,
                )
            )
            course_name = deck.name

        elif len(selected_decks) > 1:
            # Mixed: full categories + partial decks
            for cat in fully_selected_categories:
                display_items.append(
                    DisplayItem(
                        type="category",
                        name=cat["name"],
                        count=cat["count"],
                    )
                )

            for deck in partial_decks:
                display_items.append(
                    DisplayItem(
                        type="deck",
                        name=deck.name,
                        count=1,
                    )
                )

            first_deck = selected_decks[0]
            course_name = f"{first_deck.name} 외 {len(selected_decks) - 1}개"

        else:
            course_name = "선택된 단어장 없음"

        return course_name, display_items

    @staticmethod
    async def get_categories(
        session: AsyncSession,
        user_id: UUID,
    ) -> list[CategoryWithStats]:
        """
        Get all categories with statistics.

        Args:
            session: Database session
            user_id: User's profile ID

        Returns:
            List of CategoryWithStats
        """
        categories_list = []

        # Get user's selected deck IDs
        selected_decks_query = select(UserSelectedDeck.deck_id).where(
            UserSelectedDeck.user_id == user_id
        )
        result = await session.exec(selected_decks_query)
        selected_deck_ids = set(result.all())

        for category_id in get_all_category_ids():
            metadata = get_category_metadata(category_id)
            if not metadata:
                continue

            # Count total decks in this category
            total_query = select(func.count(Deck.id)).where(
                Deck.category == category_id,
                (Deck.is_public == True) | (Deck.creator_id == user_id),  # noqa: E712
            )
            result = await session.exec(total_query)
            total_decks = result.one() or 0

            # Get deck IDs in this category
            decks_query = select(Deck.id).where(
                Deck.category == category_id,
                (Deck.is_public == True) | (Deck.creator_id == user_id),  # noqa: E712
            )
            result = await session.exec(decks_query)
            category_deck_ids = set(result.all())

            # Count selected decks in this category
            selected_in_category = category_deck_ids & selected_deck_ids
            selected_decks = len(selected_in_category)

            # Calculate selection_state
            if total_decks == 0:
                selection_state = "none"
            elif selected_decks == total_decks:
                selection_state = "all"
            elif selected_decks > 0:
                selection_state = "partial"
            else:
                selection_state = "none"

            category_info = CategoryWithStats(
                id=category_id,
                name=metadata["name"],
                description=metadata["description"],
                icon=metadata["icon"],
                total_decks=total_decks,
                selected_decks=selected_decks,
                selection_state=selection_state,
            )
            categories_list.append(category_info)

        return categories_list

    @staticmethod
    async def get_category_decks(
        session: AsyncSession,
        user_id: UUID,
        category_id: str,
    ) -> tuple[CategoryDetail | None, list[DeckInCategory], int, int]:
        """
        Get decks for a specific category.

        Args:
            session: Database session
            user_id: User's profile ID
            category_id: Category identifier

        Returns:
            Tuple of (category_detail, decks_list, total_decks, selected_count)
            Returns (None, [], 0, 0) if category not found
        """
        metadata = get_category_metadata(category_id)
        if not metadata:
            return None, [], 0, 0

        # Get user's selected deck IDs
        selected_decks_query = select(UserSelectedDeck.deck_id).where(
            UserSelectedDeck.user_id == user_id
        )
        result = await session.exec(selected_decks_query)
        selected_deck_ids = set(result.all())

        # Get all decks in this category
        decks_query = select(Deck).where(
            Deck.category == category_id,
            (Deck.is_public == True) | (Deck.creator_id == user_id),  # noqa: E712
        )
        result = await session.exec(decks_query)
        decks = list(result.all())

        # Build deck list with is_selected
        decks_list = []
        selected_count = 0

        for deck in decks:
            is_selected = deck.id in selected_deck_ids
            if is_selected:
                selected_count += 1

            cards_query = select(func.count(VocabularyCard.id)).where(
                VocabularyCard.deck_id == deck.id
            )
            result = await session.exec(cards_query)
            total_cards = result.one() or 0

            deck_info = DeckInCategory(
                id=deck.id,
                name=deck.name,
                description=deck.description,
                total_cards=total_cards,
                is_selected=is_selected,
            )
            decks_list.append(deck_info)

        category_detail = CategoryDetail(
            id=category_id,
            name=metadata["name"],
            description=metadata["description"],
        )

        return category_detail, decks_list, len(decks), selected_count

    @staticmethod
    async def select_all_category_decks(
        session: AsyncSession,
        user_id: UUID,
        category_id: str,
    ) -> tuple[bool, int, int, str | None]:
        """
        Select all decks in a category.

        Args:
            session: Database session
            user_id: User's profile ID
            category_id: Category identifier

        Returns:
            Tuple of (success, total_decks, added_count, error_message)
        """
        metadata = get_category_metadata(category_id)
        if not metadata:
            return False, 0, 0, f"Category '{category_id}' not found"

        # Get all decks in this category
        decks_query = select(Deck.id).where(
            Deck.category == category_id,
            (Deck.is_public == True) | (Deck.creator_id == user_id),  # noqa: E712
        )
        result = await session.exec(decks_query)
        deck_ids = list(result.all())

        # Get already selected decks
        selected_query = select(UserSelectedDeck.deck_id).where(UserSelectedDeck.user_id == user_id)
        result = await session.exec(selected_query)
        already_selected = set(result.all())

        # Add new selections
        added_count = 0
        for deck_id in deck_ids:
            if deck_id not in already_selected:
                new_selection = UserSelectedDeck(
                    user_id=user_id,
                    deck_id=deck_id,
                )
                session.add(new_selection)
                added_count += 1

        await session.commit()

        return True, len(deck_ids), added_count, None

    @staticmethod
    async def deselect_all_category_decks(
        session: AsyncSession,
        user_id: UUID,
        category_id: str,
    ) -> tuple[bool, int, str | None]:
        """
        Deselect all decks in a category.

        Args:
            session: Database session
            user_id: User's profile ID
            category_id: Category identifier

        Returns:
            Tuple of (success, removed_count, error_message)
        """
        metadata = get_category_metadata(category_id)
        if not metadata:
            return False, 0, f"Category '{category_id}' not found"

        # Get all deck IDs in this category
        decks_query = select(Deck.id).where(
            Deck.category == category_id,
            (Deck.is_public == True) | (Deck.creator_id == user_id),  # noqa: E712
        )
        result = await session.exec(decks_query)
        deck_ids = list(result.all())

        # Delete selections for these decks
        delete_stmt = delete(UserSelectedDeck).where(
            UserSelectedDeck.user_id == user_id,
            UserSelectedDeck.deck_id.in_(deck_ids),
        )
        result = await session.exec(delete_stmt)
        await session.commit()

        removed_count = result.rowcount

        return True, removed_count, None
