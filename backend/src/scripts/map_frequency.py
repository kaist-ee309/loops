"""
Frequency Rank Mapping Script

Maps English words from VocabularyCard to frequency ranks from various data sources.
Assigns rank=999999 for unmatched words (rare/unknown).

Usage:
    uv run python src/scripts/map_frequency.py [--dry-run] [--source SOURCE]

Sources:
    - coca: COCA Top 5000 (default)
    - google: Google Ngram 246k words
    - all: Use all sources (prioritizes COCA > Google)
"""

import asyncio
import csv
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class FrequencyMapper:
    """Handles loading frequency data and mapping to vocabulary cards."""

    UNMATCHED_RANK = 999999
    DATA_DIR = Path(__file__).parent.parent.parent / "data" / "frequency"

    def __init__(self):
        self.frequency_map: dict[str, int] = {}
        self.source_name = ""

    def load_coca_data(self) -> dict[str, int]:
        """Load COCA Top 5000 frequency data."""
        file_path = self.DATA_DIR / "COCA_5000.csv"
        frequency_map = {}

        print(f"Loading COCA data from {file_path}...")

        with open(file_path, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                word = row["lemma"].lower().strip()
                rank = int(row["rank"])
                frequency_map[word] = rank

        print(f"Loaded {len(frequency_map)} words from COCA")
        return frequency_map

    def load_google_ngram_data(self) -> dict[str, int]:
        """Load Google Ngram 246k frequency data."""
        file_path = self.DATA_DIR / "google_ngram_frequency_alpha.txt"
        frequency_map = {}

        print(f"Loading Google Ngram data from {file_path}...")

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

        print(f"Loaded {len(frequency_map)} words from Google Ngram")
        return frequency_map

    def load_all_sources(self) -> dict[str, int]:
        """
        Load all sources and merge them with priority.
        Priority: COCA > Google Ngram
        """
        print("Loading all frequency data sources...")

        # Start with Google Ngram (lower priority)
        combined = self.load_google_ngram_data()

        # Override with COCA (highest priority)
        coca_map = self.load_coca_data()
        for word, rank in coca_map.items():
            combined[word] = rank

        print(f"Total combined: {len(combined)} unique words")
        return combined

    def load_frequency_data(self, source: str = "coca") -> None:
        """Load frequency data from specified source."""
        if source == "coca":
            self.frequency_map = self.load_coca_data()
            self.source_name = "COCA Top 5000"
        elif source == "google":
            self.frequency_map = self.load_google_ngram_data()
            self.source_name = "Google Ngram 246k"
        elif source == "all":
            self.frequency_map = self.load_all_sources()
            self.source_name = "All Sources (COCA + Google)"
        else:
            raise ValueError(f"Unknown source: {source}")

    def get_rank(self, english_word: str) -> int:
        """
        Get frequency rank for an English word.
        Handles case-insensitive matching and multi-word phrases.
        Returns UNMATCHED_RANK (999999) if not found.
        """
        # Handle empty or whitespace-only strings
        if not english_word or not english_word.strip():
            return self.UNMATCHED_RANK

        # Clean the word: lowercase, strip whitespace and punctuation
        import string

        word_lower = english_word.lower().strip()
        word_clean = word_lower.strip(string.punctuation)

        # Try exact match with cleaned word
        if word_clean in self.frequency_map:
            return self.frequency_map[word_clean]

        # Try first word for multi-word phrases
        words = word_clean.split()
        if len(words) > 1:
            first_word = words[0]
            if first_word in self.frequency_map:
                return self.frequency_map[first_word]

        # Not found
        return self.UNMATCHED_RANK


async def map_frequency_ranks(session, mapper: FrequencyMapper, dry_run: bool = False) -> dict:
    """
    Map frequency ranks to all vocabulary cards.

    Args:
        session: Database session
        mapper: FrequencyMapper instance with loaded data
        dry_run: If True, preview changes without updating database

    Returns:
        Dictionary with mapping statistics
    """
    from sqlmodel import select

    from app.models.vocabulary_card import VocabularyCard

    print("\nFetching vocabulary cards from database...")
    result = await session.execute(select(VocabularyCard))
    cards = list(result.scalars().all())

    print(f"Found {len(cards)} vocabulary cards")

    if not cards:
        print("No vocabulary cards found in database")
        return {
            "total_cards": 0,
            "matched": 0,
            "unmatched": 0,
            "updated": 0,
        }

    # Statistics
    stats = {
        "total_cards": len(cards),
        "matched": 0,
        "unmatched": 0,
        "updated": 0,
        "already_set": 0,
    }

    # Track rank distribution
    rank_distribution = {
        "0-1000": 0,
        "1000-5000": 0,
        "5000-10000": 0,
        "10000-50000": 0,
        "50000+": 0,
        "unmatched": 0,
    }

    print("\nMapping frequency ranks...")
    for card in cards:
        new_rank = mapper.get_rank(card.english_word)

        # Update statistics
        if new_rank == FrequencyMapper.UNMATCHED_RANK:
            stats["unmatched"] += 1
            rank_distribution["unmatched"] += 1
        else:
            stats["matched"] += 1
            if new_rank <= 1000:
                rank_distribution["0-1000"] += 1
            elif new_rank <= 5000:
                rank_distribution["1000-5000"] += 1
            elif new_rank <= 10000:
                rank_distribution["5000-10000"] += 1
            elif new_rank <= 50000:
                rank_distribution["10000-50000"] += 1
            else:
                rank_distribution["50000+"] += 1

        # Update card if changed
        if card.frequency_rank != new_rank:
            if not dry_run:
                card.frequency_rank = new_rank
            stats["updated"] += 1
        else:
            stats["already_set"] += 1

    # Commit changes if not dry run
    if not dry_run:
        await session.commit()
        print(f"\n✓ Updated {stats['updated']} cards in database")
    else:
        print(f"\n[DRY RUN] Would update {stats['updated']} cards")

    # Print statistics
    print("\n" + "=" * 60)
    print("MAPPING STATISTICS")
    print("=" * 60)
    print(f"Source: {mapper.source_name}")
    print(f"Total cards: {stats['total_cards']}")
    print(f"Matched: {stats['matched']} ({stats['matched'] / stats['total_cards'] * 100:.1f}%)")
    print(
        f"Unmatched: {stats['unmatched']} ({stats['unmatched'] / stats['total_cards'] * 100:.1f}%)"
    )
    print(f"Updated: {stats['updated']}")
    print(f"Already set: {stats['already_set']}")

    print("\nRANK DISTRIBUTION")
    print("-" * 60)
    for range_name, count in rank_distribution.items():
        percentage = count / stats["total_cards"] * 100
        print(f"{range_name:20s}: {count:5d} ({percentage:5.1f}%)")

    print("=" * 60)

    return stats


async def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Map frequency ranks to vocabulary cards",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database",
    )
    parser.add_argument(
        "--source",
        choices=["coca", "google", "all"],
        default="all",
        help="Frequency data source (default: all)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("FREQUENCY RANK MAPPING SCRIPT")
    print("=" * 60)

    if args.dry_run:
        print("\n⚠ DRY RUN MODE - No database changes will be made\n")

    # Initialize mapper and load data
    mapper = FrequencyMapper()
    mapper.load_frequency_data(args.source)

    # Connect to database and run mapping
    from app.database import async_session_maker

    async with async_session_maker() as session:
        await map_frequency_ranks(session, mapper, dry_run=args.dry_run)

    if args.dry_run:
        print("\n⚠ DRY RUN MODE - Run without --dry-run to apply changes")
    else:
        print("\n✓ Frequency mapping completed successfully")


if __name__ == "__main__":
    asyncio.run(main())
