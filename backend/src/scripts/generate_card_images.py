"""Batch-generate Gemini association images for vocabulary cards.

Run with:
  cd src && uv run python scripts/generate_card_images.py

Requires env:
  - DATABASE_URL
  - GEMINI_API_KEY
  - SUPABASE_URL
  - SUPABASE_SECRET_KEY
  - SUPABASE_STORAGE_BUCKET (optional, default: card-images)
  - GEMINI_IMAGE_MODEL (optional, default: gemini-3-pro-image-preview)
"""

from __future__ import annotations

import argparse
import asyncio
from datetime import datetime

from sqlmodel import select

from app.config import settings
from app.database import async_session_maker
from app.models.tables.vocabulary_card import VocabularyCard
from app.services.gemini_image_service import GeminiImageService
from app.services.supabase_storage_service import SupabaseStorageService


def _build_prompt(card: VocabularyCard) -> str:
    # Keep prompt short, visual, and avoid rendering text.
    word = card.english_word
    meaning = card.korean_meaning
    pos = card.part_of_speech
    pos_hint = f" ({pos})" if pos else ""

    return (
        "Create one high-quality, vivid illustration to help a Korean learner remember an English word. "
        "No text, letters, captions, watermarks, or logos in the image. "
        "Single scene, clear subject, simple background, visually memorable. "
        f"Target word: '{word}'{pos_hint}. Korean meaning: '{meaning}'."
    )


def _ext_from_mime(mime_type: str) -> str:
    mt = (mime_type or "").lower().strip()
    return {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/webp": "webp",
    }.get(mt, "png")


async def _process_card(card_id: int, *, force: bool, dry_run: bool) -> bool:
    async with async_session_maker() as session:
        card = await session.get(VocabularyCard, card_id)
        if not card:
            return False

        if not force and card.image_url:
            return False

        prompt = _build_prompt(card)
        model_id = settings.gemini_image_model

        # Mark pending
        card.image_status = "pending"
        card.image_error = None
        card.image_prompt = prompt
        card.image_model = model_id
        await session.commit()

        if dry_run:
            return True

        try:
            generated = GeminiImageService.generate_image(prompt, model=model_id)
            ext = _ext_from_mime(generated.mime_type)

            storage_path = f"vocabulary_cards/{card.id}/image.{ext}"
            public_url = SupabaseStorageService.upload_bytes(
                bucket=settings.supabase_storage_bucket,
                path=storage_path,
                data=generated.bytes,
                mime_type=generated.mime_type,
            )

            card.image_storage_path = storage_path
            card.image_url = public_url
            card.image_status = "ready"
            card.image_generated_at = datetime.utcnow()
            card.image_error = None
            await session.commit()
            return True
        except Exception as e:  # noqa: BLE001
            card.image_status = "failed"
            card.image_error = str(e)[:2000]
            await session.commit()
            return False


async def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Gemini images for vocabulary cards")
    parser.add_argument("--limit", type=int, default=0, help="Max cards to process (0 = no limit)")
    parser.add_argument("--force", action="store_true", help="Regenerate even if image_url exists")
    parser.add_argument(
        "--dry-run", action="store_true", help="Only mark pending, do not call APIs"
    )
    args = parser.parse_args()

    async with async_session_maker() as session:
        stmt = select(VocabularyCard.id)
        if not args.force:
            stmt = stmt.where(VocabularyCard.image_url == None)  # noqa: E711
        stmt = stmt.order_by(VocabularyCard.id)
        if args.limit and args.limit > 0:
            stmt = stmt.limit(args.limit)
        result = await session.exec(stmt)
        card_ids = list(result.all())

    if not card_ids:
        print("No cards to process")
        return

    print(
        f"Processing {len(card_ids)} cards (bucket={settings.supabase_storage_bucket}, model={settings.gemini_image_model})"
    )

    ok = 0
    fail = 0
    for cid in card_ids:
        success = await _process_card(cid, force=args.force, dry_run=args.dry_run)
        if success:
            ok += 1
            print(f"OK card_id={cid}")
        else:
            fail += 1
            print(f"FAIL card_id={cid}")

    print(f"Done. ok={ok} fail={fail}")


if __name__ == "__main__":
    asyncio.run(main())
