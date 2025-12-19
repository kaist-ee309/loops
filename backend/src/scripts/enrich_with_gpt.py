"""
Enrich vocabulary data with GPT-4 for missing fields.

This script:
1. Loads vocabulary.json
2. Identifies words with missing fields
3. Uses OpenAI GPT-4 to fill in missing data
4. Saves progress incrementally

Required env vars:
- OPENAI_API_KEY: Your OpenAI API key

Run with: uv run python src/scripts/enrich_with_gpt.py
"""

import asyncio
import json
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("⚠️  OPENAI_API_KEY not found in .env file")
    print("Add it to your .env file: OPENAI_API_KEY=sk-...")

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
VOCABULARY_JSON = DATA_DIR / "vocabulary.json"
ENRICHED_JSON = DATA_DIR / "vocabulary_enriched.json"
PROGRESS_FILE = DATA_DIR / "enrichment_progress.json"

# GPT settings
MODEL = "gpt-4o-mini"  # Cost-effective for bulk operations
BATCH_SIZE = 10  # Words per API call
MAX_RETRIES = 3


def load_vocabulary() -> dict:
    """Load vocabulary data."""
    with open(VOCABULARY_JSON, encoding="utf-8") as f:
        return json.load(f)


def save_vocabulary(data: dict, filepath: Path = ENRICHED_JSON) -> None:
    """Save vocabulary data."""
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  [SAVED] {filepath}")


def load_progress() -> set:
    """Load set of already processed words."""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, encoding="utf-8") as f:
            return set(json.load(f))
    return set()


def save_progress(processed: set) -> None:
    """Save progress."""
    PROGRESS_FILE.write_text(json.dumps(list(processed), ensure_ascii=False), encoding="utf-8")


def needs_enrichment(word_data: dict) -> dict:
    """Check which fields need enrichment for a word."""
    needs = {}

    # Check definition
    if not word_data.get("definition_en"):
        needs["definition_en"] = True

    # Check part of speech
    if not word_data.get("part_of_speech"):
        needs["part_of_speech"] = True

    # Check Korean meaning (always empty initially)
    if not word_data.get("korean_meaning"):
        needs["korean_meaning"] = True

    # Check example sentences
    examples = word_data.get("example_sentences")
    if not examples or len(examples) == 0:
        needs["example_sentences"] = True

    return needs


def build_prompt(words: list[dict]) -> str:
    """Build GPT prompt for batch of words."""
    word_list = []
    for w in words:
        needs = needs_enrichment(w)
        word_list.append(
            {
                "word": w["english_word"],
                "needs": list(needs.keys()),
                "current_pos": w.get("part_of_speech"),
                "current_def": w.get("definition_en"),
            }
        )

    prompt = f"""You are a vocabulary expert. For each English word below, provide ONLY the missing fields.

Words to process:
{json.dumps(word_list, indent=2)}

For each word, provide a JSON object with:
- "word": the English word
- "definition_en": A clear, concise definition (1-2 sentences) appropriate for English learners
- "part_of_speech": One of: noun, verb, adjective, adverb, preposition, conjunction, pronoun, article, interjection
- "korean_meaning": Korean translation (2-3 most common meanings, comma separated)
- "example_sentences": Array of 2 example sentences, each as {{"en": "English sentence", "ko": "Korean translation"}}

IMPORTANT:
- Only provide fields marked as needed
- Keep definitions simple and learner-friendly
- For Korean, use natural Korean expressions
- Examples should be practical, everyday sentences
- Return a JSON array of objects

Return ONLY valid JSON array, no markdown or explanation."""

    return prompt


async def call_gpt(prompt: str, client: httpx.AsyncClient) -> list[dict]:
    """Call GPT API and parse response."""
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are a vocabulary expert. Return only valid JSON.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4000,
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()

            result = response.json()
            content = result["choices"][0]["message"]["content"]

            # Parse JSON from response
            # Handle markdown code blocks if present
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            return json.loads(content.strip())

        except Exception as e:
            print(f"    ⚠️  Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(2**attempt)

    return []


async def enrich_batch(
    words: list[dict],
    client: httpx.AsyncClient,
) -> list[dict]:
    """Enrich a batch of words with GPT."""
    prompt = build_prompt(words)
    results = await call_gpt(prompt, client)

    # Map results back to words
    result_map = {r["word"]: r for r in results}

    enriched = []
    for word in words:
        eng_word = word["english_word"]
        if eng_word in result_map:
            r = result_map[eng_word]

            # Update only missing fields
            if r.get("definition_en") and not word.get("definition_en"):
                word["definition_en"] = r["definition_en"]

            if r.get("part_of_speech") and not word.get("part_of_speech"):
                word["part_of_speech"] = r["part_of_speech"]

            if r.get("korean_meaning") and not word.get("korean_meaning"):
                word["korean_meaning"] = r["korean_meaning"]

            if r.get("example_sentences"):
                existing = word.get("example_sentences") or []
                if len(existing) == 0:
                    word["example_sentences"] = r["example_sentences"]

        enriched.append(word)

    return enriched


async def main():
    """Main enrichment function."""
    print("\n" + "=" * 60)
    print("GPT VOCABULARY ENRICHMENT")
    print("=" * 60)

    if not OPENAI_API_KEY:
        print("\n❌ OPENAI_API_KEY is required. Add it to .env file.")
        return

    # Load data
    print("\n[LOAD] Loading vocabulary data...")
    data = load_vocabulary()
    words = data["words"]
    print(f"  Total words: {len(words)}")

    # Load progress
    processed = load_progress()
    print(f"  Already processed: {len(processed)}")

    # Find words needing enrichment
    to_process = []
    for w in words:
        if w["english_word"] in processed:
            continue
        needs = needs_enrichment(w)
        if needs:
            to_process.append(w)

    print(f"  Words needing enrichment: {len(to_process)}")

    if not to_process:
        print("\n✅ All words already enriched!")
        return

    # Process in batches
    print(f"\n[PROCESS] Processing in batches of {BATCH_SIZE}...")

    async with httpx.AsyncClient() as client:
        for i in range(0, len(to_process), BATCH_SIZE):
            batch = to_process[i : i + BATCH_SIZE]
            batch_words = [w["english_word"] for w in batch]

            print(f"\n  Batch {i // BATCH_SIZE + 1}: {batch_words[:3]}...")

            try:
                enriched = await enrich_batch(batch, client)

                # Update in original data
                word_map = {w["english_word"]: w for w in words}
                for ew in enriched:
                    word_map[ew["english_word"]] = ew

                # Mark as processed
                for w in batch:
                    processed.add(w["english_word"])

                # Save progress every batch
                data["words"] = list(word_map.values())
                save_vocabulary(data)
                save_progress(processed)

                print(f"    ✅ Processed {len(batch)} words")

                # Rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                print(f"    ❌ Batch failed: {e}")
                continue

    # Final stats
    print("\n" + "=" * 60)
    print("ENRICHMENT COMPLETE")
    print("=" * 60)

    # Count filled fields
    filled_def = sum(1 for w in data["words"] if w.get("definition_en"))
    filled_pos = sum(1 for w in data["words"] if w.get("part_of_speech"))
    filled_kr = sum(1 for w in data["words"] if w.get("korean_meaning"))
    filled_ex = sum(1 for w in data["words"] if w.get("example_sentences"))

    total = len(data["words"])
    print(f"\n  definition_en: {filled_def}/{total} ({filled_def * 100 // total}%)")
    print(f"  part_of_speech: {filled_pos}/{total} ({filled_pos * 100 // total}%)")
    print(f"  korean_meaning: {filled_kr}/{total} ({filled_kr * 100 // total}%)")
    print(f"  example_sentences: {filled_ex}/{total} ({filled_ex * 100 // total}%)")


if __name__ == "__main__":
    asyncio.run(main())
