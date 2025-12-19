"use client"

export type PeriodValue = "week" | "month" | "year" | "all"

interface PeriodSegmentProps {
  value: PeriodValue
  onChange: (value: PeriodValue) => void
  className?: string
}

const PERIOD_LABELS: Record<PeriodValue, string> = {
  week: "주",
  month: "월",
  year: "년",
  all: "전체",
}

export function PeriodSegment({ value, onChange, className = "" }: PeriodSegmentProps) {
  const periods: PeriodValue[] = ["week", "month", "year", "all"]

  return (
    <div className={`inline-flex rounded-full bg-gray-100 p-1 text-xs ${className}`}>
      {periods.map((period) => (
        <button
          key={period}
          onClick={() => onChange(period)}
          className={`px-3 py-1 rounded-full transition-all ${
            value === period ? "bg-white text-indigo-600 font-semibold shadow-sm" : "text-gray-500 hover:text-gray-700"
          }`}
        >
          {PERIOD_LABELS[period]}
        </button>
      ))}
    </div>
  )
}

export function getPrefix(period: PeriodValue): string {
  switch (period) {
    case "week":
      return "최근 한 주, 하루 평균"
    case "month":
      return "최근 한 달, 하루 평균"
    case "year":
      return "최근 일 년, 하루 평균"
    case "all":
      return "지금까지, 하루 평균"
  }
}

export function getDateRange(period: PeriodValue): { start: string; end: string } {
  const today = new Date()
  const end = `${today.getFullYear()}.${String(today.getMonth() + 1).padStart(2, "0")}.${String(today.getDate()).padStart(2, "0")}`

  let startDate: Date
  switch (period) {
    case "week":
      startDate = new Date(today)
      startDate.setDate(today.getDate() - 6)
      break
    case "month":
      startDate = new Date(today)
      startDate.setDate(today.getDate() - 29)
      break
    case "year":
      startDate = new Date(today)
      startDate.setFullYear(today.getFullYear() - 1)
      startDate.setDate(startDate.getDate() + 1)
      break
    case "all":
      startDate = new Date(today)
      startDate.setDate(today.getDate() - 6)
      break
  }

  const start = `${startDate.getFullYear()}.${String(startDate.getMonth() + 1).padStart(2, "0")}.${String(startDate.getDate()).padStart(2, "0")}`
  return { start, end }
}
