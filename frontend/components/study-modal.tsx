"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { X, BookOpen, RefreshCw, ChevronDown, ChevronUp, Star, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useCourseStore, type StudyMode } from "@/store/course-store"
import { buildCourseSummary } from "@/lib/course-summary"
import { MOCK_CATEGORIES } from "@/lib/mock-decks"
import { deriveCounts } from "@/lib/review-ratio"
import { cn } from "@/lib/utils"
import { startSession, type SessionStartRequest } from "@/lib/api/study"
import { toast } from "@/components/ui/use-toast"

export type ModalStep = "today" | "extra"

const STUDY_MODE_OPTIONS: { value: StudyMode; label: string }[] = [
  { value: "typing", label: "타이핑" },
  { value: "mcq", label: "객관식" },
  { value: "flip", label: "단어 플립" },
]

interface StudyModalProps {
  isOpen: boolean
  onClose: () => void
  step: ModalStep
  onStepChange: (step: ModalStep) => void
  todayGoal?: number
  todayProgress?: number
  todayNewCount?: number
  todayReviewCount?: number
  todayRetryCount?: number
}

export function StudyModal({
  isOpen,
  onClose,
  step,
  onStepChange,
  todayGoal = 20,
  todayProgress = 15,
  todayNewCount = 5,
  todayReviewCount = 15,
  todayRetryCount = 0,
}: StudyModalProps) {
  const router = useRouter()
  const [isStarting, setIsStarting] = useState(false)
  const {
    courseType,
    customSelectedDeckIds,
    targetWordCount,
    setTargetWordCount,
    reviewRatioMode,
    customReviewRatioPercent,
    studyMode,
    setStudyMode,
  } = useCourseStore()

  if (!isOpen) return null

  let courseLabel: string
  if (courseType === "integrated") {
    courseLabel = "통합 코스"
  } else {
    const { courseDisplayName } = buildCourseSummary({
      categories: MOCK_CATEGORIES,
      selectedDeckIds: customSelectedDeckIds,
    })
    courseLabel = courseDisplayName || "선택한 단어장 없음"
  }

  const {
    newCount: extraNew,
    reviewCount: extraReview,
    reviewPercent: reviewRatioPercent,
  } = deriveCounts({
    mode: reviewRatioMode,
    targetWordCount,
    customReviewRatioPercent,
  })

  const handleChangeCourse = () => {
    router.push("/course/change")
    onClose()
  }

  const handleChangeReviewRatio = () => {
    router.push("/settings/review-ratio")
    onClose()
  }

  const adjustCount = (delta: number) => {
    const newCount = Math.max(5, Math.min(200, targetWordCount + delta))
    setTargetWordCount(newCount)
  }

  const launchSession = async (payload: SessionStartRequest) => {
    if (isStarting) return
    setIsStarting(true)
    try {
      const res = await startSession(payload)
      router.push(`/learn?sessionId=${res.session_id}`)
      onClose()
    } catch (err) {
      console.debug("[StudyModal] startSession failed", err)
      toast({
        title: "학습 세션을 시작하지 못했습니다.",
        description: "잠시 후 다시 시도해주세요.",
      })
    } finally {
      setIsStarting(false)
    }
  }

  const handleStartTodayStudy = () => {
    launchSession({ new_cards_limit: 10, review_cards_limit: 30 })
  }

  const handleStartExtraStudy = () => {
    launchSession({ new_cards_limit: 20, review_cards_limit: 20 })
  }

  const StudyModeSelector = () => (
    <div className="flex rounded-full bg-gray-100 p-1 mb-6">
      {STUDY_MODE_OPTIONS.map((option) => (
        <button
          key={option.value}
          onClick={() => setStudyMode(option.value)}
          className={cn(
            "flex-1 py-2 px-3 text-sm font-medium rounded-full transition-all",
            studyMode === option.value ? "bg-white text-indigo-600 shadow-sm" : "text-gray-500 hover:text-gray-700",
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  )

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal Content */}
      <div className="relative bg-white rounded-t-3xl w-full max-w-md p-6 pb-8 animate-in slide-in-from-bottom duration-300">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-bold text-indigo-600">어휘 학습</h2>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-full">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Study Mode Selector */}
        <StudyModeSelector />

        {/* Course Type */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <div className="text-xs text-gray-400 mb-1">학습 코스</div>
            <div className="font-bold text-gray-900">{courseLabel}</div>
          </div>
          <Button
            variant="outline"
            size="sm"
            className="text-gray-600 border-gray-300 bg-transparent"
            onClick={handleChangeCourse}
          >
            <RefreshCw className="w-3 h-3 mr-1" />
            변경
          </Button>
        </div>

        {step === "today" ? (
          <>
            {/* Today's Study Stats */}
            <div className="flex items-center justify-center gap-8 mb-6">
              {/* Circular Progress */}
              <div className="relative w-32 h-32">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="40" stroke="#E5E7EB" strokeWidth="8" fill="none" />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="#F97316"
                    strokeWidth="8"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${(todayProgress / todayGoal) * 251.2} 251.2`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-4xl">🐥</div>
                </div>
              </div>

              {/* Stats */}
              <div className="space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <span className="text-gray-500">새로운 단어</span>
                  <span className="font-bold">
                    {todayNewCount} <span className="text-gray-400 font-normal">개</span>
                  </span>
                </div>
                <div className="flex justify-between gap-4">
                  <span className="text-gray-500">복습할 단어</span>
                  <span className="font-bold">
                    {todayReviewCount} <span className="text-gray-400 font-normal">개</span>
                  </span>
                </div>
                {todayRetryCount > 0 && (
                  <div className="flex justify-between gap-4">
                    <span className="text-gray-500">재도전 단어</span>
                    <span className="font-bold">
                      {todayRetryCount} <span className="text-gray-400 font-normal">개</span>
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Change Stats Button */}
            <div className="flex justify-center mb-4">
              <Button variant="ghost" size="sm" className="text-gray-400 text-xs">
                <RefreshCw className="w-3 h-3 mr-1" />
                변경
              </Button>
            </div>

            {/* Progress Text */}
            <div className="text-center mb-6">
              <span className="text-3xl font-bold text-orange-500">{todayProgress}</span>
              <span className="text-lg text-gray-400">/{todayGoal}</span>
            </div>

            {/* CTA Buttons */}
            <div className="space-y-3">
              <Button
                className="w-full py-6 bg-indigo-600 hover:bg-indigo-700"
                onClick={handleStartTodayStudy}
                disabled={isStarting}
              >
                <BookOpen className="w-5 h-5 mr-2" />
                오늘의 학습
              </Button>
              <Button variant="ghost" className="w-full text-gray-500" onClick={() => onStepChange("extra")}>
                추가 학습
              </Button>
            </div>
          </>
        ) : (
          <>
            {/* Extra Study Stats */}
            <div className="flex items-center justify-center gap-8 mb-6">
              {/* Circular Progress */}
              <div className="relative w-32 h-32">
                <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="40" stroke="#E5E7EB" strokeWidth="8" fill="none" />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="#F97316"
                    strokeWidth="8"
                    fill="none"
                    strokeLinecap="round"
                    strokeDasharray={`${(todayProgress / (todayProgress + targetWordCount)) * 251.2} 251.2`}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-4xl">🐥</div>
                </div>
              </div>

              {/* Stats - now using deriveCounts values */}
              <div className="space-y-2 text-sm">
                <div className="flex justify-between gap-4">
                  <span className="text-gray-500">새로운 단어</span>
                  <span className="font-bold">
                    {extraNew} <span className="text-gray-400 font-normal">개</span>
                  </span>
                </div>
                <div className="flex justify-between gap-4">
                  <span className="text-gray-500">복습할 단어</span>
                  <span className="font-bold">
                    {extraReview} <span className="text-gray-400 font-normal">개</span>
                  </span>
                </div>
              </div>
            </div>

            {/* Change Stats Button */}
            <div className="flex justify-center mb-4">
              <Button variant="ghost" size="sm" className="text-gray-400 text-xs">
                <RefreshCw className="w-3 h-3 mr-1" />
                변경
              </Button>
            </div>

            {/* Progress Text */}
            <div className="text-center mb-6">
              <span className="text-3xl font-bold text-orange-500">{todayProgress}</span>
              <span className="text-lg text-gray-400">/{todayProgress + targetWordCount}</span>
            </div>

            {/* Review Ratio Row */}
            <button
              className="w-full flex items-center justify-between py-3 px-4 mb-4 bg-gray-50 rounded-xl"
              onClick={handleChangeReviewRatio}
            >
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-500">복습 단어 비율</span>
                <span className="text-sm font-medium">{reviewRatioPercent}%</span>
              </div>
              <ChevronRight className="w-4 h-4 text-gray-400" />
            </button>

            {/* Word Count Adjustment & CTA */}
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2 border rounded-xl px-3 py-2">
                <button onClick={() => adjustCount(-5)} className="p-1 rounded-full hover:bg-gray-100">
                  <ChevronDown className="w-5 h-5 text-indigo-600" />
                </button>
                <span className="font-bold text-indigo-600 w-8 text-center">{targetWordCount}</span>
                <span className="text-gray-400 text-sm">개</span>
                <button onClick={() => adjustCount(5)} className="p-1 rounded-full hover:bg-gray-100">
                  <ChevronUp className="w-5 h-5 text-indigo-600" />
                </button>
              </div>
              <Button
                className="flex-1 py-6 bg-indigo-600 hover:bg-indigo-700"
                onClick={handleStartExtraStudy}
                disabled={isStarting}
              >
                <Star className="w-4 h-4 mr-2" />
                추가 학습
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
