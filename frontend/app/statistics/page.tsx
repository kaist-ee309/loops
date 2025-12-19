"use client"

import { useEffect, useMemo, useRef, useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft, TrendingUp, AlertCircle, ChevronLeft, ChevronRight } from "lucide-react"
import { BottomTabNav } from "@/components/bottom-tab-nav"
import { AuthRequired } from "@/components/auth-required"
import { TodayStudyInfoSection } from "@/components/stats/today-study-info-section"
import type { PeriodValue } from "@/components/stats/period-segment"
import { StudyTimeCard } from "@/components/stats/study-time-card"
import { StudyVolumeCard } from "@/components/stats/study-volume-card"
import { getTodayProgress, type TodayProgressRead } from "@/lib/api/profile"
import {
  getStatsAccuracy,
  getStatsHistory,
  getTotalLearned,
  type StatsAccuracyRead,
  type StatsHistoryPeriod,
  type StatsHistoryRead,
  type TotalLearnedRead,
} from "@/lib/api/stats"
import { getStudyOverview, type StudyOverviewResponse } from "@/lib/api/study"
import { toast } from "@/components/ui/use-toast"

const fallbackTodayProgress: TodayProgressRead = {
  total_reviews: 0,
  correct_count: 0,
  wrong_count: 0,
  accuracy_rate: 0,
  daily_goal: 0,
  goal_progress: 0,
}

const fallbackTotalLearned: TotalLearnedRead = {
  total_learned: 0,
  by_level: {},
  total_study_time_minutes: 0,
}

const fallbackStatsAccuracy: StatsAccuracyRead = {
  overall_accuracy: 0,
  total_reviews: 0,
  total_correct: 0,
  by_period: {},
  by_cefr_level: {},
  trend: "stable",
}

const fallbackStatsHistory = (period: StatsHistoryPeriod): StatsHistoryRead => ({
  period,
  data: [],
})

const fallbackStudyOverview: StudyOverviewResponse = {
  new_cards_count: 0,
  review_cards_count: 0,
  total_available: 0,
  due_cards: [],
}

function toSafeNumber(value: number | null | undefined, fallback = 0) {
  return Number.isFinite(value) ? (value as number) : fallback
}

function formatTimeFromMinutes(minutes: number) {
  const safeMinutes = Math.max(0, toSafeNumber(minutes))
  const hours = Math.floor(safeMinutes / 60)
  const mins = safeMinutes % 60
  if (hours === 0) return `${mins}m`
  return `${hours}h ${mins}m`
}

function mapPeriod(value: PeriodValue): StatsHistoryPeriod {
  if (value === "week") return "7d"
  if (value === "month") return "30d"
  if (value === "year") return "1y"
  return "90d"
}

function buildHistoryPoints(history: StatsHistoryRead) {
  return (history.data ?? [])
    .map((item) => {
      const dateObj = new Date(item.date)
      const label =
        Number.isNaN(dateObj.getTime()) || !item.date
          ? item.date
          : `${String(dateObj.getMonth() + 1).padStart(2, "0")}/${String(dateObj.getDate()).padStart(2, "0")}`
      return {
        label: label || "-",
        value: Math.max(0, toSafeNumber(item.cards_studied)),
        date: item.date,
      }
    })
    .filter((item) => item.date)
}

function buildEmptyWeekData(): { day: string; count: number; date: string }[] {
  const today = new Date()
  const dayNames = ["일", "월", "화", "수", "목", "금", "토"]
  const data = []

  for (let i = 6; i >= 0; i--) {
    const date = new Date(today)
    date.setDate(today.getDate() - i)
    const dateStr = `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, "0")}.${String(date.getDate()).padStart(2, "0")}`

    data.push({
      day: i === 0 ? "오늘" : dayNames[date.getDay()],
      count: 0,
      date: dateStr,
    })
  }
  return data
}

function toYmd(date: Date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, "0")
  const day = String(date.getDate()).padStart(2, "0")
  return `${year}-${month}-${day}`
}

function buildLastNDaysSkeleton(n = 7) {
  const skeleton = []
  const dayNames = ["일", "월", "화", "수", "목", "금", "토"]
  for (let i = n - 1; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const ymd = toYmd(date)
    const dayLabel = i === 0 ? "오늘" : dayNames[date.getDay()]
    const displayDate = `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, "0")}.${String(date.getDate()).padStart(2, "0")}`
    skeleton.push({ ymd, dayLabel, displayDate })
  }
  return skeleton
}

function safeYmd(dateStr?: string | null): string | null {
  if (!dateStr) return null
  const head = dateStr.slice(0, 10)
  if (/^\d{4}-\d{2}-\d{2}$/.test(head)) {
    return head
  }
  const parsed = new Date(dateStr)
  if (Number.isNaN(parsed.getTime())) return null
  return toYmd(parsed)
}

function normalizeYmd(dateStr?: string | null) {
  return safeYmd(dateStr)
}

function buildHeatmapLevels(history: StatsHistoryRead) {
  const map = new Map<string, number>()
  ;(history.data ?? []).forEach((item) => {
    const ymd = normalizeYmd(item.date)
    if (ymd) {
      map.set(ymd, Math.max(0, toSafeNumber(item.cards_studied)))
    }
  })

  const days: { ymd: string; count: number }[] = []
  for (let i = 364; i >= 0; i--) {
    const date = new Date()
    date.setDate(date.getDate() - i)
    const ymd = toYmd(date)
    days.push({ ymd, count: map.get(ymd) ?? 0 })
  }

  const maxCount = days.reduce((max, d) => Math.max(max, d.count), 0)
  const levelFor = (count: number) => {
    if (maxCount <= 0 || count <= 0) return 0
    return Math.min(4, Math.max(1, Math.ceil((count / maxCount) * 4)))
  }

  const weeks: number[][] = []
  let currentWeek: number[] = new Array(7).fill(0)
  let prevIdx = 0
  let isFirst = true

  days.forEach(({ ymd, count }) => {
    const parts = ymd.split("-").map((p) => Number(p))
    const dateObj = new Date(parts[0], parts[1] - 1, parts[2])
    const dayIdx = (dateObj.getDay() + 6) % 7 // Monday=0 ... Sunday=6
    if (!isFirst && dayIdx < prevIdx) {
      weeks.push(currentWeek)
      currentWeek = new Array(7).fill(0)
    }
    currentWeek[dayIdx] = levelFor(count)
    prevIdx = dayIdx
    isFirst = false
  })

  weeks.push(currentWeek)

  const last52 = weeks.slice(-52)
  if (last52.length < 52) {
    const missing = 52 - last52.length
    const padding = Array.from({ length: missing }, () => new Array(7).fill(0))
    return [...padding, ...last52]
  }
  return last52
}

function formatDueDate(dateStr?: string | null) {
  const ymd = safeYmd(dateStr)
  if (!ymd) return "-"
  const [y, m, d] = ymd.split("-")
  return `${y}.${m}.${d}`
}

export default function StatisticsPage() {
  const router = useRouter()
  const [selectedDayIndex, setSelectedDayIndex] = useState<number | null>(null)
  const [activeTab, setActiveTab] = useState<"period" | "study" | "vocab">("period")
  const [studyTimePeriod, setStudyTimePeriod] = useState<PeriodValue>("week")
  const [studyVolumePeriod, setStudyVolumePeriod] = useState<PeriodValue>("week")
  const [todayProgress, setTodayProgress] = useState<TodayProgressRead>(fallbackTodayProgress)
  const [totalLearned, setTotalLearned] = useState<TotalLearnedRead>(fallbackTotalLearned)
  const [statsAccuracy, setStatsAccuracy] = useState<StatsAccuracyRead>(fallbackStatsAccuracy)
  const [statsHistory, setStatsHistory] = useState<StatsHistoryRead>(fallbackStatsHistory(mapPeriod("week")))
  const [heatmapHistory, setHeatmapHistory] = useState<StatsHistoryRead>(fallbackStatsHistory("1y"))
  const [studyOverview, setStudyOverview] = useState<StudyOverviewResponse>(fallbackStudyOverview)
  const [isLoading, setIsLoading] = useState(true)
  const errorToastShownRef = useRef(false)

  const historyPoints = useMemo(() => {
    const mapped = buildHistoryPoints(statsHistory)
    return mapped.length > 0 ? mapped : []
  }, [statsHistory])

  const weeklyData = useMemo(() => {
    if (!statsHistory?.data || statsHistory.data.length === 0) return buildEmptyWeekData()

    const skeleton = buildLastNDaysSkeleton(7)
    const valueMap = new Map<string, number>()

    statsHistory.data.forEach((item) => {
      const ymd = normalizeYmd(item.date)
      if (ymd) {
        valueMap.set(ymd, Math.max(0, toSafeNumber(item.cards_studied)))
      }
    })

    const dayNames = ["일", "월", "화", "수", "목", "금", "토"]

    return skeleton.map(({ ymd, dayLabel, displayDate }) => ({
      day: dayLabel || dayNames[0],
      count: valueMap.get(ymd) ?? 0,
      date: displayDate,
    }))
  }, [statsHistory])

  useEffect(() => {
    let isMounted = true

    ;(async () => {
      const [todayRes, totalRes, accuracyRes, overviewRes, heatmapRes] = await Promise.allSettled([
        getTodayProgress(),
        getTotalLearned(),
        getStatsAccuracy(),
        getStudyOverview(50),
        getStatsHistory("1y"),
      ])

      if (!isMounted) return

      const hasError =
        todayRes.status === "rejected" ||
        totalRes.status === "rejected" ||
        accuracyRes.status === "rejected" ||
        overviewRes.status === "rejected" ||
        heatmapRes.status === "rejected"

      if (todayRes.status === "fulfilled") {
        setTodayProgress(todayRes.value)
      } else {
        console.debug("[statistics] today-progress failed", todayRes.reason)
        setTodayProgress(fallbackTodayProgress)
      }

      if (totalRes.status === "fulfilled") {
        setTotalLearned(totalRes.value)
      } else {
        console.debug("[statistics] total-learned failed", totalRes.reason)
        setTotalLearned(fallbackTotalLearned)
      }

      if (accuracyRes.status === "fulfilled") {
        setStatsAccuracy(accuracyRes.value)
      } else {
        console.debug("[statistics] stats accuracy failed", accuracyRes.reason)
        setStatsAccuracy(fallbackStatsAccuracy)
      }

      if (overviewRes.status === "fulfilled") {
        setStudyOverview(overviewRes.value)
      } else {
        console.debug("[statistics] study overview failed", overviewRes.reason)
        setStudyOverview(fallbackStudyOverview)
      }

      if (heatmapRes.status === "fulfilled") {
        setHeatmapHistory(heatmapRes.value)
      } else {
        console.debug("[statistics] stats history 1y failed", heatmapRes.reason)
        setHeatmapHistory(fallbackStatsHistory("1y"))
      }

      if (hasError && !errorToastShownRef.current) {
        errorToastShownRef.current = true
        toast({
          title: "일부 데이터 로딩 실패",
          description: "일부 학습 정보를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.",
        })
      }

      setIsLoading(false)
    })()

    return () => {
      isMounted = false
    }
  }, [])

  useEffect(() => {
    let isMounted = true
    const period = mapPeriod(studyVolumePeriod)
    setStatsHistory(fallbackStatsHistory(period))

    ;(async () => {
      try {
        const res = await getStatsHistory(period)
        if (!isMounted) return
        setStatsHistory(res)
      } catch (err) {
        if (!isMounted) return
        console.debug("[statistics] stats history failed", err)
        setStatsHistory(fallbackStatsHistory(period))
        if (!errorToastShownRef.current) {
          errorToastShownRef.current = true
          toast({
            title: "일부 데이터 로딩 실패",
            description: "일부 학습 정보를 불러오지 못했습니다. 잠시 후 다시 시도해주세요.",
          })
        }
      } finally {
        // no-op
      }
    })()

    return () => {
      isMounted = false
    }
  }, [studyVolumePeriod])

  const studyVolumeData = useMemo(() => {
    if (historyPoints.length === 0) {
      return [{ label: "-", value: 0, date: "-" }]
    }
    return historyPoints
  }, [historyPoints])

  const heatmapWeeks = useMemo(() => buildHeatmapLevels(heatmapHistory), [heatmapHistory])
  const heatmapFirstHalf = heatmapWeeks.slice(0, 26)
  const heatmapSecondHalf = heatmapWeeks.slice(26, 52)

  const weeklyMaxCount = Math.max(...weeklyData.map((d) => d.count), 1)
  const totalLearnedCount = Math.max(0, toSafeNumber(totalLearned.total_learned))
  const totalStudyTimeLabel = formatTimeFromMinutes(totalLearned.total_study_time_minutes)
  const accuracyPercent = Math.max(0, Math.round(toSafeNumber(statsAccuracy.overall_accuracy)))
  const todayStudyTimeMinutes = Math.max(
    0,
    toSafeNumber((todayProgress as { today_study_time_minutes?: number } | undefined)?.today_study_time_minutes),
  )

  const todayInfoData = useMemo(
    () => ({
      totalStudyTimeSec: todayStudyTimeMinutes * 60,
      totalQuestions: Math.max(0, toSafeNumber(todayProgress.total_reviews)),
      vocab: {
        reviewAccuracyPercent: Math.max(0, Math.round(toSafeNumber(todayProgress.accuracy_rate))),
        newCount: 0,
        reviewCount: Math.max(0, toSafeNumber(todayProgress.total_reviews)),
      },
      grammar: {},
      expression: {},
      listening: {},
    }),
    [todayProgress, todayStudyTimeMinutes],
  )

  const dueCards = useMemo(() => (studyOverview.due_cards ?? []).slice(0, 10), [studyOverview])

  const months = ["DEC", "JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV"]
  const daysOfWeek = ["월", "화", "수", "목", "금", "토", "일"]
  const heatmapColors = ["bg-gray-100", "bg-indigo-100", "bg-indigo-200", "bg-indigo-400", "bg-indigo-600"]

  const handleDayClick = (index: number) => {
    if (selectedDayIndex === index) {
      setSelectedDayIndex(null)
    } else {
      setSelectedDayIndex(index)
    }
  }

  return (
    <AuthRequired>
      <div className="min-h-screen bg-gray-50 pb-20">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
            <ArrowLeft className="w-5 h-5 text-gray-700" />
          </Button>
          <h1 className="text-xl font-bold text-gray-900">학습 통계</h1>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white border-b border-gray-200 px-4">
          <div className="flex gap-6">
            <button
              className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "period" ? "border-gray-900 text-gray-900" : "border-transparent text-gray-500"
              }`}
              onClick={() => setActiveTab("period")}
            >
              기간별
            </button>
            <button
              className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "study" ? "border-gray-900 text-gray-900" : "border-transparent text-gray-500"
              }`}
              onClick={() => setActiveTab("study")}
            >
              학습별
            </button>
            <button
              className={`py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === "vocab" ? "border-gray-900 text-gray-900" : "border-transparent text-gray-500"
              }`}
              onClick={() => setActiveTab("vocab")}
            >
              어휘력
            </button>
          </div>
        </div>

        <div className="p-4 space-y-6">
          {/* Today Study Info Section */}
          {activeTab === "period" && <TodayStudyInfoSection isLoading={isLoading} data={todayInfoData} />}

          {/* Period Tab Content */}
          {activeTab === "period" && (
            <>
              {/* 기간별 학습 정보 title */}
              <h2 className="text-base font-bold text-gray-900">기간별 학습 정보</h2>

              <StudyTimeCard period={studyTimePeriod} onPeriodChange={setStudyTimePeriod} />
              <StudyVolumeCard period={studyVolumePeriod} onPeriodChange={setStudyVolumePeriod} dataOverride={studyVolumeData} />

              {/* Weekly Stats */}
              <div className="bg-white rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="w-5 h-5 text-indigo-600" />
                    <h2 className="font-bold text-lg text-gray-900">주간 학습량</h2>
                  </div>
                  <span className="text-sm text-gray-500">이번 주</span>
                </div>

                <div className="flex items-end justify-between h-48 gap-3">
                  {weeklyData.map((data, index) => (
                    <div
                      key={index}
                      className="flex-1 flex flex-col items-center cursor-pointer"
                      onClick={() => handleDayClick(index)}
                    >
                      <div className="relative flex-1 w-full flex flex-col items-center justify-end">
                        {selectedDayIndex === index && (
                          <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 -translate-y-full bg-white border border-gray-200 rounded-lg px-2 py-1 shadow-md z-10 whitespace-nowrap">
                            <div className="text-[11px] font-bold text-gray-900">{data.date}</div>
                            <div className="text-[10px] text-gray-600">{data.count}문제</div>
                            <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 translate-y-full">
                              <div className="w-2 h-2 bg-white border-r border-b border-gray-200 transform rotate-45 -translate-y-1" />
                            </div>
                          </div>
                        )}
                        <div className="w-full bg-gray-100 rounded-t-lg relative h-[100px] flex items-end">
                          <div
                            className={`w-full rounded-t-lg transition-all ${
                              selectedDayIndex === index ? "bg-indigo-600" : "bg-indigo-400"
                            }`}
                            style={{ height: `${weeklyMaxCount > 0 ? (data.count / weeklyMaxCount) * 100 : 0}%` }}
                          />
                        </div>
                      </div>
                      <span
                        className={`text-xs font-medium mt-2 ${
                          selectedDayIndex === index ? "text-indigo-600" : "text-gray-600"
                        }`}
                      >
                        {data.day}
                      </span>
                    </div>
                  ))}
                </div>

                <div className="pt-4 border-t border-gray-100 grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{totalLearnedCount}</div>
                    <div className="text-xs text-gray-500">총 단어</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-indigo-600">{accuracyPercent}%</div>
                    <div className="text-xs text-gray-500">정답률</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-900">{totalStudyTimeLabel}</div>
                    <div className="text-xs text-gray-500">학습 시간</div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-2xl p-6 space-y-4">
                <div className="flex items-center justify-between">
                  <h2 className="font-bold text-lg text-gray-900">연간 학습</h2>
                  <div className="flex items-center gap-2">
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <ChevronLeft className="w-4 h-4 text-gray-400" />
                    </Button>
                    <span className="text-sm text-gray-600">최근</span>
                    <Button variant="ghost" size="icon" className="h-8 w-8">
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    </Button>
                  </div>
                </div>

                <div className="flex items-center gap-1 text-[9px] text-gray-500">
                  <span>Less</span>
                  {heatmapColors.map((color, i) => (
                    <div key={i} className={`w-2 h-2 rounded-[2px] ${color}`} />
                  ))}
                  <span>More</span>
                </div>

                <div>
                <div className="flex text-[10px] text-gray-400 ml-8">
                  {months.slice(0, 6).map((month) => (
                    <div key={month} className="flex-1 text-center">
                      {month}
                    </div>
                  ))}
                </div>

                <div className="mt-1 space-y-[2px]">
                  {daysOfWeek.map((day, dayIndex) => (
                    <div key={day} className="flex items-center gap-2">
                      <span className="text-[10px] leading-none text-gray-400 w-6 flex-shrink-0">{day}</span>

                      <div className="flex gap-[2px] flex-1">
                        {heatmapFirstHalf.map((week, weekIndex) => (
                          <div
                            key={weekIndex}
                            className={`flex-1 aspect-square rounded-[3px] ${heatmapColors[week[dayIndex]]}`}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div>
                <div className="flex text-[10px] text-gray-400 ml-8">
                  {months.slice(6, 12).map((month) => (
                    <div key={month} className="flex-1 text-center">
                      {month}
                    </div>
                  ))}
                </div>

                <div className="mt-1 space-y-[2px]">
                  {daysOfWeek.map((day, dayIndex) => (
                    <div key={day} className="flex items-center gap-2">
                      <span className="text-[10px] leading-none text-gray-400 w-6 flex-shrink-0">{day}</span>

                      <div className="flex gap-[2px] flex-1">
                        {heatmapSecondHalf.map((week, weekIndex) => (
                          <div
                            key={weekIndex}
                            className={`flex-1 aspect-square rounded-[3px] ${heatmapColors[week[dayIndex]]}`}
                          />
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

              <div className="bg-white rounded-2xl p-6 space-y-4">
                <div className="flex items-center gap-2">
                  <AlertCircle className="w-5 h-5 text-orange-600" />
                  <h2 className="font-bold text-lg text-gray-900">오늘 복습 예정 TOP10</h2>
                </div>

                <div className="space-y-3">
                  {dueCards.length === 0 ? (
                    <div className="text-sm text-gray-500 text-center py-2">표시할 복습 카드가 없습니다.</div>
                  ) : (
                    dueCards.map((card, index) => (
                      <div key={`${card.english_word}-${index}`} className="flex items-center gap-3">
                        <div className="w-6 h-6 rounded-full bg-orange-100 text-orange-600 flex items-center justify-center text-xs font-bold">
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{card.english_word}</div>
                          <div className="text-xs text-gray-500">{card.korean_meaning}</div>
                          <div className="flex items-center gap-2 mt-1 text-[11px] text-gray-500">
                            <span>{formatDueDate(card.next_review_date)}</span>
                            {card.card_state ? <span className="text-gray-400">· {card.card_state}</span> : null}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>

                <Button
                  variant="outline"
                  className="w-full bg-transparent"
                  onClick={() => {
                    console.debug("[statistics] 집중 복습 CTA clicked")
                  }}
                >
                  취약 단어만 집중 복습
                </Button>
              </div>
            </>
          )}

          {/* Study Tab Content */}
          {activeTab === "study" && (
            <div className="bg-white rounded-2xl p-6 text-center text-gray-500">학습별 통계 (준비 중)</div>
          )}

          {/* Vocab Tab Content */}
          {activeTab === "vocab" && (
            <div className="bg-white rounded-2xl p-6 text-center text-gray-500">어휘력 통계 (준비 중)</div>
          )}
        </div>

        <BottomTabNav />
      </div>
    </AuthRequired>
  )
}
