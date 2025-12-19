"use client"

import { useState } from "react"
import { PeriodSegment, type PeriodValue, getPrefix, getDateRange } from "./period-segment"

type StudyVolumePoint = {
  label: string
  value: number
  date?: string
}

const generateWeekData = (): StudyVolumePoint[] => {
  const today = new Date()
  const dayNames = ["일", "월", "화", "수", "목", "금", "토"]
  const data: StudyVolumePoint[] = []

  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    const dateStr = `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, "0")}.${String(date.getDate()).padStart(2, "0")}`

    data.push({
      label: i === 0 ? "오늘" : dayNames[date.getDay()],
      value: i === 0 ? 20 : Math.floor(Math.random() * 5),
      date: dateStr,
    })
  }
  return data
}

const studyVolumeMock: Record<PeriodValue, StudyVolumePoint[]> = {
  week: generateWeekData(),
  month: Array.from({ length: 30 }, (_, i) => {
    const date = new Date()
    date.setDate(date.getDate() - (29 - i))
    return {
      label: String(i + 1),
      value: Math.floor(Math.random() * 25),
      date: `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, "0")}.${String(date.getDate()).padStart(2, "0")}`,
    }
  }),
  year: [
    { label: "1월", value: 450, date: "2025.01" },
    { label: "2월", value: 380, date: "2025.02" },
    { label: "3월", value: 520, date: "2025.03" },
    { label: "4월", value: 300, date: "2025.04" },
    { label: "5월", value: 410, date: "2025.05" },
    { label: "6월", value: 480, date: "2025.06" },
    { label: "7월", value: 350, date: "2025.07" },
    { label: "8월", value: 290, date: "2025.08" },
    { label: "9월", value: 500, date: "2025.09" },
    { label: "10월", value: 550, date: "2025.10" },
    { label: "11월", value: 400, date: "2025.11" },
    { label: "12월", value: 600, date: "2025.12" },
  ],
  all: [
    { label: "2023", value: 3500, date: "2023" },
    { label: "2024-Q1", value: 1200, date: "2024 Q1" },
    { label: "2024-Q2", value: 1100, date: "2024 Q2" },
    { label: "2024-Q3", value: 1300, date: "2024 Q3" },
    { label: "2024-Q4", value: 1400, date: "2024 Q4" },
    { label: "2025", value: 800, date: "2025" },
  ],
}

interface StudyVolumeCardProps {
  period: PeriodValue
  onPeriodChange: (value: PeriodValue) => void
  dataOverride?: StudyVolumePoint[]
}

export function StudyVolumeCard({ period, onPeriodChange, dataOverride }: StudyVolumeCardProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null)
  const data = dataOverride ?? studyVolumeMock[period] ?? []
  const totalCount = data.reduce((sum, p) => sum + p.value, 0)
  const dayCount = data.length || 1
  const avgCount = Math.round(totalCount / dayCount)
  const maxValue = Math.max(...data.map((d) => d.value), 1)
  const { start, end } = getDateRange(period)

  // For year/all periods, use dotted vertical line style
  const isLineChart = period === "year" || period === "all"

  return (
    <div className="bg-white rounded-2xl shadow-sm px-4 py-3 space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between">
        <PeriodSegment value={period} onChange={onPeriodChange} />
      </div>

      {/* Title and Description */}
      <div>
        <h3 className="text-sm font-semibold text-gray-900">학습량</h3>
        <p className="text-sm text-gray-600 mt-1">
          {getPrefix(period)} <span className="text-indigo-600 font-semibold">{avgCount}개</span>의 문제를 풀었어요.
        </p>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-3 text-xs">
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-indigo-600" />
          어휘
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-blue-400" />
          문법
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-orange-400" />
          회화 표현
        </span>
        <span className="flex items-center gap-1">
          <span className="w-2 h-2 rounded-full bg-yellow-500" />
          리스닝
        </span>
      </div>

      {/* Chart */}
      <div className="relative h-28">
        {isLineChart ? (
          // Vertical dotted line chart for year/all
          <div className="flex items-end justify-between h-full gap-1">
            {data.map((point, index) => (
              <div
                key={index}
                className="flex-1 flex flex-col items-center relative cursor-pointer"
                onClick={() => setActiveIndex(activeIndex === index ? null : index)}
              >
                {/* Tooltip */}
                {activeIndex === index && (
                  <div className="absolute -top-2 left-1/2 -translate-x-1/2 -translate-y-full bg-white border border-gray-200 rounded-lg px-2 py-1 text-[10px] text-gray-700 shadow-md whitespace-nowrap z-10">
                    {point.date || point.label}
                    <br />
                    {point.value}문제
                  </div>
                )}
                {/* Dotted line */}
                <div
                  className="w-0.5 border-l-2 border-dotted border-gray-300"
                  style={{ height: `${100 - (point.value / maxValue) * 100}%` }}
                />
                {/* Solid bar */}
                <div
                  className={`w-2 rounded-t transition-all ${
                    activeIndex === index ? "bg-indigo-600" : "bg-indigo-400"
                  }`}
                  style={{ height: `${(point.value / maxValue) * 100}%` }}
                />
              </div>
            ))}
          </div>
        ) : (
          // Bar chart for week/month
          <div className="flex items-end justify-between h-full gap-1">
            {data.map((point, index) => (
              <div
                key={index}
                className="flex-1 flex flex-col items-center relative cursor-pointer"
                onClick={() => setActiveIndex(activeIndex === index ? null : index)}
              >
                {/* Tooltip */}
                {activeIndex === index && (
                  <div className="absolute -top-2 left-1/2 -translate-x-1/2 -translate-y-full bg-white border border-gray-200 rounded-lg px-2 py-1 text-[10px] text-gray-700 shadow-md whitespace-nowrap z-10">
                    {point.date || point.label}
                    <br />
                    {point.value}문제
                  </div>
                )}
                <div className="w-full h-full flex items-end justify-center">
                  <div
                    className={`w-full max-w-[20px] rounded-t-lg transition-all ${
                      point.value === 0 ? "bg-gray-200 h-1" : activeIndex === index ? "bg-indigo-600" : "bg-indigo-400"
                    }`}
                    style={{ height: point.value > 0 ? `${(point.value / maxValue) * 100}%` : undefined }}
                  />
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* X-axis labels */}
      {period === "week" && (
        <div className="flex justify-between text-[10px] text-gray-400">
          {data.map((point, index) => (
            <div
              key={index}
              className={`flex-1 text-center ${activeIndex === index ? "text-gray-900 font-medium" : ""}`}
            >
              {point.label}
            </div>
          ))}
        </div>
      )}

      {/* Date Range for month/year/all */}
      {period !== "week" && (
        <div className="flex justify-between text-xs text-gray-400">
          <span>{start}</span>
          <span className="text-indigo-600 font-medium">{end}</span>
        </div>
      )}
    </div>
  )
}
