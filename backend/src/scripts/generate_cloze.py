"""
Cloze 문장 사전 생성 스크립트.

기존 vocabulary_cards에서 example_sentences가 있는 카드에 대해
cloze_sentences를 생성하여 DB를 업데이트합니다.

Run with: PYTHONPATH=src uv run python src/scripts/generate_cloze.py
"""

import asyncio
import sys
from pathlib import Path

# 상위 디렉토리를 path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.database import async_session_maker
from app.models.tables.vocabulary_card import VocabularyCard
from app.services.cloze_service import ClozeService


async def count_cards_needing_cloze(session: AsyncSession) -> dict:
    """Cloze 생성이 필요한 카드 수를 확인합니다."""
    # 전체 카드 수
    total_result = await session.exec(select(VocabularyCard))
    total = len(total_result.all())

    # example_sentences가 있는 카드
    with_examples_result = await session.exec(
        select(VocabularyCard).where(VocabularyCard.example_sentences.isnot(None))
    )
    with_examples = len(with_examples_result.all())

    # cloze_sentences가 이미 있는 카드
    with_cloze_result = await session.exec(
        select(VocabularyCard).where(VocabularyCard.cloze_sentences.isnot(None))
    )
    with_cloze = len(with_cloze_result.all())

    # 생성 필요한 카드 (example_sentences 있고, cloze_sentences 없는)
    need_cloze_result = await session.exec(
        select(VocabularyCard).where(
            VocabularyCard.example_sentences.isnot(None),
            VocabularyCard.cloze_sentences.is_(None),
        )
    )
    need_cloze = len(need_cloze_result.all())

    return {
        "total": total,
        "with_examples": with_examples,
        "with_cloze": with_cloze,
        "need_cloze": need_cloze,
    }


async def generate_cloze_batch(
    session: AsyncSession,
    batch_size: int = 100,
    max_cloze_per_card: int = 3,
) -> int:
    """배치 단위로 cloze_sentences를 생성합니다."""
    # 생성이 필요한 카드 조회
    query = (
        select(VocabularyCard)
        .where(
            VocabularyCard.example_sentences.isnot(None),
            VocabularyCard.cloze_sentences.is_(None),
        )
        .limit(batch_size)
    )

    result = await session.exec(query)
    cards = list(result.all())

    if not cards:
        return 0

    updated = 0
    for card in cards:
        # Cloze 생성
        cloze_data = ClozeService.prepare_cloze_for_storage(
            card=card,
            max_count=max_cloze_per_card,
        )

        if cloze_data:
            card.cloze_sentences = cloze_data
            session.add(card)
            updated += 1

    # 커밋
    await session.commit()

    return updated


async def generate_all_cloze(
    batch_size: int = 100,
    max_cloze_per_card: int = 3,
    dry_run: bool = False,
) -> None:
    """모든 카드에 대해 cloze_sentences를 생성합니다."""
    async with async_session_maker() as session:
        # 상태 확인
        print("\n" + "=" * 60)
        print("Cloze 문장 사전 생성 스크립트")
        print("=" * 60)

        stats = await count_cards_needing_cloze(session)
        print("\n📊 현재 상태:")
        print(f"  - 전체 카드 수: {stats['total']:,}")
        print(f"  - example_sentences 있는 카드: {stats['with_examples']:,}")
        print(f"  - cloze_sentences 있는 카드: {stats['with_cloze']:,}")
        print(f"  - 생성 필요한 카드: {stats['need_cloze']:,}")

        if stats["need_cloze"] == 0:
            print("\n✅ 생성할 cloze가 없습니다. 이미 모두 생성되었거나 예문이 없습니다.")
            return

        if dry_run:
            print("\n🔍 Dry run 모드 - 실제 업데이트는 수행하지 않습니다.")
            # 샘플 미리보기
            query = (
                select(VocabularyCard)
                .where(
                    VocabularyCard.example_sentences.isnot(None),
                    VocabularyCard.cloze_sentences.is_(None),
                )
                .limit(5)
            )
            result = await session.exec(query)
            samples = list(result.all())

            print("\n📝 샘플 미리보기 (처음 5개):")
            for card in samples:
                print(f"\n  [{card.english_word}]")
                cloze_data = ClozeService.prepare_cloze_for_storage(card, max_cloze_per_card)
                if cloze_data:
                    for i, cloze in enumerate(cloze_data, 1):
                        print(f"    {i}. {cloze['sentence']}")
                        print(f"       정답: {cloze['answer']}")
                        if cloze.get("hint"):
                            print(f"       힌트: {cloze['hint']}")
                else:
                    print("    (cloze 생성 실패 - 예문에서 단어를 찾을 수 없음)")
            return

        # 실제 생성
        print(f"\n🔄 생성 시작 (배치 크기: {batch_size})")
        total_updated = 0
        batch_num = 0

        while True:
            batch_num += 1
            updated = await generate_cloze_batch(
                session=session,
                batch_size=batch_size,
                max_cloze_per_card=max_cloze_per_card,
            )

            if updated == 0:
                break

            total_updated += updated
            print(f"  ✓ 배치 {batch_num}: {updated}개 업데이트 (누적: {total_updated}개)")

        # 최종 결과
        print(f"\n✅ 완료! 총 {total_updated}개 카드에 cloze_sentences 생성됨")

        # 최종 통계
        final_stats = await count_cards_needing_cloze(session)
        print("\n📊 최종 상태:")
        print(f"  - cloze_sentences 있는 카드: {final_stats['with_cloze']:,}")
        print(f"  - 생성 실패/불가 카드: {final_stats['need_cloze']:,}")


def main():
    """메인 함수."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cloze 문장 사전 생성 스크립트",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # Dry run (실제 업데이트 없이 미리보기)
  PYTHONPATH=src uv run python src/scripts/generate_cloze.py --dry-run

  # 실제 생성 (배치 크기 100)
  PYTHONPATH=src uv run python src/scripts/generate_cloze.py

  # 배치 크기 변경
  PYTHONPATH=src uv run python src/scripts/generate_cloze.py --batch-size 200

  # 카드당 cloze 개수 변경
  PYTHONPATH=src uv run python src/scripts/generate_cloze.py --max-cloze 5
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 업데이트 없이 미리보기만 수행",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="배치 크기 (기본값: 100)",
    )
    parser.add_argument(
        "--max-cloze",
        type=int,
        default=3,
        help="카드당 최대 cloze 개수 (기본값: 3)",
    )

    args = parser.parse_args()

    asyncio.run(
        generate_all_cloze(
            batch_size=args.batch_size,
            max_cloze_per_card=args.max_cloze,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
