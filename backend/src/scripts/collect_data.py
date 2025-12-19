"""
Data collection script for vocabulary deck data.

This script:
1. Downloads NGSL, NAWL, BSL, AWL word lists from official sources
2. Enriches words with WordNet definitions and examples
3. Merges words with multi-tagging for duplicates
4. Outputs a single JSON file for seeding

Run with: uv run python src/scripts/collect_data.py
"""

import json
import re
from pathlib import Path

import httpx
import nltk
import pandas as pd
from nltk.corpus import wordnet as wn

# Ensure WordNet data is downloaded
try:
    wn.synsets("test")
except LookupError:
    print("Downloading WordNet data...")
    nltk.download("wordnet")
    nltk.download("omw-1.4")

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
OUTPUT_FILE = DATA_DIR / "vocabulary.json"

# Source URLs (from GitHub antdurrant/word.lists repository)
SOURCES = {
    "ngsl": "https://raw.githubusercontent.com/antdurrant/word.lists/master/data-raw/list_ngsl/NGSL+1.01+with+SFI.xlsx",
    "bsl": "https://raw.githubusercontent.com/antdurrant/word.lists/master/data-raw/list_business/BSL_1.01_SFI_freq_bands.csv",
    "awl": "https://raw.githubusercontent.com/antdurrant/word.lists/master/data-raw/list_ASWL/Dang%2C%20Coxhead%2C%20%26%20Webb_ASWL%20flemmas%20within%20Level%206%20word%20families.xlsx",
    # New sources
    "oxford5000": "https://raw.githubusercontent.com/tyypgzl/Oxford-5000-words/main/full-word.json",
    "gre": "https://raw.githubusercontent.com/Xatta-Trone/gre-words-collection/main/word-list/combined.csv",
}

# Deck metadata for reference
DECK_METADATA = {
    "ngsl": {
        "name": "General English (NGSL)",
        "description": "New General Service List - 2800 most common English words covering ~92% of general text",
        "category": "daily",
        "difficulty_level": "beginner",
        "cefr_level": "A1-B2",
        "is_public": True,
        "is_official": True,
    },
    "ngsl_1000": {
        "name": "Basic Core 1000",
        "description": "Top 1000 most common English words from NGSL for beginners",
        "category": "daily",
        "difficulty_level": "beginner",
        "cefr_level": "A1-A2",
        "is_public": True,
        "is_official": True,
    },
    "nawl": {
        "name": "Academic (NAWL)",
        "description": "New Academic Word List - 963 essential academic vocabulary for TOEFL and academic writing",
        "category": "academic",
        "difficulty_level": "advanced",
        "cefr_level": "B2-C1",
        "is_public": True,
        "is_official": True,
    },
    "bsl": {
        "name": "Business English (BSL)",
        "description": "Business Service List - 1700 essential business and professional vocabulary",
        "category": "business",
        "difficulty_level": "intermediate",
        "cefr_level": "B1-C1",
        "is_public": True,
        "is_official": True,
    },
    "awl": {
        "name": "Academic (AWL)",
        "description": "Academic Spoken Word List - Academic vocabulary for IELTS and academic English",
        "category": "academic",
        "difficulty_level": "advanced",
        "cefr_level": "B2-C1",
        "is_public": True,
        "is_official": True,
    },
    "oxford5000": {
        "name": "Oxford 5000",
        "description": "Oxford Learner's Dictionary 5000 most important words for English learners",
        "category": "daily",
        "difficulty_level": "intermediate",
        "cefr_level": "A1-C1",
        "is_public": True,
        "is_official": True,
    },
    "gre": {
        "name": "GRE Advanced",
        "description": "Graduate Record Examination vocabulary - advanced academic and professional words",
        "category": "academic",
        "difficulty_level": "advanced",
        "cefr_level": "C1-C2",
        "is_public": True,
        "is_official": True,
    },
}


def download_file(url: str, filename: str) -> Path:
    """Download a file from URL to raw directory."""
    filepath = RAW_DIR / filename
    if filepath.exists():
        print(f"  [SKIP] {filename} already exists")
        return filepath

    print(f"  [DOWNLOAD] {filename}...")
    response = httpx.get(url, follow_redirects=True, timeout=60.0)
    response.raise_for_status()

    filepath.write_bytes(response.content)
    print(f"  [OK] Saved to {filepath}")
    return filepath


def parse_ngsl(filepath: Path) -> tuple[list[dict], list[dict]]:
    """Parse NGSL Excel file. Returns (ngsl_words, nawl_words)."""
    print("  [PARSE] NGSL file (includes NGSL core and NAWL)...")
    df = pd.read_excel(filepath, sheet_name=0)

    print(f"    Columns: {list(df.columns)}")
    print(f"    Wordlist values: {df['Wordlist'].unique()}")

    ngsl_words = []
    nawl_words = []

    for idx, row in df.iterrows():
        wordlist = str(row.get("Wordlist", "")).lower()

        # Get the word
        headword = None
        for col in ["Lemma", "lemma", "Headword", "headword", "Word", "word"]:
            if col in df.columns:
                val = row[col]
                if pd.notna(val):
                    headword = str(val).strip().lower()
                    break

        if not headword or headword == "nan":
            continue

        # Get rank
        rank = None
        for col in ["Rank", "rank"]:
            if col in df.columns:
                val = row[col]
                if pd.notna(val):
                    try:
                        rank = int(val)
                    except (ValueError, TypeError):
                        pass
                    break

        if rank is None:
            rank = idx + 1

        # Categorize by wordlist
        if "ngsl" in wordlist and "nawl" not in wordlist:
            ngsl_words.append(
                {
                    "word": headword,
                    "rank": rank,
                    "source": "ngsl",
                }
            )
        elif "nawl" in wordlist:
            nawl_words.append(
                {
                    "word": headword,
                    "rank": len(nawl_words) + 1,  # NAWL has its own ranking
                    "source": "nawl",
                }
            )

    print(f"  [OK] Parsed {len(ngsl_words)} NGSL core words")
    print(f"  [OK] Parsed {len(nawl_words)} NAWL words")
    return ngsl_words, nawl_words


def parse_bsl(filepath: Path) -> list[dict]:
    """Parse BSL CSV file."""
    print("  [PARSE] BSL...")

    # BSL is a CSV file
    df = pd.read_csv(filepath)

    print(f"    Columns: {list(df.columns)}")

    words = []
    for idx, row in df.iterrows():
        headword = None
        for col in ["Headword", "headword", "Word", "word", "Lemma", "lemma"]:
            if col in df.columns:
                val = row[col]
                if pd.notna(val):
                    headword = str(val).strip().lower()
                    break

        if not headword:
            val = row.iloc[0]
            if pd.notna(val):
                headword = str(val).strip().lower()

        if not headword or headword == "nan":
            continue

        words.append(
            {
                "word": headword,
                "rank": idx + 1,
                "source": "bsl",
            }
        )

    print(f"  [OK] Parsed {len(words)} BSL words")
    return words


def parse_awl(filepath: Path) -> list[dict]:
    """Parse AWL Excel file (ASWL - Academic Spoken Word List)."""
    print("  [PARSE] AWL (ASWL)...")

    # Read all sheets
    xls = pd.ExcelFile(filepath)
    print(f"    Sheets: {xls.sheet_names}")

    words = []
    seen = set()  # Avoid duplicates

    # Process Level sheets (1-4)
    for sheet in xls.sheet_names:
        if "Level" not in sheet:
            continue

        df = pd.read_excel(xls, sheet_name=sheet)
        print(f"    Processing {sheet}: {len(df)} rows")

        # Get headword column (usually "Level 6 word family headword")
        headword_col = None
        for col in df.columns:
            if "headword" in col.lower():
                headword_col = col
                break

        if not headword_col:
            headword_col = df.columns[1] if len(df.columns) > 1 else df.columns[0]

        for _idx, row in df.iterrows():
            val = row[headword_col]
            if pd.notna(val):
                headword = str(val).strip().lower()
                if headword and headword != "nan" and headword not in seen:
                    seen.add(headword)
                    words.append(
                        {
                            "word": headword,
                            "rank": len(words) + 1,
                            "source": "awl",
                        }
                    )

    print(f"  [OK] Parsed {len(words)} AWL words")
    return words


def parse_oxford5000(filepath: Path) -> list[dict]:
    """Parse Oxford 5000 JSON file with rich metadata."""
    print("  [PARSE] Oxford 5000...")

    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)

    words = []
    seen = set()

    for item in data:
        value = item.get("value", {})
        word = value.get("word", "").strip().lower()

        if not word or word in seen:
            continue

        seen.add(word)

        # Get CEFR level from Oxford data
        cefr_level = value.get("level", "B1")

        # Get part of speech
        pos = value.get("type", "").lower()
        if pos:
            # Normalize POS
            pos_map = {
                "noun": "noun",
                "verb": "verb",
                "adjective": "adjective",
                "adverb": "adverb",
                "preposition": "preposition",
                "conjunction": "conjunction",
                "determiner": "determiner",
                "pronoun": "pronoun",
                "exclamation": "exclamation",
                "indefinite article": "article",
                "definite article": "article",
                "modal verb": "verb",
                "auxiliary verb": "verb",
                "linking verb": "verb",
                "number": "number",
            }
            pos = pos_map.get(pos, pos.split()[0] if pos else None)

        # Get phonetics
        phonetics = value.get("phonetics", {})
        ipa_uk = phonetics.get("uk", "") if isinstance(phonetics, dict) else ""
        ipa_us = phonetics.get("us", "") if isinstance(phonetics, dict) else ""

        # Get audio URLs
        audio_uk = value.get("uk", {}).get("mp3", "")
        audio_us = value.get("us", {}).get("mp3", "")

        words.append(
            {
                "word": word,
                "source": "oxford5000",
                "cefr_level": cefr_level,
                "part_of_speech": pos,
                "pronunciation_ipa": ipa_uk or ipa_us,
                "audio_url_uk": audio_uk,
                "audio_url_us": audio_us,
            }
        )

    print(f"  [OK] Parsed {len(words)} Oxford 5000 words")
    return words


def parse_gre(filepath: Path) -> list[dict]:
    """Parse GRE word list CSV (words only)."""
    print("  [PARSE] GRE combined word list...")

    words = []
    seen = set()

    with open(filepath, encoding="utf-8") as f:
        for line in f:
            word = line.strip().lower()
            # Clean the word
            word = re.sub(r"[^a-zA-Z\-\']", "", word)

            if not word or len(word) < 2 or word in seen:
                continue

            seen.add(word)
            words.append(
                {
                    "word": word,
                    "source": "gre",
                }
            )

    print(f"  [OK] Parsed {len(words)} GRE words")
    return words


def get_wordnet_data(word: str) -> dict:
    """Get definition, examples, and POS from WordNet."""
    synsets = wn.synsets(word)
    if not synsets:
        return {"definition_en": None, "example_sentences": [], "part_of_speech": None}

    # Get the most common synset (first one)
    syn = synsets[0]

    # Map WordNet POS to readable format
    pos_map = {
        "n": "noun",
        "v": "verb",
        "a": "adjective",
        "r": "adverb",
        "s": "adjective",  # satellite adjective
    }
    pos = pos_map.get(syn.pos(), None)

    # Get definition
    definition = syn.definition()

    # Get examples (up to 3)
    examples = []
    for s in synsets[:3]:
        for ex in s.examples()[:2]:
            if ex not in [e.get("en") for e in examples]:
                examples.append({"en": ex, "ko": None})
            if len(examples) >= 3:
                break
        if len(examples) >= 3:
            break

    return {
        "definition_en": definition,
        "example_sentences": examples if examples else None,
        "part_of_speech": pos,
    }


def clean_word(word: str) -> str:
    """Clean and normalize a word."""
    # Remove numbers, special characters, keep only letters and hyphens
    word = re.sub(r"[^a-zA-Z\-\']", "", word)
    return word.lower().strip()


def merge_and_tag(word_lists: dict[str, list[dict]]) -> dict[str, dict]:
    """Merge word lists with multi-tagging for duplicates."""
    print("\n[MERGE] Merging word lists with multi-tagging...")

    all_words = {}

    # Process NGSL first (as base frequency)
    for item in word_lists.get("ngsl", []):
        word = clean_word(item["word"])
        if not word or len(word) < 2:
            continue

        all_words[word] = {
            "english_word": word,
            "tags": ["ngsl"],
            "frequency_rank": item["rank"],
        }
        if item["rank"] <= 1000:
            all_words[word]["tags"].append("ngsl_1000")

    # Process Oxford 5000 (has rich metadata)
    for item in word_lists.get("oxford5000", []):
        word = clean_word(item["word"])
        if not word or len(word) < 2:
            continue

        if word in all_words:
            # Add tag and merge Oxford metadata
            if "oxford5000" not in all_words[word]["tags"]:
                all_words[word]["tags"].append("oxford5000")
            # Use Oxford's CEFR if available (more accurate)
            if item.get("cefr_level"):
                all_words[word]["oxford_cefr"] = item["cefr_level"]
            # Add Oxford POS if missing
            if item.get("part_of_speech") and not all_words[word].get("part_of_speech"):
                all_words[word]["part_of_speech"] = item["part_of_speech"]
            # Add pronunciation
            if item.get("pronunciation_ipa"):
                all_words[word]["pronunciation_ipa"] = item["pronunciation_ipa"]
            # Add audio URLs
            if item.get("audio_url_uk"):
                all_words[word]["audio_url_uk"] = item["audio_url_uk"]
            if item.get("audio_url_us"):
                all_words[word]["audio_url_us"] = item["audio_url_us"]
        else:
            # New word from Oxford
            all_words[word] = {
                "english_word": word,
                "tags": ["oxford5000"],
                "frequency_rank": None,
                "oxford_cefr": item.get("cefr_level"),
                "part_of_speech": item.get("part_of_speech"),
                "pronunciation_ipa": item.get("pronunciation_ipa"),
                "audio_url_uk": item.get("audio_url_uk"),
                "audio_url_us": item.get("audio_url_us"),
            }

    # Process other lists and merge
    for source, items in word_lists.items():
        if source in ["ngsl", "oxford5000"]:
            continue

        for item in items:
            word = clean_word(item["word"])
            if not word or len(word) < 2:
                continue

            if word in all_words:
                # Add tag to existing word
                if source not in all_words[word]["tags"]:
                    all_words[word]["tags"].append(source)
            else:
                # New word
                all_words[word] = {
                    "english_word": word,
                    "tags": [source],
                    "frequency_rank": None,
                }

    print(f"  [OK] Merged into {len(all_words)} unique words")
    return all_words


def enrich_with_wordnet(words: dict[str, dict], batch_size: int = 100) -> dict[str, dict]:
    """Enrich words with WordNet data."""
    print(f"\n[ENRICH] Adding WordNet definitions for {len(words)} words...")

    total = len(words)
    for idx, (word, data) in enumerate(words.items()):
        if idx % batch_size == 0:
            print(f"  [PROGRESS] {idx}/{total} ({idx * 100 // total}%)")

        wn_data = get_wordnet_data(word)
        data.update(wn_data)

    print(f"  [OK] Enriched {total} words with WordNet data")
    return words


def assign_difficulty(words: dict[str, dict]) -> dict[str, dict]:
    """Assign difficulty level based on tags, frequency, and Oxford CEFR."""
    print("\n[DIFFICULTY] Assigning difficulty levels...")

    cefr_to_difficulty = {
        "A1": "beginner",
        "A2": "beginner",
        "B1": "intermediate",
        "B2": "intermediate",
        "C1": "advanced",
        "C2": "advanced",
    }

    for _word, data in words.items():
        tags = data.get("tags", [])
        rank = data.get("frequency_rank")
        oxford_cefr = data.get("oxford_cefr")

        # Use Oxford CEFR if available (most accurate)
        if oxford_cefr:
            data["cefr_level"] = oxford_cefr
            data["difficulty_level"] = cefr_to_difficulty.get(oxford_cefr, "intermediate")
        # Otherwise, determine by tags and rank
        elif "ngsl_1000" in tags:
            data["difficulty_level"] = "beginner"
            data["cefr_level"] = "A1"
        elif "ngsl" in tags and rank and rank <= 2000:
            data["difficulty_level"] = "beginner"
            data["cefr_level"] = "A2"
        elif "ngsl" in tags:
            data["difficulty_level"] = "intermediate"
            data["cefr_level"] = "B1"
        elif "bsl" in tags:
            data["difficulty_level"] = "intermediate"
            data["cefr_level"] = "B2"
        elif "gre" in tags:
            # GRE words are typically C1-C2 level
            data["difficulty_level"] = "advanced"
            data["cefr_level"] = "C1"
        elif "nawl" in tags or "awl" in tags:
            data["difficulty_level"] = "advanced"
            data["cefr_level"] = "C1"
        elif "oxford5000" in tags:
            # Oxford-only words default to B1
            data["difficulty_level"] = "intermediate"
            data["cefr_level"] = "B1"
        else:
            data["difficulty_level"] = "intermediate"
            data["cefr_level"] = "B1"

        # Clean up temporary oxford_cefr field
        if "oxford_cefr" in data:
            del data["oxford_cefr"]

    print("  [OK] Difficulty levels assigned")
    return words


def save_output(words: dict[str, dict], deck_metadata: dict) -> None:
    """Save final output to JSON files."""
    print("\n[SAVE] Saving output files...")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Convert to list format
    word_list = list(words.values())

    # 1. Save merged vocabulary.json (all words)
    merged_output = {
        "metadata": {
            "total_words": len(word_list),
            "decks": deck_metadata,
        },
        "words": word_list,
    }
    OUTPUT_FILE.write_text(
        json.dumps(merged_output, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  [OK] Saved {len(word_list)} words to {OUTPUT_FILE}")

    # 2. Save separate JSON files per deck
    decks_dir = DATA_DIR / "decks"
    decks_dir.mkdir(parents=True, exist_ok=True)

    deck_files = {
        "ngsl_1000": "basic_1000.json",
        "ngsl": "ngsl_general.json",
        "nawl": "nawl_academic.json",
        "bsl": "bsl_business.json",
        "awl": "awl_academic.json",
        "oxford5000": "oxford_5000.json",
        "gre": "gre_advanced.json",
    }

    for tag, filename in deck_files.items():
        deck_words = [w for w in word_list if tag in w.get("tags", [])]
        if not deck_words:
            continue

        deck_output = {
            "metadata": {
                "deck": deck_metadata.get(tag, {}),
                "total_words": len(deck_words),
            },
            "words": deck_words,
        }

        filepath = decks_dir / filename
        filepath.write_text(json.dumps(deck_output, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  [OK] Saved {len(deck_words)} words to {filepath}")

    # 3. Save decks metadata
    decks_meta_file = DATA_DIR / "decks_metadata.json"
    decks_meta_file.write_text(
        json.dumps(deck_metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"  [OK] Saved deck metadata to {decks_meta_file}")

    # Print statistics
    print("\n" + "=" * 50)
    print("STATISTICS")
    print("=" * 50)

    tag_counts = {}
    for word_data in word_list:
        for tag in word_data.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1]):
        print(f"  {tag}: {count} words")

    # Count words with definitions
    with_def = sum(1 for w in word_list if w.get("definition_en"))
    print(
        f"\n  Words with definitions: {with_def}/{len(word_list)} ({with_def * 100 // len(word_list)}%)"
    )


def main():
    """Main data collection function."""
    print("\n" + "=" * 50)
    print("VOCABULARY DATA COLLECTION")
    print("=" * 50)

    # Ensure directories exist
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1: Download source files
    print("\n[STEP 1] Downloading source files...")
    files = {}
    for source, url in SOURCES.items():
        if url.endswith(".xlsx"):
            ext = "xlsx"
        elif url.endswith(".csv"):
            ext = "csv"
        elif url.endswith(".json"):
            ext = "json"
        else:
            ext = "txt"
        files[source] = download_file(url, f"{source}.{ext}")

    # Step 2: Parse each source
    print("\n[STEP 2] Parsing source files...")

    # NGSL file contains both NGSL and NAWL
    ngsl_words, nawl_words = parse_ngsl(files["ngsl"])

    word_lists = {
        "ngsl": ngsl_words,
        "nawl": nawl_words,
        "bsl": parse_bsl(files["bsl"]),
        "awl": parse_awl(files["awl"]),
        "oxford5000": parse_oxford5000(files["oxford5000"]),
        "gre": parse_gre(files["gre"]),
    }

    # Step 3: Merge and tag
    all_words = merge_and_tag(word_lists)

    # Step 4: Enrich with WordNet
    all_words = enrich_with_wordnet(all_words)

    # Step 5: Assign difficulty levels
    all_words = assign_difficulty(all_words)

    # Step 6: Save output
    save_output(all_words, DECK_METADATA)

    print("\n" + "=" * 50)
    print("DATA COLLECTION COMPLETE!")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    main()
