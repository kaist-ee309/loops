"""Verify seeded data in Supabase."""

import asyncio

from sqlmodel import func, select

from app.database import async_session_maker
from app.models.tables.deck import Deck
from app.models.tables.vocabulary_card import VocabularyCard


async def verify():
    """Verify all seeded data."""
    async with async_session_maker() as session:
        # 1. Deck count and details
        print("=" * 60)
        print("DECKS")
        print("=" * 60)
        result = await session.exec(select(Deck).order_by(Deck.id))
        decks = result.all()
        for d in decks:
            print(f"  [{d.id}] {d.name} - {d.category}, {d.difficulty_level}")
        print(f"\nTotal decks: {len(decks)}")

        # 2. Total vocabulary cards
        print("\n" + "=" * 60)
        print("VOCABULARY CARDS")
        print("=" * 60)
        result = await session.exec(select(func.count(VocabularyCard.id)))
        total = result.one()
        print(f"Total cards: {total}")

        # 3. Cards per deck
        print("\nCards per deck:")
        for d in decks:
            result = await session.exec(
                select(func.count(VocabularyCard.id)).where(VocabularyCard.deck_id == d.id)
            )
            count = result.one()
            print(f"  [{d.id}] {d.name}: {count} cards")

        # 4. Cards with no deck (should be 0 or few)
        result = await session.exec(
            select(func.count(VocabularyCard.id)).where(VocabularyCard.deck_id == None)
        )
        no_deck = result.one()
        print(f"  [NULL] No deck assigned: {no_deck} cards")

        # 5. Sample cards from each deck
        print("\n" + "=" * 60)
        print("SAMPLE CARDS (3 per deck)")
        print("=" * 60)
        for d in decks:
            print(f"\n[{d.name}]")
            result = await session.exec(
                select(VocabularyCard).where(VocabularyCard.deck_id == d.id).limit(3)
            )
            cards = result.all()
            for c in cards:
                tags = c.tags if c.tags else []
                defn = c.definition_en[:50] + "..." if c.definition_en else "N/A"
                print(f"  - {c.english_word}: {defn} | tags: {tags}")

        # 6. Check multi-tagged words
        print("\n" + "=" * 60)
        print("MULTI-TAGGED WORDS (sample)")
        print("=" * 60)
        result = await session.exec(select(VocabularyCard).limit(1000))
        cards = result.all()
        multi_tagged = [c for c in cards if c.tags and len(c.tags) > 1]
        print(f"Found {len(multi_tagged)} multi-tagged words in first 1000 cards")
        for c in multi_tagged[:5]:
            print(f"  - {c.english_word}: tags={c.tags}")

        # 7. Check difficulty distribution
        print("\n" + "=" * 60)
        print("DIFFICULTY DISTRIBUTION")
        print("=" * 60)
        for level in range(1, 11):
            result = await session.exec(
                select(func.count(VocabularyCard.id)).where(
                    VocabularyCard.difficulty_level == level
                )
            )
            count = result.one()
            if count > 0:
                print(f"  Level {level}: {count} cards")

        # 8. Check CEFR distribution
        print("\n" + "=" * 60)
        print("CEFR LEVEL DISTRIBUTION")
        print("=" * 60)
        for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
            result = await session.exec(
                select(func.count(VocabularyCard.id)).where(VocabularyCard.cefr_level == level)
            )
            count = result.one()
            if count > 0:
                print(f"  {level}: {count} cards")


if __name__ == "__main__":
    asyncio.run(verify())
