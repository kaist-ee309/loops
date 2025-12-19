"use client"

import { PeriodSegment, type PeriodValue, getPrefix, getDateRange } from "./period-segment"

type StudyTimePoint = {
  label: string
  minutes: number
}

const studyTimeMock: Record<PeriodValue, StudyTimePoint[]> = {
  week: [
    { label: "월", minutes: 3 },
    { label: "화", minutes: 5 },
    { label: "수", minutes: 2 },
    { label: "목", minutes: 8 },
    { label: "금", minutes: 4 },
    { label: "토", minutes: 12 },
    { label: "일", minutes: 6 },
  ],
  month: Array.from({ length: 30 }, (_, i) => ({
    label: String(i + 1),
    minutes: Math.floor(Math.random() * 15) + 1,
  })),
  year: [
    { label: "1월", minutes: 120 },
    { label: "2월", minutes: 95 },
    { label: "3월", minutes: 150 },
    { label: "4월", minutes: 80 },
    { label: "5월", minutes: 110 },
    { label: "6월", minutes: 130 },
    { label: "7월", minutes: 90 },
    { label: "8월", minutes: 70 },
    { label: "9월", minutes: 140 },
    { label: "10월", minutes: 160 },
    { label: "11월", minutes: 100 },
    { label: "12월", minutes: 180 },
  ],
  all: [
    { label: "2023", minutes: 800 },
    { label: "2024-Q1", minutes: 400 },
    { label: "2024-Q2", minutes: 350 },
    { label: "2024-Q3", minutes: 420 },
    { label: "2024-Q4", minutes: 380 },
    { label: "2025", minutes: 200 },
  ],
}

interface StudyTimeCardProps {
  period: PeriodValue
  onPeriodChange: (value: PeriodValue) => void
}

function formatMinutes(minutes: number): string {
  if (minutes <= 0) return "--:--"
  const h = Math.floor(minutes / 60)
  const m = minutes % 60
  if (h > 0) {
    return `${h}시간 ${m}분`
  }
  return `${m}분`
}

export function StudyTimeCard({ period, onPeriodChange }: StudyTimeCardProps) {
  const data = studyTimeMock[period] ?? []
  const totalMinutes = data.reduce((sum, p) => sum + p.minutes, 0)
  const dayCount = data.length || 1
  const avgMinutes = Math.round(totalMinutes / dayCount)
  const maxMinutes = data.reduce((max, d) => (Number.isFinite(d.minutes) ? Math.max(max, d.minutes) : max), 0)
  const { start, end } = getDateRange(period)
  const chartWidth = 100
  const chartHeight = 100
  const hasValidMax = Number.isFinite(maxMinutes) && maxMinutes > 0

  const points =
    data.length === 0
      ? "0.00,100.00"
      : data
          .map((point, index) => {
            const n = data.length
            const rawX = n === 1 ? 0 : (index / (n - 1)) * chartWidth
            const safeX = Number.isFinite(rawX) ? rawX : 0
            const value = Number.isFinite(point.minutes) ? point.minutes : 0
            const ratio = hasValidMax ? value / maxMinutes : 0
            const safeRatio = Number.isFinite(ratio) ? Math.min(Math.max(ratio, 0), 1) : 0
            const rawY = chartHeight - safeRatio * chartHeight
            const safeY = Number.isFinite(rawY) ? rawY : chartHeight

            return `${safeX.toFixed(2)},${safeY.toFixed(2)}`
          })
          .join(" ")

  return (
    <div className="bg-white rounded-2xl shadow-sm px-4 py-3 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <PeriodSegment value={period} onChange={onPeriodChange} />
      </div>

      {/* Title and Description */}
      <div>
        <h3 className="text-sm font-semibold text-gray-900">학습 시간</h3>
        <p className="text-sm text-gray-600 mt-1">
          {getPrefix(period)} 학습 시간은{" "}
          <span className="text-indigo-600 font-semibold">{formatMinutes(avgMinutes)}</span>
          예요.
        </p>
      </div>

      {/* Line Chart */}
      <div className="relative h-24 border border-gray-200 rounded-lg p-2">
        {/* Grid lines */}
        <div className="absolute inset-2 flex flex-col justify-between">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="border-b border-gray-100" />
          ))}
        </div>

        {/* Line */}
        <svg
          className="absolute inset-2 w-[calc(100%-16px)] h-[calc(100%-16px)]"
          viewBox="0 0 100 100"
          preserveAspectRatio="none"
        >
          <polyline fill="none" stroke="#818cf8" strokeWidth="2" vectorEffect="non-scaling-stroke" points={points} />
        </svg>
      </div>

      {/* Date Range */}
      <div className="flex justify-between text-xs text-gray-400">
        <span>{start}</span>
        <span className="text-indigo-600 font-medium">{end}</span>
      </div>
    </div>
  )
}
