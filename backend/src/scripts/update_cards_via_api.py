"""
Update Vocabulary Cards via Supabase REST API

Updates existing vocabulary cards with:
- Frequency ranks (Issue #24)
- CEFR levels (Issue #26)

This script uses REST API instead of direct database connection.

Usage:
    uv run python src/scripts/update_cards_via_api.py [--dry-run]
"""

import csv
import os
import sys
from collections import defaultdict
from pathlib import Path

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be set in .env")
    sys.exit(1)

# API endpoints
API_BASE = f"{SUPABASE_URL}/rest/v1"
CARDS_URL = f"{API_BASE}/vocabulary_cards"

# Headers
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


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
        print("Loading Oxford CEFR data...")

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

        print(f"Loaded {len(self.cefr_map)} words with CEFR levels from Oxford")

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


def fetch_all_cards():
    """Fetch all vocabulary cards from Supabase using pagination."""
    print("\nFetching vocabulary cards from Supabase...")

    all_cards = []
    offset = 0
    limit = 1000

    while True:
        params = {
            "select": "id,english_word,frequency_rank,cefr_level",
            "offset": offset,
            "limit": limit,
        }

        response = requests.get(CARDS_URL, headers=HEADERS, params=params)

        if response.status_code != 200:
            print(f"Error fetching cards: {response.status_code}")
            print(response.text)
            sys.exit(1)

        cards = response.json()

        if not cards:
            break

        all_cards.extend(cards)
        offset += limit

        print(f"  Fetched {len(all_cards)} cards so far...")

        # Break if we got fewer cards than limit (last page)
        if len(cards) < limit:
            break

    print(f"Total cards fetched: {len(all_cards)}")
    return all_cards


def update_card(card_id: int, updates: dict, dry_run: bool = False):
    """Update a single card via REST API."""
    if dry_run:
        return True

    url = f"{CARDS_URL}?id=eq.{card_id}"
    response = requests.patch(url, headers=HEADERS, json=updates)

    return response.status_code in [200, 204]


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update vocabulary cards with frequency ranks and CEFR levels",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without updating database",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("VOCABULARY CARDS UPDATE SCRIPT (REST API)")
    print("=" * 70)

    if args.dry_run:
        print("\n[!] DRY RUN MODE - No database changes will be made\n")

    # Initialize mappers
    freq_mapper = FrequencyMapper()
    freq_mapper.load_frequency_data()

    cefr_mapper = CEFRMapper()
    cefr_mapper.load_oxford_data()

    # Fetch all cards
    cards = fetch_all_cards()

    if not cards:
        print("No vocabulary cards found in database")
        return

    # Statistics
    stats = {
        "total_cards": len(cards),
        "freq_matched": 0,
        "freq_unmatched": 0,
        "freq_updated": 0,
        "freq_already_set": 0,
        "cefr_from_oxford": 0,
        "cefr_from_frequency": 0,
        "cefr_updated": 0,
        "cefr_already_set": 0,
        "errors": 0,
    }

    # Track distributions
    freq_distribution = defaultdict(int)
    cefr_distribution = defaultdict(int)

    # Track unmatched words
    unmatched_words = []

    print("\nProcessing cards...")

    for i, card in enumerate(cards, 1):
        card_id = card["id"]
        english_word = card["english_word"]
        current_freq = card.get("frequency_rank")
        current_cefr = card.get("cefr_level")

        updates = {}

        # Map frequency rank
        new_freq = freq_mapper.get_rank(english_word)

        if new_freq == FrequencyMapper.UNMATCHED_RANK:
            stats["freq_unmatched"] += 1
            unmatched_words.append(english_word)
            freq_distribution["unmatched"] += 1
        else:
            stats["freq_matched"] += 1
            if new_freq <= 1000:
                freq_distribution["0-1000"] += 1
            elif new_freq <= 5000:
                freq_distribution["1000-5000"] += 1
            elif new_freq <= 10000:
                freq_distribution["5000-10000"] += 1
            elif new_freq <= 50000:
                freq_distribution["10000-50000"] += 1
            else:
                freq_distribution["50000+"] += 1

        if current_freq != new_freq:
            updates["frequency_rank"] = new_freq
            stats["freq_updated"] += 1
        else:
            stats["freq_already_set"] += 1

        # Map CEFR level
        import string

        word_clean = english_word.lower().strip().strip(string.punctuation)
        is_from_oxford = word_clean in cefr_mapper.cefr_map

        new_cefr = cefr_mapper.get_level(english_word, new_freq)

        if is_from_oxford:
            stats["cefr_from_oxford"] += 1
        else:
            stats["cefr_from_frequency"] += 1

        cefr_distribution[new_cefr] += 1

        if current_cefr != new_cefr:
            updates["cefr_level"] = new_cefr
            stats["cefr_updated"] += 1
        else:
            stats["cefr_already_set"] += 1

        # Update card if needed
        if updates:
            success = update_card(card_id, updates, dry_run=args.dry_run)
            if not success and not args.dry_run:
                stats["errors"] += 1
                print(f"  [X] Error updating card {card_id}: {english_word}")

        # Progress indicator
        if i % 100 == 0:
            print(f"  Processed {i}/{len(cards)} cards...")

    # Print results
    if not args.dry_run:
        print(
            f"\n[OK] Updated {stats['freq_updated'] + stats['cefr_updated']} fields in {len(cards)} cards"
        )
    else:
        print(f"\n[DRY RUN] Would update {stats['freq_updated'] + stats['cefr_updated']} fields")

    print("\n" + "=" * 70)
    print("FREQUENCY RANK STATISTICS")
    print("=" * 70)
    print(f"Total cards: {stats['total_cards']}")
    print(
        f"Matched: {stats['freq_matched']} ({stats['freq_matched'] / stats['total_cards'] * 100:.1f}%)"
    )
    print(
        f"Unmatched: {stats['freq_unmatched']} ({stats['freq_unmatched'] / stats['total_cards'] * 100:.1f}%)"
    )
    print(f"Updated: {stats['freq_updated']}")
    print(f"Already set: {stats['freq_already_set']}")

    print("\nRANK DISTRIBUTION")
    print("-" * 70)
    for range_name in ["0-1000", "1000-5000", "5000-10000", "10000-50000", "50000+", "unmatched"]:
        count = freq_distribution[range_name]
        percentage = count / stats["total_cards"] * 100 if stats["total_cards"] > 0 else 0
        print(f"{range_name:20s}: {count:5d} ({percentage:5.1f}%)")

    print("\n" + "=" * 70)
    print("CEFR LEVEL STATISTICS")
    print("=" * 70)
    print(
        f"From Oxford data: {stats['cefr_from_oxford']} ({stats['cefr_from_oxford'] / stats['total_cards'] * 100:.1f}%)"
    )
    print(
        f"From frequency: {stats['cefr_from_frequency']} ({stats['cefr_from_frequency'] / stats['total_cards'] * 100:.1f}%)"
    )
    print(f"Updated: {stats['cefr_updated']}")
    print(f"Already set: {stats['cefr_already_set']}")

    print("\nLEVEL DISTRIBUTION")
    print("-" * 70)
    for level in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        count = cefr_distribution[level]
        percentage = count / stats["total_cards"] * 100 if stats["total_cards"] > 0 else 0
        print(f"{level:20s}: {count:5d} ({percentage:5.1f}%)")

    print("=" * 70)

    # Save unmatched words report
    if unmatched_words and not args.dry_run:
        report_path = Path(__file__).parent / "unmatched_words_report.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("UNMATCHED WORDS REPORT\n")
            f.write("=" * 70 + "\n")
            f.write(f"Total unmatched: {len(unmatched_words)}\n\n")
            for word in sorted(set(unmatched_words)):
                f.write(f"{word}\n")

        print(f"\n[REPORT] Unmatched words report saved to: {report_path}")

    if stats["errors"] > 0:
        print(f"\n[!] {stats['errors']} errors occurred during update")

    if args.dry_run:
        print("\n[!] DRY RUN MODE - Run without --dry-run to apply changes")
    else:
        print("\n[OK] Update completed successfully")


if __name__ == "__main__":
    main()
