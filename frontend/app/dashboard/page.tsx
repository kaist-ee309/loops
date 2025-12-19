"use client"

import { useEffect, useRef, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Flame, BookOpen, Clock, Bell, BarChart3 } from "lucide-react"
import { BottomTabNav } from "@/components/bottom-tab-nav"
import { AuthRequired } from "@/components/auth-required"
import { StudyModal, type ModalStep } from "@/components/study-modal"
import { Skeleton } from "@/components/ui/skeleton"
import { getStreak, getTodayProgress, type StreakRead, type TodayProgressRead } from "@/lib/api/profile"
import { getStudyOverview, type StudyOverviewResponse } from "@/lib/api/study"
import { toast } from "@/components/ui/use-toast"
import { UserDisplayName } from "@/components/user-display-name"

export default function DashboardPage() {
  const [isStudyModalOpen, setIsStudyModalOpen] = useState(false)
  const [modalStep, setModalStep] = useState<ModalStep>("today")
  const [todayProgressData, setTodayProgressData] = useState<TodayProgressRead | null>(null)
  const [streak, setStreak] = useState<StreakRead | null>(null)
  const [studyOverview, setStudyOverview] = useState<StudyOverviewResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const errorToastShownRef = useRef(false)

  const toSafeCount = (value: number | undefined | null) =>
    Number.isFinite(value) ? Math.max(0, Math.round(value as number)) : 0

  const toSafePercent = (value: number | undefined | null) => {
    const percent = Number.isFinite(value) ? Math.round(value as number) : 0
    return Number.isFinite(percent) ? Math.max(0, percent) : 0
  }

  useEffect(() => {
    let isMounted = true

    ;(async () => {
      const [todayRes, streakRes, overviewRes] = await Promise.allSettled([
        getTodayProgress(),
        getStreak(),
        getStudyOverview(),
      ])

      if (!isMounted) return

      const hasError =
        todayRes.status === "rejected" || streakRes.status === "rejected" || overviewRes.status === "rejected"

      if (todayRes.status === "fulfilled") {
        setTodayProgressData(todayRes.value)
      } else if (todayRes.status === "rejected") {
        console.debug("[dashboard] today-progress failed", todayRes.reason)
      }

      if (streakRes.status === "fulfilled") {
        setStreak(streakRes.value)
      } else if (streakRes.status === "rejected") {
        console.debug("[dashboard] streak failed", streakRes.reason)
      }

      if (overviewRes.status === "fulfilled") {
        setStudyOverview(overviewRes.value)
      } else if (overviewRes.status === "rejected") {
        console.debug("[dashboard] study overview failed", overviewRes.reason)
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

  const totalReviews = toSafeCount(todayProgressData?.total_reviews)
  const correctCount = toSafeCount(todayProgressData?.correct_count)
  const wrongCount = toSafeCount(todayProgressData?.wrong_count)
  const todayGoal = toSafeCount(todayProgressData?.daily_goal)
  const accuracyPct = toSafePercent(todayProgressData?.accuracy_rate)
  const goalPct = toSafePercent(todayProgressData?.goal_progress)
  const progressPctRaw = todayGoal > 0 ? (totalReviews / todayGoal) * 100 : 0
  const todayProgressPercent = Number.isFinite(progressPctRaw) ? Math.min(Math.max(progressPctRaw, 0), 100) : 0
  const isTodayComplete = goalPct >= 100 || (todayGoal > 0 && totalReviews >= todayGoal)

  const currentStreak = toSafeCount(streak?.current_streak)
  const longestStreak = toSafeCount(streak?.longest_streak)
  const streakMessage = streak?.message ?? "이대로 계속 가보자구요! 🔥"

  const todayNewCount = toSafeCount(studyOverview?.new_cards_count)
  const todayReviewCount = toSafeCount(studyOverview?.review_cards_count)
  const totalAvailable = toSafeCount(studyOverview?.total_available)

  const handleContinueStudy = () => {
    // If today complete, go straight to extra; otherwise start with today
    setModalStep(isTodayComplete ? "extra" : "today")
    setIsStudyModalOpen(true)
  }

  if (isLoading) {
    return (
      <AuthRequired>
        <div className="min-h-screen bg-gray-50 pb-20 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
          <div className="bg-white p-6 pb-8 rounded-b-3xl shadow-sm space-y-6">
            <div className="flex justify-between items-center">
              <div className="space-y-2">
                <Skeleton className="h-6 w-40" />
                <Skeleton className="h-4 w-28" />
              </div>
              <Skeleton className="h-10 w-10 rounded-full" />
            </div>
            <Skeleton className="h-16 w-full rounded-2xl" />
            <div className="grid grid-cols-2 gap-4">
              <Skeleton className="h-20 rounded-2xl" />
              <Skeleton className="h-20 rounded-2xl" />
            </div>
          </div>

          <div className="p-6 space-y-4">
            <Skeleton className="h-6 w-24" />
            <Skeleton className="h-48 rounded-3xl" />
          </div>

          <BottomTabNav />
        </div>
      </AuthRequired>
    )
  }

  return (
    <AuthRequired>
      <div className="min-h-screen bg-gray-50 pb-20 overflow-y-auto [&::-webkit-scrollbar]:hidden [-ms-overflow-style:none] [scrollbar-width:none]">
        {/* Header */}
        <div className="bg-white p-6 pb-8 rounded-b-3xl shadow-sm space-y-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                안녕하세요, <UserDisplayName withSuffix />
              </h1>
              <p className="text-gray-500">오늘도 목표를 향해 달려볼까요?</p>
            </div>
            <Link href="/notifications">
              <Button variant="ghost" size="icon">
                <Bell className="w-5 h-5 text-gray-500" />
              </Button>
            </Link>
          </div>

          {/* Streak Card */}
          <div className="bg-orange-50 border border-orange-100 p-4 rounded-2xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-full text-orange-500">
                <Flame className="w-5 h-5 fill-current" />
              </div>
              <div>
                <div className="font-bold text-orange-900">{currentStreak}일 연속 학습 중</div>
                <div className="text-xs text-orange-600">
                  {streakMessage}
                  {longestStreak > 0 ? ` · 최장 ${longestStreak}일` : ""}
                </div>
              </div>
            </div>
          </div>

          {/* Main Stats */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-white border border-gray-100 p-4 rounded-2xl shadow-sm">
              <div className="text-gray-500 text-xs mb-1">새로 학습</div>
              <div className="text-2xl font-bold text-gray-900">
                {todayNewCount}
                <span className="text-sm font-normal text-gray-400 ml-1">개</span>
              </div>
            </div>
            <div className="bg-white border border-gray-100 p-4 rounded-2xl shadow-sm">
              <div className="text-gray-500 text-xs mb-1">복습 카드</div>
              <div className="text-2xl font-bold text-gray-900">
                {todayReviewCount}
                <span className="text-sm font-normal text-gray-400 ml-1">개</span>
              </div>
            </div>
          </div>
        </div>

        {/* Today's Review Section */}
        <div className="p-6 space-y-4">
          <h2 className="font-bold text-lg text-gray-900">오늘의 학습</h2>

          <div className="bg-white p-6 rounded-3xl shadow-sm border border-gray-100 space-y-6">
            <div className="flex justify-between items-end">
              <div>
                <div className="text-3xl font-bold text-indigo-600">
                  {totalReviews}
                  <span className="text-lg text-gray-400 font-normal">/{todayGoal || "-"}</span>
                </div>
                <div className="text-sm text-gray-500 mt-1">오늘의 목표 달성까지</div>
              </div>
              <div className="text-right">
                <div className="text-sm font-medium text-gray-900">{goalPct}%</div>
                <div className="text-xs text-gray-400">목표 진행률</div>
              </div>
            </div>

            <div className="flex gap-4 text-xs text-gray-500">
              <span>정확도 {accuracyPct}%</span>
              <span>맞힌 문제 {correctCount}개</span>
              <span>틀린 문제 {wrongCount}개</span>
            </div>

            {/* Progress Bar */}
            <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
              <div
                className="h-full bg-indigo-500 rounded-full"
                style={{ width: `${todayProgressPercent}%` }}
              />
            </div>

            <Button className="w-full py-6 text-lg shadow-indigo-200 shadow-lg" onClick={handleContinueStudy}>
              학습 계속하기
            </Button>
          </div>
        </div>

        {/* Weekly Stats Preview */}
        <div className="px-6 space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="font-bold text-lg text-gray-900">주간 리포트</h2>
            <Link href="/statistics">
              <Button variant="ghost" size="sm" className="text-indigo-600">
                <BarChart3 className="w-4 h-4 mr-1" />
                자세히
              </Button>
            </Link>
          </div>
          <div className="bg-white p-4 rounded-2xl border border-gray-100 shadow-sm">
            <div className="flex justify-between items-center mb-4">
              <div className="flex items-center gap-2">
                <Clock className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">목표 진행률</span>
              </div>
              <span className="font-bold">{goalPct}%</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-gray-400" />
                <span className="text-sm text-gray-600">학습 가능 카드</span>
              </div>
              <span className="font-bold">
                {totalAvailable}
                <span className="text-sm font-normal text-gray-400 ml-1">개</span>
              </span>
            </div>
          </div>
        </div>

        {/* Bottom Tab Navigation */}
        <BottomTabNav />

        <StudyModal
          isOpen={isStudyModalOpen}
          onClose={() => setIsStudyModalOpen(false)}
          step={modalStep}
          onStepChange={setModalStep}
          todayGoal={todayGoal}
          todayProgress={totalReviews}
          todayNewCount={todayNewCount}
          todayReviewCount={todayReviewCount}
          todayRetryCount={wrongCount}
        />
      </div>
    </AuthRequired>
  )
}
