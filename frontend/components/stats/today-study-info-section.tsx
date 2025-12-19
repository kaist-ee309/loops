"use client"

import { Clock, FileText, BookOpen, Languages, MessageSquare, Headphones } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import { SummaryStatCard } from "./summary-stat-card"
import { CategoryRow } from "./category-row"

type TodayStudyCategory = {
  reviewAccuracyPercent?: number
  newCount?: number
  reviewCount?: number
}

interface TodayStudy {
  totalStudyTimeSec?: number
  totalQuestions?: number
  vocab: TodayStudyCategory
  grammar?: TodayStudyCategory
  expression?: TodayStudyCategory
  listening?: { questionCount?: number; maxLevel?: number }
}

interface TodayStudyInfoSectionProps {
  isLoading: boolean
  data?: TodayStudy
}

// Mock data for demonstration
const mockTodayStudy: TodayStudy = {
  totalStudyTimeSec: 5 * 60 * 60 + 45 * 60, // 5시간 45분
  totalQuestions: 20,
  vocab: {
    reviewAccuracyPercent: undefined,
    newCount: 20,
    reviewCount: undefined,
  },
  grammar: {
    reviewAccuracyPercent: undefined,
    newCount: undefined,
    reviewCount: undefined,
  },
  expression: {
    reviewAccuracyPercent: undefined,
    newCount: undefined,
    reviewCount: undefined,
  },
  listening: {
    questionCount: undefined,
    maxLevel: undefined,
  },
}

function formatStudyTime(seconds?: number): string {
  if (seconds == null) return "--:--"
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  return `${String(hours).padStart(2, "0")}:${String(minutes).padStart(2, "0")}`
}

function formatNumber(value?: number): string {
  return value != null ? String(value) : "-"
}

function formatPercent(value?: number): string {
  return value != null ? `${value}%` : "-%"
}

function buildSubLabel(newCount?: number, reviewCount?: number): string {
  const hasNew = newCount != null
  const hasReview = reviewCount != null

  // 둘 다 없으면 "-"로 단일 표시
  if (!hasNew && !hasReview) {
    return "-"
  }

  const parts: string[] = []
  parts.push(`새 문제 ${hasNew ? newCount : "-"}`)
  parts.push(`복습 문제 ${hasReview ? reviewCount : "-"}`)

  return parts.join(" / ")
}

export function TodayStudyInfoSection({ isLoading, data }: TodayStudyInfoSectionProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <h2 className="text-base font-bold text-gray-900">오늘의 학습 정보</h2>
        <div className="grid grid-cols-2 gap-3">
          <Skeleton className="h-20 rounded-2xl" />
          <Skeleton className="h-20 rounded-2xl" />
        </div>
        <Skeleton className="h-64 rounded-2xl" />
      </div>
    )
  }

  const today = data ?? mockTodayStudy

  return (
    <div className="space-y-4">
      <h2 className="text-base font-bold text-gray-900">오늘의 학습 정보</h2>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-3">
        <SummaryStatCard
          icon={<Clock className="w-5 h-5 text-indigo-600" />}
          label="총 학습 시간"
          value={formatStudyTime(today.totalStudyTimeSec)}
        />
        <SummaryStatCard
          icon={<FileText className="w-5 h-5 text-yellow-500" />}
          label="총 학습 문제"
          value={formatNumber(today.totalQuestions)}
        />
      </div>

      {/* Category rows card */}
      <div className="bg-white rounded-2xl shadow-sm px-4 py-1">
        <CategoryRow
          icon={<BookOpen className="w-5 h-5 text-indigo-600" />}
          title="어휘"
          rightLabel={`복습 정답률 ${formatPercent(today.vocab.reviewAccuracyPercent)}`}
          progressPercent={today.vocab.reviewAccuracyPercent ?? 0}
          subLabel={buildSubLabel(today.vocab.newCount, today.vocab.reviewCount)}
        />
        <CategoryRow
          icon={<Languages className="w-5 h-5 text-green-600" />}
          title="문법"
          rightLabel={`복습 정답률 ${formatPercent(today.grammar?.reviewAccuracyPercent)}`}
          progressPercent={today.grammar?.reviewAccuracyPercent ?? 0}
          subLabel={buildSubLabel(today.grammar?.newCount, today.grammar?.reviewCount)}
        />
        <CategoryRow
          icon={<MessageSquare className="w-5 h-5 text-purple-600" />}
          title="표현"
          rightLabel={`복습 정답률 ${formatPercent(today.expression?.reviewAccuracyPercent)}`}
          progressPercent={today.expression?.reviewAccuracyPercent ?? 0}
          subLabel={buildSubLabel(today.expression?.newCount, today.expression?.reviewCount)}
        />
        <CategoryRow
          icon={<Headphones className="w-5 h-5 text-blue-600" />}
          title="리스닝"
          rightLabel={`최고 레벨 ${today.listening?.maxLevel != null ? today.listening.maxLevel : "-"}`}
          progressPercent={0}
          subLabel={`문제 ${formatNumber(today.listening?.questionCount)}`}
        />
      </div>
    </div>
  )
}
