import { apiFetch } from "@/lib/api/http"

export type QuizType = "word_to_meaning" | "meaning_to_word" | "cloze" | "listening"

export interface ClozeQuestion {
  sentence: string
  answer: string
  hint?: string | null
  audio_url?: string | null
}

export interface StudyCard {
  id: number
  english_word: string
  korean_meaning: string
  pronunciation_ipa?: string | null
  audio_url?: string | null
  is_new: boolean
  quiz_type: QuizType
  question: string | ClozeQuestion
  options?: string[] | null
  example_sentences?: unknown[] | null
}

export interface DueCard {
  english_word: string
  korean_meaning: string
  next_review_date?: string | null
  card_state?: string | null
}

export interface StudyOverviewResponse {
  new_cards_count: number
  review_cards_count: number
  total_available: number
  due_cards: DueCard[]
}

export interface SessionStartRequest {
  new_cards_limit?: number
  review_cards_limit?: number
}

export type StartSessionRequest = SessionStartRequest

export interface SessionStartResponse {
  session_id: string
  total_cards: number
  new_cards_count: number
  review_cards_count: number
  started_at: string
}

export interface CardRequest {
  session_id: string
  quiz_type: QuizType
}

export interface CardResponse {
  card: StudyCard | null
  cards_remaining: number
  cards_completed: number
}

export interface AnswerRequest {
  session_id: string
  card_id: number
  answer: string
  response_time_ms?: number
}

export interface AnswerResponse {
  is_correct: boolean
  correct_answer: string
  user_answer: string
  feedback?: string | null
  next_review_date?: string | null
  card_state?: string | null
}

export interface SessionSummary {
  total_cards: number
  correct: number
  wrong: number
  accuracy: number
  duration_seconds: number
}

export interface SessionCompleteResponse {
  session_summary: SessionSummary
  streak: {
    current_streak: number
    longest_streak: number
    is_new_record: boolean
    streak_status: string
    message: string
  }
  daily_goal: {
    goal: number
    completed: number
    progress: number
    is_completed: boolean
  }
  xp: {
    base_xp: number
    bonus_xp: number
    total_xp: number
  }
}

// API Functions
export async function getStudyOverview(limit = 50): Promise<StudyOverviewResponse> {
  const search = new URLSearchParams()
  search.set("limit", String(limit))

  return apiFetch<StudyOverviewResponse>(`/api/v1/study/overview?${search.toString()}`, {
    method: "GET",
    auth: true,
  })
}

export async function startSession(params: SessionStartRequest): Promise<SessionStartResponse> {
  return apiFetch<SessionStartResponse>("/api/v1/study/session/start", {
    method: "POST",
    auth: true,
    body: params,
  })
}

export async function getNextCard(sessionId: string, quizType: QuizType): Promise<CardResponse> {
  return apiFetch<CardResponse>("/api/v1/study/session/card", {
    method: "POST",
    auth: true,
    body: {
      session_id: sessionId,
      quiz_type: quizType,
    },
  })
}

export async function submitAnswer(params: AnswerRequest): Promise<AnswerResponse> {
  return apiFetch<AnswerResponse>("/api/v1/study/session/answer", {
    method: "POST",
    auth: true,
    body: params,
  })
}

export async function completeSession(sessionId: string): Promise<SessionCompleteResponse> {
  return apiFetch<SessionCompleteResponse>("/api/v1/study/session/complete", {
    method: "POST",
    auth: true,
    body: { session_id: sessionId },
  })
}
