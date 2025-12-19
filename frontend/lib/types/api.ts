// 백엔드 API 문서 기반 타입 정의

export interface User {
  id: number
  email: string
  username: string
  is_active: boolean
  is_superuser: boolean
  created_at: string
}

export interface UserProfile {
  goal: "job" | "exam" | "travel" | "hobby"
  level: "beginner" | "intermediate" | "advanced"
  daily_time: 10 | 20 | 30
}

export interface VocabularyCard {
  id: number
  word: string
  definition: string // 한글 뜻
  pronunciation?: string // 발음 기호
  example_sentence?: string
  example_translation?: string
  audio_url?: string
  difficulty_level?: number
}

// FSRS Rating Constants
export const FSRS_RATING = {
  AGAIN: 1,
  HARD: 2,
  GOOD: 3,
  EASY: 4,
} as const

export type FsrsRating = (typeof FSRS_RATING)[keyof typeof FSRS_RATING]

export interface ReviewLog {
  card_id: number
  rating: FsrsRating
  reviewed_at: string
}

export interface DashboardStats {
  streak_days: number
  today_review_count: number
  today_review_total: number
  new_cards_count: number
  total_cards_learned: number
  study_time_minutes: number
}
