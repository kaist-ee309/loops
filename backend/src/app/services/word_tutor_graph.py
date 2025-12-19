"""LangGraph-based word tutor chat workflows."""

from __future__ import annotations

from typing import Annotated, TypedDict
from uuid import UUID

from langchain_core.messages import AIMessage, AnyMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import RetryPolicy
from pydantic import BaseModel, Field
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.config import settings
from app.core.exceptions import NotFoundError
from app.models import VocabularyCard, WordTutorMessage, WordTutorThread
from app.models.enums import ChatRole


class StarterQuestionsOutput(BaseModel):
    starter_questions: list[str] = Field(
        description="해당 단어로 시작하기 좋은 추천 질문 리스트 (3~7개)",
    )


class TutorAnswerOutput(BaseModel):
    answer: str = Field(description="사용자 질문에 대한 답변(한국어, 학습자 친화적)")
    follow_up_questions: list[str] = Field(description="후속 추천 질문 리스트 (2~5개)")


class WordTutorState(TypedDict, total=False):
    # runtime dependencies
    db: AsyncSession

    # identifiers
    user_id: UUID
    session_id: UUID
    card_id: int
    thread_id: UUID

    # chat memory
    messages: Annotated[list[AnyMessage], add_messages]

    # context
    card: VocabularyCard

    # inputs/outputs
    input_message: str
    starter_questions: list[str]
    assistant_answer: str
    follow_up_questions: list[str]


def _build_llm() -> ChatOpenAI:
    # LangChain OpenAI reads OPENAI_API_KEY from env too, but we pass explicitly for clarity.
    api_key = settings.openai_api_key or None
    return ChatOpenAI(
        model=settings.openai_model,
        api_key=api_key,
        temperature=0.3,
        timeout=30,
    )


def _card_context_text(card: VocabularyCard) -> str:
    parts: list[str] = [
        f"영어 단어: {card.english_word}",
        f"한국어 뜻: {card.korean_meaning}",
    ]
    if card.part_of_speech:
        parts.append(f"품사: {card.part_of_speech}")
    if card.definition_en:
        parts.append(f"영어 정의: {card.definition_en}")
    if card.example_sentences:
        parts.append(f"예문: {card.example_sentences}")
    return "\n".join(parts)


async def _load_context(state: WordTutorState) -> WordTutorState:
    session = state["db"]
    thread = await session.get(WordTutorThread, state["thread_id"])
    if not thread:
        raise NotFoundError(f"Thread {state['thread_id']} not found")

    card = await session.get(VocabularyCard, thread.card_id)
    if not card:
        raise NotFoundError(f"Card {thread.card_id} not found")

    # Load recent history
    result = await session.exec(
        select(WordTutorMessage)
        .where(WordTutorMessage.thread_id == thread.id)
        .order_by(WordTutorMessage.created_at.asc())
        .limit(50)
    )
    rows = list(result.all())

    msgs: list[AnyMessage] = []
    for m in rows:
        if m.role == ChatRole.SYSTEM:
            # Internal marker messages aren't useful for the LLM.
            if m.content == "STARTER_QUESTIONS":
                continue
            msgs.append(SystemMessage(content=m.content))
        elif m.role == ChatRole.USER:
            msgs.append(HumanMessage(content=m.content))
        else:
            msgs.append(AIMessage(content=m.content))

    return {
        "card": card,
        "messages": msgs,
        "starter_questions": thread.starter_questions,
    }


def _should_generate_starters(state: WordTutorState) -> str:
    existing = state.get("starter_questions") or []
    return "generate" if len(existing) == 0 else "skip"


async def _generate_starters(state: WordTutorState) -> WordTutorState:
    llm = _build_llm()
    try:
        structured = llm.with_structured_output(StarterQuestionsOutput, method="json_schema")
    except Exception:
        structured = llm.with_structured_output(StarterQuestionsOutput, method="function_calling")

    sys = SystemMessage(
        content=(
            "너는 영어 단어 학습 앱의 AI 튜터다.\n"
            "주어진 단어를 기준으로 사용자가 학습 직후에 궁금해할 질문을 3~7개 추천해라.\n"
            "질문은 한국어로, 구체적이고 학습에 도움이 되게. 발음/뉘앙스/예문/구분/콜로케이션 위주.\n"
            "반드시 JSON 스키마에 맞춰 응답."
        ),
    )
    user = HumanMessage(content=_card_context_text(state["card"]))

    try:
        out = await structured.ainvoke([sys, user])
        starters = out.starter_questions
    except Exception:
        # fallback: safe defaults
        starters = [
            f"'{state['card'].english_word}'는 어떤 상황에서 자주 쓰이나요?",
            f"'{state['card'].english_word}'를 포함한 자연스러운 예문을 2개만 만들어줘.",
            f"'{state['card'].english_word}'의 비슷한 단어(동의어/유의어)와 차이를 알려줘.",
        ]

    return {"starter_questions": starters}


async def _save_starters(state: WordTutorState) -> WordTutorState:
    session = state["db"]
    thread = await session.get(WordTutorThread, state["thread_id"])
    if not thread:
        raise NotFoundError(f"Thread {state['thread_id']} not found")

    thread.starter_questions = state.get("starter_questions") or []
    session.add(thread)

    # Persist a system message that includes the starter questions (optional, but keeps audit trail).
    session.add(
        WordTutorMessage(
            thread_id=thread.id,
            role=ChatRole.SYSTEM,
            content="STARTER_QUESTIONS",
            suggested_questions=thread.starter_questions,
        )
    )

    await session.commit()
    return {}


async def _generate_answer(state: WordTutorState) -> WordTutorState:
    llm = _build_llm()
    try:
        structured = llm.with_structured_output(TutorAnswerOutput, method="json_schema")
    except Exception:
        structured = llm.with_structured_output(TutorAnswerOutput, method="function_calling")

    sys = SystemMessage(
        content=(
            "너는 영어 단어 학습 앱의 AI 튜터다.\n"
            "주어진 단어 컨텍스트를 바탕으로 사용자의 질문에 한국어로 답변해라.\n"
            "- 짧고 정확하게\n"
            "- 필요하면 예문 1~2개(영어+한국어)\n"
            "- 혼동되는 단어/표현이 있으면 비교\n"
            "그리고 follow_up_questions(2~5개)도 함께 추천해라.\n"
            "반드시 JSON 스키마에 맞춰 응답."
        ),
    )

    context = HumanMessage(content=f"[단어 컨텍스트]\n{_card_context_text(state['card'])}")
    user_q = HumanMessage(content=state["input_message"])

    # Keep a small amount of prior turns for coherence
    history = state.get("messages") or []
    history_tail = history[-10:]

    try:
        out = await structured.ainvoke([sys, context, *history_tail, user_q])
        answer = out.answer
        followups = out.follow_up_questions
    except Exception:
        answer = "지금은 답변을 생성하는 데 실패했어요. 질문을 조금만 바꿔서 다시 보내줘."
        followups = []

    return {"assistant_answer": answer, "follow_up_questions": followups}


async def _save_turn(state: WordTutorState) -> WordTutorState:
    session = state["db"]
    thread = await session.get(WordTutorThread, state["thread_id"])
    if not thread:
        raise NotFoundError(f"Thread {state['thread_id']} not found")

    session.add(
        WordTutorMessage(
            thread_id=thread.id,
            role=ChatRole.USER,
            content=state["input_message"],
        )
    )
    session.add(
        WordTutorMessage(
            thread_id=thread.id,
            role=ChatRole.ASSISTANT,
            content=state.get("assistant_answer") or "",
            suggested_questions=state.get("follow_up_questions"),
            model=settings.openai_model,
        )
    )

    await session.commit()
    return {}


_LLM_RETRY_POLICY = RetryPolicy(
    max_attempts=3,
    initial_interval=0.5,
    backoff_factor=2.0,
)


def build_start_graph():
    """Graph for /tutor/start."""
    g = StateGraph(WordTutorState)
    g.add_node("load_context", _load_context)
    g.add_node("generate_starters", _generate_starters, retry_policy=_LLM_RETRY_POLICY)
    g.add_node("save_starters", _save_starters)

    g.add_edge(START, "load_context")
    g.add_conditional_edges(
        "load_context",
        _should_generate_starters,
        {"generate": "generate_starters", "skip": END},
    )
    g.add_edge("generate_starters", "save_starters")
    g.add_edge("save_starters", END)
    return g.compile()


def build_message_graph():
    """Graph for /tutor/message."""
    g = StateGraph(WordTutorState)
    g.add_node("load_context", _load_context)
    g.add_node("generate_answer", _generate_answer, retry_policy=_LLM_RETRY_POLICY)
    g.add_node("save_turn", _save_turn)

    g.add_edge(START, "load_context")
    g.add_edge("load_context", "generate_answer")
    g.add_edge("generate_answer", "save_turn")
    g.add_edge("save_turn", END)
    return g.compile()


START_GRAPH = build_start_graph()
MESSAGE_GRAPH = build_message_graph()
