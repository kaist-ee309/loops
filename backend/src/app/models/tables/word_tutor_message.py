"""Word tutor chat message model."""

from uuid import UUID, uuid4

from sqlalchemy import JSON, ForeignKey, Text, Uuid
from sqlmodel import Column, Enum, Field, SQLModel

from app.models.base import TimestampMixin
from app.models.enums import ChatRole


class WordTutorMessageBase(SQLModel):
    """Base WordTutorMessage model with shared fields."""

    thread_id: UUID = Field(
        sa_column=Column(
            Uuid,
            ForeignKey("word_tutor_threads.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
    )

    role: ChatRole = Field(
        sa_column=Column(Enum(ChatRole), nullable=False, index=True),
    )

    content: str = Field(sa_column=Column(Text, nullable=False))

    suggested_questions: list[str] | None = Field(default=None, sa_column=Column(JSON))

    # Observability / debugging
    openai_response_id: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, max_length=100)
    usage: dict | None = Field(default=None, sa_column=Column(JSON))


class WordTutorMessage(WordTutorMessageBase, TimestampMixin, table=True):
    """Word tutor message persisted for a thread."""

    __tablename__ = "word_tutor_messages"

    id: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(Uuid, primary_key=True, nullable=False),
    )
