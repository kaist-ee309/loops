import { apiFetch } from "@/lib/api/http"

export interface TodayProgressRead {
  total_reviews: number
  correct_count: number
  wrong_count: number
  accuracy_rate: number
  daily_goal: number
  goal_progress: number
}

export interface StreakRead {
  current_streak: number
  longest_streak: number
  message?: string
}

export async function getTodayProgress(): Promise<TodayProgressRead> {
  return apiFetch<TodayProgressRead>("/api/v1/profiles/me/today-progress", { auth: true })
}

export async function getStreak(): Promise<StreakRead> {
  return apiFetch<StreakRead>("/api/v1/profiles/me/streak", { auth: true })
}
