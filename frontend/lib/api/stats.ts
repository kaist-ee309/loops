import { apiFetch } from "@/lib/api/http"

export type StatsHistoryPeriod = "7d" | "30d" | "90d" | "1y"

export interface TotalLearnedRead {
  total_learned: number
  by_level: Record<string, number>
  total_study_time_minutes: number
}

export interface StatsHistoryItem {
  date: string
  cards_studied: number
  correct_count: number
  accuracy_rate: number
}

export interface StatsHistoryRead {
  period: string
  data: StatsHistoryItem[]
}

export interface StatsAccuracyRead {
  overall_accuracy: number
  total_reviews: number
  total_correct: number
  by_period: Record<string, number | null> | any
  by_cefr_level: Record<string, number>
  trend: string
}

export function getTotalLearned(): Promise<TotalLearnedRead> {
  return apiFetch<TotalLearnedRead>("/api/v1/stats/total-learned", { auth: true })
}

export function getStatsHistory(period: StatsHistoryPeriod): Promise<StatsHistoryRead> {
  return apiFetch<StatsHistoryRead>(`/api/v1/stats/history?period=${period}`, { auth: true })
}

export function getStatsAccuracy(): Promise<StatsAccuracyRead> {
  return apiFetch<StatsAccuracyRead>("/api/v1/stats/accuracy", { auth: true })
}
