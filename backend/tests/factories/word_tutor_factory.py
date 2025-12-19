"""Factories for WordTutorThread and WordTutorMessage models."""

from uuid import uuid4

import factory

from app.models import ChatRole, WordTutorMessage, WordTutorThread
from tests.factories.base import AsyncSQLModelFactory


class WordTutorThreadFactory(AsyncSQLModelFactory):
    """Factory for creating WordTutorThread instances."""

    class Meta:
        model = WordTutorThread

    id = factory.LazyFunction(uuid4)

    user_id = factory.LazyFunction(uuid4)
    session_id = factory.LazyFunction(uuid4)
    card_id = factory.Sequence(lambda n: n + 1)

    starter_questions = factory.LazyFunction(
        lambda: [
            "이 단어의 어원은 무엇인가요?",
            "비슷한 의미의 단어는 무엇이 있나요?",
            "이 단어를 사용한 예문을 만들어주세요.",
        ]
    )

    class Params:
        """Factory parameters for common scenarios."""

        no_questions = factory.Trait(
            starter_questions=[],
        )


class WordTutorMessageFactory(AsyncSQLModelFactory):
    """Factory for creating WordTutorMessage instances."""

    class Meta:
        model = WordTutorMessage

    id = factory.LazyFunction(uuid4)

    thread_id = factory.LazyFunction(uuid4)
    role = ChatRole.USER
    content = factory.Faker("paragraph")

    suggested_questions = None

    # Observability fields
    openai_response_id = None
    model = None
    usage = None

    class Params:
        """Factory parameters for common scenarios."""

        user_message = factory.Trait(
            role=ChatRole.USER,
            content=factory.Faker("sentence"),
            suggested_questions=None,
            openai_response_id=None,
            model=None,
            usage=None,
        )

        assistant_message = factory.Trait(
            role=ChatRole.ASSISTANT,
            content=factory.Faker("paragraph"),
            suggested_questions=[
                "더 알고 싶은 것이 있나요?",
                "다른 예문을 원하시나요?",
            ],
            openai_response_id="chatcmpl-test123",
            model="gpt-4o-mini",
            usage={"prompt_tokens": 100, "completion_tokens": 50, "total_tokens": 150},
        )

        system_message = factory.Trait(
            role=ChatRole.SYSTEM,
            content="You are a helpful vocabulary tutor.",
            suggested_questions=None,
        )
