"""
TOEFL Vocabulary Data Collection Script

This script collects TOEFL vocabulary from multiple sources:
1. GitHub Academic Word Lists (AWL, NAWL, AVL, AKL) - JSON format
2. PrepScholar TOEFL Vocabulary PDF
3. TST Prep Ultimate TOEFL List PDF

Run with: cd src && PYTHONPATH=. uv run python scripts/collect_toefl_data.py
"""

import json
import re
from datetime import datetime
from pathlib import Path

import pdfplumber
import requests

# Paths
DATA_DIR = Path(__file__).parent.parent / "data" / "toefl"
TOEFL_DECK_ID = 9  # TOEFL Essential deck


def parse_awl_json(filepath: Path) -> list[dict]:
    """Parse Academic Word List JSON - structured by sublists with word families."""
    words = []
    with open(filepath) as f:
        data = json.load(f)

    for sublist_name, sublist_data in data.items():
        sublist_num = sublist_name.replace("sublist_", "")
        for headword, word_info in sublist_data.items():
            words.append(
                {
                    "english_word": headword.lower(),
                    "part_of_speech": None,
                    "definition_en": None,
                    "tags": ["toefl", "academic", "awl", f"awl_sublist_{sublist_num}"],
                    "source": "AWL",
                }
            )
            # Also add common derived forms
            subwords = word_info.get("subwords") if isinstance(word_info, dict) else None
            if subwords:
                for subword in subwords[:3]:  # Limit to avoid too many variants
                    if subword.lower() != headword.lower():
                        words.append(
                            {
                                "english_word": subword.lower(),
                                "part_of_speech": None,
                                "definition_en": None,
                                "tags": [
                                    "toefl",
                                    "academic",
                                    "awl",
                                    f"awl_sublist_{sublist_num}",
                                ],
                                "source": "AWL",
                            }
                        )
    return words


def parse_nawl_json(filepath: Path) -> list[dict]:
    """Parse New Academic Word List JSON - flat dictionary of words."""
    words = []
    with open(filepath) as f:
        data = json.load(f)

    for word in data.keys():
        words.append(
            {
                "english_word": word.lower(),
                "part_of_speech": None,
                "definition_en": None,
                "tags": ["toefl", "academic", "nawl"],
                "source": "NAWL",
            }
        )
    return words


def parse_avl_json(filepath: Path) -> list[dict]:
    """Parse Academic Vocabulary List JSON - structured by frequency bands."""
    words = []
    with open(filepath) as f:
        data = json.load(f)

    for band_name, band_data in data.items():
        band_num = band_name.replace("band_", "")
        if isinstance(band_data, dict):
            for word in band_data.keys():
                # AVL has many words, only take bands 1-3 (most frequent)
                if int(band_num) <= 3:
                    words.append(
                        {
                            "english_word": word.lower(),
                            "part_of_speech": None,
                            "definition_en": None,
                            "tags": [
                                "toefl",
                                "academic",
                                "avl",
                                f"avl_band_{band_num}",
                            ],
                            "source": "AVL",
                        }
                    )
    return words


def parse_akl_json(filepath: Path) -> list[dict]:
    """Parse Academic Keyword List JSON."""
    words = []
    with open(filepath) as f:
        data = json.load(f)

    if isinstance(data, dict):
        for category, word_list in data.items():
            if isinstance(word_list, list):
                for word in word_list:
                    words.append(
                        {
                            "english_word": word.lower(),
                            "part_of_speech": (
                                category
                                if category in ["noun", "verb", "adjective", "adverb"]
                                else None
                            ),
                            "definition_en": None,
                            "tags": ["toefl", "academic", "akl"],
                            "source": "AKL",
                        }
                    )
    return words


def parse_prepscholar_pdf(filepath: Path) -> list[dict]:
    """Parse PrepScholar TOEFL PDF."""
    words = []

    try:
        with pdfplumber.open(filepath) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # Extract words - PrepScholar format: word followed by definition
        # Pattern: word at start of line or after number
        lines = text.split("\n")
        current_word = None
        current_def = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip header/footer lines
            if any(
                skip in line.lower()
                for skip in ["prepscholar", "toefl", "page", "vocabulary list", "www."]
            ):
                continue

            # Check if this looks like a new word entry (starts with a word)
            match = re.match(r"^(\d+\.\s*)?([a-zA-Z]+)\s*[-–:]\s*(.+)$", line)
            if match:
                # Save previous word
                if current_word:
                    words.append(
                        {
                            "english_word": current_word.lower(),
                            "part_of_speech": None,
                            "definition_en": (" ".join(current_def) if current_def else None),
                            "tags": ["toefl", "prepscholar"],
                            "source": "PrepScholar",
                        }
                    )

                current_word = match.group(2)
                current_def = [match.group(3)] if match.group(3) else []
            elif current_word and line and not line[0].isdigit():
                # Continue definition
                current_def.append(line)

        # Don't forget last word
        if current_word:
            words.append(
                {
                    "english_word": current_word.lower(),
                    "part_of_speech": None,
                    "definition_en": " ".join(current_def) if current_def else None,
                    "tags": ["toefl", "prepscholar"],
                    "source": "PrepScholar",
                }
            )

    except Exception as e:
        print(f"Error parsing PrepScholar PDF: {e}")

    return words


def parse_tstprep_pdf(filepath: Path) -> list[dict]:
    """Parse TST Prep Ultimate TOEFL List PDF."""
    words = []

    try:
        with pdfplumber.open(filepath) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"

        # Extract words - look for word patterns
        lines = text.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Skip header/footer lines
            if any(
                skip in line.lower()
                for skip in [
                    "tst prep",
                    "toefl",
                    "page",
                    "ultimate",
                    "vocabulary",
                    "www.",
                    "http",
                ]
            ):
                continue

            # Pattern: word - definition or word (part of speech) - definition
            match = re.match(r"^([a-zA-Z]+)\s*(?:\([a-z\.]+\))?\s*[-–:]\s*(.+)$", line)
            if match:
                word = match.group(1)
                definition = match.group(2)

                # Filter out non-words
                if len(word) >= 3 and word.isalpha():
                    words.append(
                        {
                            "english_word": word.lower(),
                            "part_of_speech": None,
                            "definition_en": definition,
                            "tags": ["toefl", "tstprep"],
                            "source": "TST Prep",
                        }
                    )
            else:
                # Try simple word extraction
                match = re.match(r"^([a-zA-Z]{3,})$", line)
                if match:
                    words.append(
                        {
                            "english_word": match.group(1).lower(),
                            "part_of_speech": None,
                            "definition_en": None,
                            "tags": ["toefl", "tstprep"],
                            "source": "TST Prep",
                        }
                    )

    except Exception as e:
        print(f"Error parsing TST Prep PDF: {e}")

    return words


def merge_and_deduplicate(all_words: list[dict]) -> list[dict]:
    """Merge words from all sources and remove duplicates."""
    seen = {}

    for word_data in all_words:
        word = word_data["english_word"].lower().strip()

        # Skip empty or too short words
        if len(word) < 3:
            continue

        # Skip words with numbers or special characters
        if not word.isalpha():
            continue

        if word not in seen:
            seen[word] = word_data
        else:
            # Merge tags
            existing_tags = set(seen[word]["tags"])
            new_tags = set(word_data["tags"])
            seen[word]["tags"] = list(existing_tags | new_tags)

            # Keep definition if we have one
            if word_data["definition_en"] and not seen[word]["definition_en"]:
                seen[word]["definition_en"] = word_data["definition_en"]

    return list(seen.values())


def insert_to_database(words: list[dict]) -> int:
    """Insert words into database via REST API."""
    base_url = "https://okuopdnrlglgzqdnxmqy.supabase.co/rest/v1/vocabulary_cards"
    headers = {
        "apikey": "sb_secret_rH4WMoFFlfagTIIsmmHIyw_SALulPKu",
        "Authorization": "Bearer sb_secret_rH4WMoFFlfagTIIsmmHIyw_SALulPKu",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    # First, get existing words to avoid duplicates
    print("Fetching existing words...")
    existing_response = requests.get(f"{base_url}?select=english_word", headers=headers)
    existing_words = set()
    if existing_response.status_code == 200:
        existing_words = {w["english_word"].lower() for w in existing_response.json()}
    print(f"Found {len(existing_words)} existing words in database")

    # Filter out existing words
    new_words = [w for w in words if w["english_word"].lower() not in existing_words]
    print(f"New words to insert: {len(new_words)}")

    if not new_words:
        print("No new words to insert!")
        return 0

    # Prepare records for insertion
    now = datetime.utcnow().isoformat() + "Z"
    records = []
    for word_data in new_words:
        records.append(
            {
                "english_word": word_data["english_word"],
                "korean_meaning": "",  # To be translated later
                "part_of_speech": word_data["part_of_speech"],
                "definition_en": word_data["definition_en"],
                "difficulty_level": "intermediate",
                "cefr_level": "B2",
                "tags": word_data["tags"],
                "deck_id": TOEFL_DECK_ID,
                "is_verified": False,
                "created_at": now,
                "updated_at": now,
            }
        )

    # Batch insert (Supabase supports up to 1000 per request)
    batch_size = 500
    inserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        response = requests.post(base_url, headers=headers, json=batch)

        if response.status_code in [200, 201]:
            inserted += len(batch)
            print(f"Inserted batch {i // batch_size + 1}: {len(batch)} words")
        else:
            print(f"Error inserting batch: {response.status_code} - {response.text[:200]}")

    return inserted


def main():
    print("\n" + "=" * 60)
    print("TOEFL VOCABULARY DATA COLLECTION")
    print("=" * 60 + "\n")

    all_words = []

    # Phase 1: Parse JSON files
    print("Phase 1: Parsing JSON files...")

    awl_path = DATA_DIR / "AWL.json"
    if awl_path.exists():
        awl_words = parse_awl_json(awl_path)
        print(f"  AWL: {len(awl_words)} words")
        all_words.extend(awl_words)

    nawl_path = DATA_DIR / "NAWL.json"
    if nawl_path.exists():
        nawl_words = parse_nawl_json(nawl_path)
        print(f"  NAWL: {len(nawl_words)} words")
        all_words.extend(nawl_words)

    avl_path = DATA_DIR / "AVL.json"
    if avl_path.exists():
        avl_words = parse_avl_json(avl_path)
        print(f"  AVL (bands 1-3): {len(avl_words)} words")
        all_words.extend(avl_words)

    akl_path = DATA_DIR / "AKL.json"
    if akl_path.exists():
        akl_words = parse_akl_json(akl_path)
        print(f"  AKL: {len(akl_words)} words")
        all_words.extend(akl_words)

    # Phase 2: Parse PDF files
    print("\nPhase 2: Parsing PDF files...")

    prepscholar_path = DATA_DIR / "prepscholar_toefl.pdf"
    if prepscholar_path.exists():
        prepscholar_words = parse_prepscholar_pdf(prepscholar_path)
        print(f"  PrepScholar: {len(prepscholar_words)} words")
        all_words.extend(prepscholar_words)

    tstprep_path = DATA_DIR / "tstprep_toefl.pdf"
    if tstprep_path.exists():
        tstprep_words = parse_tstprep_pdf(tstprep_path)
        print(f"  TST Prep: {len(tstprep_words)} words")
        all_words.extend(tstprep_words)

    # Phase 3: Merge and deduplicate
    print("\nPhase 3: Merging and deduplicating...")
    print(f"  Total raw words: {len(all_words)}")

    unique_words = merge_and_deduplicate(all_words)
    print(f"  Unique words after dedup: {len(unique_words)}")

    # Phase 4: Insert to database
    print("\nPhase 4: Inserting to database...")
    inserted = insert_to_database(unique_words)

    print("\n" + "=" * 60)
    print(f"COMPLETED: {inserted} new words inserted into TOEFL deck")
    print("=" * 60 + "\n")

    return inserted


if __name__ == "__main__":
    main()
