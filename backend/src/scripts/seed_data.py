"""
Seed script to populate database with sample data.

This script adds:
- Official decks (NGSL, NAWL, BSL, AWL)
- Vocabulary cards from collected JSON data

Note: Users are managed by Supabase Auth and profiles are created on registration.

Run with: cd src && PYTHONPATH=. uv run python scripts/seed_data.py
"""

import asyncio
import csv
import json
import sys
from pathlib import Path

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import async_session_maker
from app.models.tables.deck import Deck
from app.models.tables.vocabulary_card import VocabularyCard

# Path to collected vocabulary data
DATA_DIR = Path(__file__).parent.parent / "data"
VOCABULARY_JSON = DATA_DIR / "vocabulary.json"

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


class FrequencyMapper:
    """Handles loading frequency data and mapping to vocabulary cards."""

    UNMATCHED_RANK = 999999
    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "frequency"

    def __init__(self):
        self.frequency_map: dict[str, int] = {}

    def load_coca_data(self) -> dict[str, int]:
        """Load COCA Top 5000 frequency data."""
        file_path = self.DATA_DIR / "COCA_5000.csv"
        frequency_map = {}

        with open(file_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row["lemma"].lower().strip()
                rank = int(row["rank"])
                frequency_map[word] = rank

        return frequency_map

    def load_google_ngram_data(self) -> dict[str, int]:
        """Load Google Ngram 246k frequency data."""
        file_path = self.DATA_DIR / "google_ngram_frequency_alpha.txt"
        frequency_map = {}

        with open(file_path, encoding="utf-8") as f:
            next(f)  # Skip header
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    rank_str = parts[0]
                    word = parts[1].lower().strip()
                    try:
                        rank = int(rank_str)
                        frequency_map[word] = rank
                    except ValueError:
                        continue

        return frequency_map

    def load_all_sources(self) -> dict[str, int]:
        """
        Load all sources and merge them with priority.
        Priority: COCA > Google Ngram
        """
        # Start with Google Ngram (lower priority)
        combined = self.load_google_ngram_data()

        # Override with COCA (highest priority)
        coca_map = self.load_coca_data()
        for word, rank in coca_map.items():
            combined[word] = rank

        return combined

    def load_frequency_data(self):
        """Load frequency data from all sources."""
        self.frequency_map = self.load_all_sources()

    def get_rank(self, english_word: str) -> int:
        """
        Get frequency rank for an English word.
        Returns UNMATCHED_RANK (999999) if not found.
        """
        if not english_word or not english_word.strip():
            return self.UNMATCHED_RANK

        import string

        word_lower = english_word.lower().strip()
        word_clean = word_lower.strip(string.punctuation)

        # Try exact match
        if word_clean in self.frequency_map:
            return self.frequency_map[word_clean]

        # Try first word for multi-word phrases
        words = word_clean.split()
        if len(words) > 1:
            first_word = words[0]
            if first_word in self.frequency_map:
                return self.frequency_map[first_word]

        return self.UNMATCHED_RANK


class CEFRMapper:
    """Handles loading CEFR level data and mapping to vocabulary cards."""

    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "frequency"

    def __init__(self):
        self.cefr_map: dict[str, str] = {}

    def load_oxford_data(self):
        """Load Oxford 3000 and 5000 CEFR data."""
        # Load Oxford 3000
        oxford_3000_path = self.DATA_DIR / "oxford-3000.csv"
        with open(oxford_3000_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row["word"].lower().strip()
                level = row["level"].upper()
                self.cefr_map[word] = level

        # Load Oxford 5000
        oxford_5000_path = self.DATA_DIR / "oxford-5000.csv"
        with open(oxford_5000_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row["word"].lower().strip()
                level = row["level"].upper()
                # Don't override if already set from Oxford 3000
                if word not in self.cefr_map:
                    self.cefr_map[word] = level

    def get_cefr_level_from_frequency(self, frequency_rank: int) -> str:
        """
        Assign CEFR level based on frequency rank.

        Fallback when word not in Oxford data:
        - A1: 1-500 (most common)
        - A2: 501-1500
        - B1: 1501-3000
        - B2: 3001-5000
        - C1: 5001-10000
        - C2: 10001+ (rare)
        """
        if frequency_rank <= 500:
            return "A1"
        elif frequency_rank <= 1500:
            return "A2"
        elif frequency_rank <= 3000:
            return "B1"
        elif frequency_rank <= 5000:
            return "B2"
        elif frequency_rank <= 10000:
            return "C1"
        else:
            return "C2"

    def get_level(self, english_word: str, frequency_rank: int) -> str:
        """
        Get CEFR level for an English word.
        Prioritizes Oxford data, falls back to frequency-based assignment.
        """
        if not english_word or not english_word.strip():
            return self.get_cefr_level_from_frequency(frequency_rank)

        import string

        word_lower = english_word.lower().strip()
        word_clean = word_lower.strip(string.punctuation)

        # Try exact match in Oxford data
        if word_clean in self.cefr_map:
            return self.cefr_map[word_clean]

        # Try first word for multi-word phrases
        words = word_clean.split()
        if len(words) > 1:
            first_word = words[0]
            if first_word in self.cefr_map:
                return self.cefr_map[first_word]

        # Fallback to frequency-based
        return self.get_cefr_level_from_frequency(frequency_rank)


async def seed_decks(session: AsyncSession) -> dict[str, int]:
    """Seed official decks and return tag -> deck_id mapping."""
    print("Seeding decks...")

    # Check if decks already exist
    statement = select(Deck).where(Deck.name == "Basic Core 1000")
    result = await session.exec(statement)
    if result.one_or_none():
        print("  ⚠️  Decks already exist, loading existing...")
        # Load existing deck IDs
        all_decks = await session.exec(select(Deck))
        deck_map = {}
        for deck in all_decks.all():
            # Map deck names to tags
            if "Basic" in deck.name:
                deck_map["ngsl_1000"] = deck.id
            elif "General" in deck.name:
                deck_map["ngsl"] = deck.id
            elif "NAWL" in deck.name:
                deck_map["nawl"] = deck.id
            elif "AWL" in deck.name and "NAWL" not in deck.name:
                deck_map["awl"] = deck.id
            elif "Business" in deck.name:
                deck_map["bsl"] = deck.id
            elif "Oxford" in deck.name:
                deck_map["oxford5000"] = deck.id
            elif "GRE" in deck.name:
                deck_map["gre"] = deck.id
        return deck_map

    # Official deck definitions
    decks_data = [
        {
            "tag": "ngsl_1000",
            "deck": Deck(
                name="Basic Core 1000",
                description="Top 1000 most common English words from NGSL for beginners",
                category="daily",
                difficulty_level="beginner",
                is_public=True,
                is_official=True,
            ),
        },
        {
            "tag": "ngsl",
            "deck": Deck(
                name="General English (NGSL)",
                description="New General Service List - 2800 most common English words covering ~92% of general text",
                category="daily",
                difficulty_level="beginner",
                is_public=True,
                is_official=True,
            ),
        },
        {
            "tag": "nawl",
            "deck": Deck(
                name="Academic (NAWL)",
                description="New Academic Word List - 963 essential academic vocabulary for TOEFL and academic writing",
                category="academic",
                difficulty_level="advanced",
                is_public=True,
                is_official=True,
            ),
        },
        {
            "tag": "awl",
            "deck": Deck(
                name="Academic (AWL)",
                description="Academic Spoken Word List - Academic vocabulary for IELTS and academic English",
                category="academic",
                difficulty_level="advanced",
                is_public=True,
                is_official=True,
            ),
        },
        {
            "tag": "bsl",
            "deck": Deck(
                name="Business English (BSL)",
                description="Business Service List - 1700 essential business and professional vocabulary",
                category="business",
                difficulty_level="intermediate",
                is_public=True,
                is_official=True,
            ),
        },
        {
            "tag": "oxford5000",
            "deck": Deck(
                name="Oxford 5000",
                description="Oxford Learner's Dictionary 5000 most important words for English learners",
                category="daily",
                difficulty_level="intermediate",
                is_public=True,
                is_official=True,
            ),
        },
        {
            "tag": "gre",
            "deck": Deck(
                name="GRE Advanced",
                description="Graduate Record Examination vocabulary - advanced academic and professional words",
                category="academic",
                difficulty_level="advanced",
                is_public=True,
                is_official=True,
            ),
        },
    ]

    deck_map = {}
    for item in decks_data:
        deck = item["deck"]
        session.add(deck)
        await session.flush()  # Get the ID
        deck_map[item["tag"]] = deck.id
        print(f"  ✅ Added deck: {deck.name} (id={deck.id})")

    await session.commit()
    print("✅ Decks seeded successfully\n")
    return deck_map


async def seed_vocabulary_from_json(session: AsyncSession, deck_map: dict[str, int]) -> None:
    """Seed vocabulary cards from collected JSON data."""
    print("Seeding vocabulary cards from JSON...")

    if not VOCABULARY_JSON.exists():
        print(f"  ⚠️  {VOCABULARY_JSON} not found. Run collect_data.py first.")
        print("  Seeding sample cards instead...")
        await seed_sample_vocabulary_cards(session)
        return

    # Check if cards already exist
    statement = select(func.count()).select_from(VocabularyCard)
    result = await session.exec(statement)
    count = result.one()
    if count > 10:  # More than sample cards
        print(f"  ⚠️  {count} vocabulary cards already exist, skipping...")
        return

    # Load JSON data
    with open(VOCABULARY_JSON, encoding="utf-8") as f:
        data = json.load(f)

    words = data.get("words", [])
    total = len(words)
    print(f"  Loading {total} words from JSON...")

    # Batch insert for better performance
    batch_size = 500
    added = 0

    for i in range(0, total, batch_size):
        batch = words[i : i + batch_size]

        # Priority order: most specific tags first
        tag_priority = ["ngsl_1000", "nawl", "awl", "bsl", "ngsl", "oxford5000", "gre"]

        for word_data in batch:
            # Map tags to primary deck_id (use highest priority matching deck)
            tags = word_data.get("tags", [])
            deck_id = None
            for priority_tag in tag_priority:
                if priority_tag in tags and priority_tag in deck_map:
                    deck_id = deck_map[priority_tag]
                    break

            card = VocabularyCard(
                english_word=word_data.get("english_word", ""),
                korean_meaning="",  # To be translated later
                part_of_speech=word_data.get("part_of_speech"),
                definition_en=word_data.get("definition_en"),
                difficulty_level=word_data.get("difficulty_level"),
                cefr_level=word_data.get("cefr_level"),
                frequency_rank=word_data.get("frequency_rank"),
                example_sentences=word_data.get("example_sentences"),
                tags=tags,
                deck_id=deck_id,
                is_verified=False,
            )
            session.add(card)
            added += 1

        await session.commit()
        print(f"  [PROGRESS] {min(i + batch_size, total)}/{total} cards added...")

    print(f"✅ {added} vocabulary cards seeded successfully\n")


async def seed_sample_vocabulary_cards(session: AsyncSession) -> None:
    """Seed sample vocabulary cards (fallback if JSON not available)."""
    print("Seeding sample vocabulary cards...")

    # Check if cards already exist
    statement = select(VocabularyCard).where(VocabularyCard.english_word == "contract")
    result = await session.exec(statement)
    if result.one_or_none():
        print("  ⚠️  Sample vocabulary cards already exist, skipping...")
        return

    cards = [
        VocabularyCard(
            english_word="contract",
            korean_meaning="계약",
            part_of_speech="noun",
            pronunciation_ipa="/ˈkɑːntrækt/",
            definition_en="a written or spoken agreement, especially one concerning employment, sales, or tenancy",
            example_sentences=[
                {
                    "en": "I signed a contract with the company.",
                    "ko": "나는 회사와 계약을 체결했다.",
                }
            ],
            difficulty_level="intermediate",
            cefr_level="B1",
            frequency_rank=1250,
            tags=["ngsl", "bsl"],
        ),
        VocabularyCard(
            english_word="algorithm",
            korean_meaning="알고리즘",
            part_of_speech="noun",
            pronunciation_ipa="/ˈælɡərɪðəm/",
            definition_en="a process or set of rules to be followed in calculations or problem-solving operations",
            example_sentences=[
                {
                    "en": "The algorithm improves over time.",
                    "ko": "알고리즘은 시간이 지남에 따라 개선된다.",
                }
            ],
            difficulty_level="advanced",
            cefr_level="C1",
            frequency_rank=2500,
            tags=["nawl"],
        ),
        VocabularyCard(
            english_word="challenge",
            korean_meaning="도전, 과제",
            part_of_speech="noun",
            pronunciation_ipa="/ˈtʃælɪndʒ/",
            definition_en="a task or situation that tests someone's abilities",
            example_sentences=[
                {
                    "en": "This project is a real challenge.",
                    "ko": "이 프로젝트는 진짜 도전이다.",
                }
            ],
            difficulty_level="beginner",
            cefr_level="A2",
            frequency_rank=800,
            tags=["ngsl", "ngsl_1000"],
        ),
    ]

    for card in cards:
        session.add(card)
        print(f"  ✅ Added card: {card.english_word} ({card.difficulty_level})")

    await session.commit()
    print("✅ Sample vocabulary cards seeded successfully\n")


async def main():
    """Main seeding function."""
    print("\n" + "=" * 50)
    print("DATABASE SEEDING SCRIPT")
    print("=" * 50 + "\n")

    async with async_session_maker() as session:
        try:
            # Seed decks and get ID mapping
            deck_map = await seed_decks(session)

            # Seed vocabulary from JSON (or sample cards if JSON not found)
            await seed_vocabulary_from_json(session, deck_map)

            print("=" * 50)
            print("✅ ALL DATA SEEDED SUCCESSFULLY!")
            print("=" * 50)
            print("\nSeeded:")
            print(f"  - {len(deck_map)} decks")
            print("  - Vocabulary cards from JSON")
            print("\nNote: Users/profiles are managed by Supabase Auth.")
            print("\n" + "=" * 50 + "\n")

        except Exception as e:
            print(f"\n❌ Error seeding data: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
