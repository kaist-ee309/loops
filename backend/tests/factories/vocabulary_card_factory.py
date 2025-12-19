"""Factory for VocabularyCard model."""

import factory

from app.models import VocabularyCard
from tests.factories.base import AsyncSQLModelFactory


class VocabularyCardFactory(AsyncSQLModelFactory):
    """Factory for creating VocabularyCard instances."""

    class Meta:
        model = VocabularyCard

    id = factory.Sequence(lambda n: n + 1)

    english_word = factory.Faker("word")
    korean_meaning = factory.Faker("word", locale="ko_KR")
    part_of_speech = factory.Faker(
        "random_element", elements=["noun", "verb", "adjective", "adverb"]
    )

    # Pronunciation
    pronunciation_ipa = factory.LazyAttribute(lambda o: f"/ˈ{o.english_word[:3]}/")

    # Definition
    definition_en = factory.Faker("sentence")

    # Entry type
    word_type = "word"

    # Categorization
    difficulty_level = factory.Faker(
        "random_element", elements=["beginner", "intermediate", "advanced"]
    )
    cefr_level = factory.Faker("random_element", elements=["A1", "A2", "B1", "B2", "C1", "C2"])
    category = factory.Faker("random_element", elements=["business", "travel", "academic", "daily"])

    # Frequency
    frequency_rank = factory.Sequence(lambda n: n + 1)

    # Audio
    audio_url = None

    # Deck
    deck_id = None

    # Metadata
    is_verified = True

    # JSON fields
    example_sentences = factory.LazyAttribute(
        lambda o: [{"en": f"This is an example with {o.english_word}.", "ko": "이것은 예문입니다."}]
    )
    tags = factory.LazyAttribute(lambda o: [o.category] if o.category else [])
    cloze_sentences = factory.LazyAttribute(
        lambda o: [
            {
                "sentence": "Please fill in the _____.",
                "answer": o.english_word,
                "hint": o.korean_meaning,
            }
        ]
    )
    related_words = None

    # Image fields
    image_url = None
    image_storage_path = None
    image_prompt = None
    image_model = None
    image_status = None
    image_error = None
    image_generated_at = None

    class Params:
        """Factory parameters for common scenarios."""

        with_image = factory.Trait(
            image_url="https://storage.example.com/images/test.png",
            image_storage_path="card-images/test.png",
            image_status="ready",
        )

        phrase = factory.Trait(
            word_type="phrase",
            english_word=factory.Faker("sentence", nb_words=3),
        )

        idiom = factory.Trait(
            word_type="idiom",
            english_word="break the ice",
            korean_meaning="분위기를 부드럽게 하다",
        )

        no_cloze = factory.Trait(
            cloze_sentences=None,
        )
