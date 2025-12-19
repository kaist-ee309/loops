"""Seed vocabulary cards via Supabase REST API."""

import json
import os
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(Path(__file__).parent.parent.parent / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SECRET_KEY")  # Need secret key for inserts

DATA_DIR = Path(__file__).parent.parent / "data"
VOCABULARY_JSON = DATA_DIR / "vocabulary.json"

# Priority order for deck assignment
TAG_PRIORITY = ["ngsl_1000", "nawl", "awl", "bsl", "ngsl", "oxford5000", "gre"]


DECK_DEFINITIONS = [
    {
        "tag": "ngsl_1000",
        "name": "Basic Core 1000",
        "description": "Top 1000 most common English words from NGSL for beginners",
        "category": "daily",
        "difficulty_level": "beginner",
        "is_public": True,
        "is_official": True,
    },
    {
        "tag": "ngsl",
        "name": "General English (NGSL)",
        "description": "New General Service List - 2800 most common English words covering ~92% of general text",
        "category": "daily",
        "difficulty_level": "beginner",
        "is_public": True,
        "is_official": True,
    },
    {
        "tag": "nawl",
        "name": "Academic (NAWL)",
        "description": "New Academic Word List - 963 essential academic vocabulary for TOEFL and academic writing",
        "category": "academic",
        "difficulty_level": "advanced",
        "is_public": True,
        "is_official": True,
    },
    {
        "tag": "awl",
        "name": "Academic (AWL)",
        "description": "Academic Spoken Word List - Academic vocabulary for IELTS and academic English",
        "category": "academic",
        "difficulty_level": "advanced",
        "is_public": True,
        "is_official": True,
    },
    {
        "tag": "bsl",
        "name": "Business English (BSL)",
        "description": "Business Service List - 1700 essential business and professional vocabulary",
        "category": "business",
        "difficulty_level": "intermediate",
        "is_public": True,
        "is_official": True,
    },
    {
        "tag": "oxford5000",
        "name": "Oxford 5000",
        "description": "Oxford Learner's Dictionary 5000 most important words for English learners",
        "category": "daily",
        "difficulty_level": "intermediate",
        "is_public": True,
        "is_official": True,
    },
    {
        "tag": "gre",
        "name": "GRE Advanced",
        "description": "Graduate Record Examination vocabulary - advanced academic and professional words",
        "category": "academic",
        "difficulty_level": "advanced",
        "is_public": True,
        "is_official": True,
    },
]


def ensure_decks_exist() -> dict[str, int]:
    """Ensure all decks exist and return tag -> ID mapping."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    # Get existing decks
    response = httpx.get(
        f"{SUPABASE_URL}/rest/v1/decks?select=id,name",
        headers=headers,
    )
    response.raise_for_status()
    existing = {d["name"]: d["id"] for d in response.json()}

    deck_map = {}

    for deck_def in DECK_DEFINITIONS:
        tag = deck_def["tag"]
        name = deck_def["name"]

        if name in existing:
            deck_map[tag] = existing[name]
            print(f"    [EXISTS] {name} (id={existing[name]})")
        else:
            # Create new deck
            now = datetime.utcnow().isoformat()
            record = {
                "created_at": now,
                "updated_at": now,
                "name": name,
                "description": deck_def["description"],
                "category": deck_def["category"],
                "difficulty_level": deck_def["difficulty_level"],
                "is_public": deck_def["is_public"],
                "is_official": deck_def["is_official"],
            }

            response = httpx.post(
                f"{SUPABASE_URL}/rest/v1/decks",
                headers={
                    **headers,
                    "Content-Type": "application/json",
                    "Prefer": "return=representation",
                },
                json=record,
            )
            response.raise_for_status()
            new_deck = response.json()[0]
            deck_map[tag] = new_deck["id"]
            print(f"    [CREATED] {name} (id={new_deck['id']})")

    return deck_map


def get_deck_map() -> dict[str, int]:
    """Get deck name to ID mapping from Supabase."""
    return ensure_decks_exist()


def seed_vocabulary():
    """Seed vocabulary cards via REST API."""
    print("=" * 60)
    print("SEEDING VOCABULARY VIA REST API")
    print("=" * 60)

    if not VOCABULARY_JSON.exists():
        print(f"❌ {VOCABULARY_JSON} not found!")
        return

    # Get deck mapping
    print("\nFetching deck IDs...")
    deck_map = get_deck_map()
    print(f"  Deck map: {deck_map}")

    # Load vocabulary
    print("\nLoading vocabulary JSON...")
    with open(VOCABULARY_JSON, encoding="utf-8") as f:
        data = json.load(f)
    words = data.get("words", [])
    total = len(words)
    print(f"  Loaded {total} words")

    # Prepare headers
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    # Batch insert
    batch_size = 500
    inserted = 0

    print("\nInserting cards...")
    for i in range(0, total, batch_size):
        batch = words[i : i + batch_size]
        records = []

        for word_data in batch:
            tags = word_data.get("tags", [])

            # Determine deck_id by priority
            deck_id = None
            for priority_tag in TAG_PRIORITY:
                if priority_tag in tags and priority_tag in deck_map:
                    deck_id = deck_map[priority_tag]
                    break

            now = datetime.utcnow().isoformat()

            # Use UK audio URL if available, fallback to US
            audio_url = word_data.get("audio_url_uk") or word_data.get("audio_url_us")

            record = {
                "created_at": now,
                "updated_at": now,
                "english_word": word_data.get("english_word", ""),
                "korean_meaning": word_data.get("korean_meaning", ""),
                "part_of_speech": word_data.get("part_of_speech"),
                "pronunciation_ipa": word_data.get("pronunciation_ipa"),
                "definition_en": word_data.get("definition_en"),
                "difficulty_level": word_data.get("difficulty_level"),
                "cefr_level": word_data.get("cefr_level"),
                "frequency_rank": word_data.get("frequency_rank"),
                "audio_url": audio_url,
                "example_sentences": word_data.get("example_sentences"),
                "tags": tags,
                "deck_id": deck_id,
                "is_verified": False,
            }
            records.append(record)

        # Insert batch
        response = httpx.post(
            f"{SUPABASE_URL}/rest/v1/vocabulary_cards",
            headers=headers,
            json=records,
            timeout=60.0,
        )

        if response.status_code not in [200, 201]:
            print(f"  ❌ Error at batch {i}: {response.text}")
            continue

        inserted += len(records)
        print(f"  [PROGRESS] {min(i + batch_size, total)}/{total} cards inserted...")

    print(f"\n✅ Inserted {inserted} vocabulary cards")


def verify_counts():
    """Verify card counts per deck."""
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Prefer": "count=exact",
    }

    # Get decks
    response = httpx.get(
        f"{SUPABASE_URL}/rest/v1/decks?select=id,name",
        headers=headers,
    )
    decks = response.json()

    print("\nCards per deck:")
    for d in decks:
        response = httpx.get(
            f"{SUPABASE_URL}/rest/v1/vocabulary_cards?deck_id=eq.{d['id']}&select=count",
            headers=headers,
        )
        count = response.headers.get("content-range", "*/0").split("/")[-1]
        print(f"  [{d['id']}] {d['name']}: {count} cards")


if __name__ == "__main__":
    seed_vocabulary()
    verify_counts()
