import enum


class CardState(str, enum.Enum):
    """Card state enum for FSRS algorithm."""

    NEW = "NEW"
    LEARNING = "LEARNING"
    REVIEW = "REVIEW"
    RELEARNING = "RELEARNING"


class SessionStatus(str, enum.Enum):
    """Study session status enum."""

    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class QuizType(str, enum.Enum):
    """Quiz type enum."""

    WORD_TO_MEANING = "word_to_meaning"  # 영어 단어 보고 뜻 맞추기
    MEANING_TO_WORD = "meaning_to_word"  # 뜻 보고 영어 단어 맞추기
    CLOZE = "cloze"  # 빈칸 채우기
    LISTENING = "listening"  # 발음 듣고 단어 맞추기
    IMAGE_TO_WORD = "image_to_word"  # 이미지 보고 영어 단어 맞추기


class ChatRole(str, enum.Enum):
    """Chat message role enum for word tutor chat."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
