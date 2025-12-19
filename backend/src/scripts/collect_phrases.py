"""
Phrase/Idiom Data Collection Script

This script collects phrasal verbs and idioms from various sources
and inserts them into the vocabulary_cards table with word_type='phrase'.

Run with: cd src && PYTHONPATH=. uv run python scripts/collect_phrases.py
"""

import csv
import json
from datetime import datetime
from pathlib import Path

import requests

# Paths
DATA_DIR = Path(__file__).parent.parent / "data" / "phrases"
TOEFL_DECK_ID = 9  # TOEFL Essential deck

# Supabase config
BASE_URL = "https://okuopdnrlglgzqdnxmqy.supabase.co/rest/v1/vocabulary_cards"
HEADERS = {
    "apikey": "sb_secret_rH4WMoFFlfagTIIsmmHIyw_SALulPKu",
    "Authorization": "Bearer sb_secret_rH4WMoFFlfagTIIsmmHIyw_SALulPKu",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}


def parse_phrasal_verbs_json(filepath: Path) -> list[dict]:
    """Parse simple JSON array of phrasal verbs."""
    phrases = []

    with open(filepath) as f:
        data = json.load(f)

    if isinstance(data, list):
        for phrase in data:
            if isinstance(phrase, str) and len(phrase) >= 3:
                phrases.append(
                    {
                        "english_word": phrase.lower().strip(),
                        "word_type": "phrase",
                        "part_of_speech": "phrasal verb",
                        "definition_en": None,
                        "korean_meaning": "",
                        "tags": ["phrasal verb", "toefl"],
                        "source": "phrasal_verbs_json",
                    }
                )

    return phrases


def parse_common_phrasal_verbs_csv(filepath: Path) -> list[dict]:
    """Parse CSV file with phrasal verbs and meanings."""
    phrases = []

    with open(filepath, encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter="\t")
        seen = set()

        for row in reader:
            phrasal = row.get("phrasal", "").strip()
            meaning = row.get("meaning", "").strip()
            example = row.get("phrase", "").strip()

            if not phrasal or len(phrasal) < 3:
                continue

            # Deduplicate within this source
            if phrasal.lower() in seen:
                continue
            seen.add(phrasal.lower())

            phrases.append(
                {
                    "english_word": phrasal.lower(),
                    "word_type": "phrase",
                    "part_of_speech": "phrasal verb",
                    "definition_en": meaning if meaning else None,
                    "korean_meaning": "",
                    "example_sentences": ([{"en": example, "ko": ""}] if example else None),
                    "tags": ["phrasal verb", "toefl"],
                    "source": "common_phrasal_verbs_csv",
                }
            )

    return phrases


def get_academic_collocations() -> list[dict]:
    """Generate common academic collocations manually."""
    # High-frequency academic collocations useful for TOEFL
    collocations = [
        # Research & Analysis
        ("carry out research", "conduct or perform research"),
        ("conduct a study", "perform a research study"),
        ("collect data", "gather information for analysis"),
        ("analyze data", "examine data to find patterns"),
        ("draw conclusions", "form final judgments based on evidence"),
        ("reach a conclusion", "arrive at a final decision or judgment"),
        ("support a hypothesis", "provide evidence for a theory"),
        ("test a hypothesis", "verify a theory through experiments"),
        # Academic Writing
        ("according to", "as stated by"),
        ("in contrast", "showing difference"),
        ("on the other hand", "from another perspective"),
        ("in addition", "furthermore"),
        ("as a result", "consequently"),
        ("due to", "because of"),
        ("in terms of", "regarding"),
        ("with regard to", "concerning"),
        ("in order to", "for the purpose of"),
        ("as well as", "in addition to"),
        # Discussion & Argument
        ("take into account", "consider"),
        ("take into consideration", "think about carefully"),
        ("make a distinction", "differentiate between"),
        ("raise a question", "bring up an issue"),
        ("address an issue", "deal with a problem"),
        ("play a role", "have an influence"),
        ("have an impact", "affect or influence"),
        ("make a contribution", "add value"),
        ("make progress", "advance or improve"),
        ("make a decision", "decide"),
        # Comparison & Contrast
        ("in comparison with", "when compared to"),
        ("in relation to", "connected with"),
        ("similar to", "like"),
        ("different from", "unlike"),
        ("the same as", "identical to"),
        # Time & Sequence
        ("at the same time", "simultaneously"),
        ("for the time being", "temporarily"),
        ("in the meantime", "during the intervening time"),
        ("sooner or later", "eventually"),
        ("from time to time", "occasionally"),
        # Cause & Effect
        ("lead to", "result in"),
        ("result in", "cause"),
        ("give rise to", "cause to happen"),
        ("bring about", "cause to happen"),
        ("account for", "explain the reason for"),
        # Emphasis
        ("above all", "most importantly"),
        ("in particular", "especially"),
        ("in fact", "actually"),
        ("as a matter of fact", "in reality"),
        ("to a large extent", "mostly"),
        ("to some extent", "partially"),
        # Conclusion
        ("in conclusion", "to summarize"),
        ("to sum up", "in summary"),
        ("all in all", "considering everything"),
        ("on the whole", "generally"),
        ("by and large", "mostly"),
    ]

    phrases = []
    for phrase, meaning in collocations:
        phrases.append(
            {
                "english_word": phrase.lower(),
                "word_type": "collocation",
                "part_of_speech": None,
                "definition_en": meaning,
                "korean_meaning": "",
                "tags": ["collocation", "academic", "toefl"],
                "source": "academic_collocations",
            }
        )

    return phrases


def get_common_idioms() -> list[dict]:
    """Common English idioms useful for TOEFL."""
    idioms = [
        ("a piece of cake", "something very easy"),
        ("break the ice", "start a conversation in a social situation"),
        ("hit the nail on the head", "describe exactly what is causing a problem"),
        ("kill two birds with one stone", "accomplish two things with one action"),
        ("let the cat out of the bag", "reveal a secret"),
        ("once in a blue moon", "very rarely"),
        ("speak of the devil", "the person we were talking about has appeared"),
        ("the ball is in your court", "it's your decision or responsibility"),
        ("under the weather", "feeling sick"),
        ("back to square one", "starting over"),
        ("beat around the bush", "avoid the main topic"),
        ("bite off more than you can chew", "take on too much"),
        ("cost an arm and a leg", "very expensive"),
        ("get out of hand", "become uncontrollable"),
        ("get the hang of it", "learn how to do something"),
        ("give someone the benefit of the doubt", "trust someone despite uncertainty"),
        ("go the extra mile", "make more effort than expected"),
        ("hang in there", "persist through difficulty"),
        ("it takes two to tango", "both parties are responsible"),
        ("jump on the bandwagon", "join a popular trend"),
        ("keep an eye on", "watch carefully"),
        ("let someone off the hook", "free from responsibility"),
        ("make ends meet", "have enough money for basic needs"),
        ("miss the boat", "miss an opportunity"),
        ("no pain no gain", "effort is required for success"),
        ("on the same page", "in agreement"),
        ("pull someone's leg", "joke with someone"),
        ("rain or shine", "no matter what happens"),
        ("see eye to eye", "agree completely"),
        ("take it with a grain of salt", "be skeptical about something"),
        ("the best of both worlds", "benefits from two different things"),
        ("think outside the box", "think creatively"),
        ("time flies", "time passes quickly"),
        ("turn over a new leaf", "start fresh"),
        ("wrap your head around", "understand something complex"),
    ]

    phrases = []
    for idiom, meaning in idioms:
        phrases.append(
            {
                "english_word": idiom.lower(),
                "word_type": "idiom",
                "part_of_speech": None,
                "definition_en": meaning,
                "korean_meaning": "",
                "tags": ["idiom", "toefl"],
                "source": "common_idioms",
            }
        )

    return phrases


def merge_and_deduplicate(all_phrases: list[dict]) -> list[dict]:
    """Merge phrases and remove duplicates."""
    seen = {}

    for phrase_data in all_phrases:
        phrase = phrase_data["english_word"].lower().strip()

        # Skip empty or too short
        if len(phrase) < 3:
            continue

        if phrase not in seen:
            seen[phrase] = phrase_data
        else:
            # Merge - keep definition if we have one
            if phrase_data.get("definition_en") and not seen[phrase].get("definition_en"):
                seen[phrase]["definition_en"] = phrase_data["definition_en"]

            # Merge tags
            existing_tags = set(seen[phrase].get("tags", []))
            new_tags = set(phrase_data.get("tags", []))
            seen[phrase]["tags"] = list(existing_tags | new_tags)

    return list(seen.values())


def insert_to_database(phrases: list[dict]) -> int:
    """Insert phrases into database via REST API."""
    # First, get existing entries to avoid duplicates
    print("Fetching existing entries...")
    existing_response = requests.get(f"{BASE_URL}?select=english_word", headers=HEADERS)
    existing_words = set()
    if existing_response.status_code == 200:
        existing_words = {w["english_word"].lower() for w in existing_response.json()}
    print(f"Found {len(existing_words)} existing entries in database")

    # Filter out existing
    new_phrases = [p for p in phrases if p["english_word"].lower() not in existing_words]
    print(f"New phrases to insert: {len(new_phrases)}")

    if not new_phrases:
        print("No new phrases to insert!")
        return 0

    # Prepare records - all records must have the same keys for Supabase bulk insert
    now = datetime.utcnow().isoformat() + "Z"
    records = []
    for phrase_data in new_phrases:
        # Add word_type to tags for now (until migration is applied)
        tags = phrase_data.get("tags", [])
        word_type = phrase_data.get("word_type", "phrase")
        if word_type not in tags:
            tags = [word_type] + tags

        record = {
            "english_word": phrase_data["english_word"],
            "korean_meaning": phrase_data.get("korean_meaning", ""),
            "part_of_speech": phrase_data.get("part_of_speech"),
            "definition_en": phrase_data.get("definition_en"),
            "difficulty_level": "intermediate",
            "cefr_level": "B2",
            "tags": tags,
            "deck_id": TOEFL_DECK_ID,
            "is_verified": False,
            "created_at": now,
            "updated_at": now,
            "example_sentences": phrase_data.get("example_sentences"),
        }
        records.append(record)

    # Batch insert
    batch_size = 100
    inserted = 0

    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        response = requests.post(BASE_URL, headers=HEADERS, json=batch)

        if response.status_code in [200, 201]:
            inserted += len(batch)
            print(f"Inserted batch {i // batch_size + 1}: {len(batch)} phrases")
        else:
            print(f"Error inserting batch: {response.status_code} - {response.text[:200]}")

    return inserted


def main():
    print("\n" + "=" * 60)
    print("PHRASE/IDIOM DATA COLLECTION")
    print("=" * 60 + "\n")

    all_phrases = []

    # Phase 1: Parse downloaded files
    print("Phase 1: Parsing downloaded files...")

    json_path = DATA_DIR / "phrasal_verbs.json"
    if json_path.exists():
        json_phrases = parse_phrasal_verbs_json(json_path)
        print(f"  Phrasal verbs JSON: {len(json_phrases)} phrases")
        all_phrases.extend(json_phrases)

    csv_path = DATA_DIR / "common_phrasal_verbs.csv"
    if csv_path.exists():
        csv_phrases = parse_common_phrasal_verbs_csv(csv_path)
        print(f"  Common phrasal verbs CSV: {len(csv_phrases)} phrases")
        all_phrases.extend(csv_phrases)

    # Phase 2: Add curated lists
    print("\nPhase 2: Adding curated academic collocations and idioms...")

    collocations = get_academic_collocations()
    print(f"  Academic collocations: {len(collocations)}")
    all_phrases.extend(collocations)

    idioms = get_common_idioms()
    print(f"  Common idioms: {len(idioms)}")
    all_phrases.extend(idioms)

    # Phase 3: Merge and deduplicate
    print("\nPhase 3: Merging and deduplicating...")
    print(f"  Total raw phrases: {len(all_phrases)}")

    unique_phrases = merge_and_deduplicate(all_phrases)
    print(f"  Unique phrases after dedup: {len(unique_phrases)}")

    # Show breakdown by type
    type_counts = {}
    for p in unique_phrases:
        wt = p.get("word_type", "phrase")
        type_counts[wt] = type_counts.get(wt, 0) + 1
    print("  By word_type:")
    for wt, count in sorted(type_counts.items()):
        print(f"    {wt}: {count}")

    # Phase 4: Insert to database
    print("\nPhase 4: Inserting to database...")
    inserted = insert_to_database(unique_phrases)

    print("\n" + "=" * 60)
    print(f"COMPLETED: {inserted} new phrases inserted into TOEFL deck")
    print("=" * 60 + "\n")

    return inserted


if __name__ == "__main__":
    main()
