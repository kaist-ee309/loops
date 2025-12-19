"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { ChevronLeft, Check, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useCourseStore, type CourseType } from "@/store/course-store"
import { buildCourseSummary } from "@/lib/course-summary"
import { MOCK_CATEGORIES } from "@/lib/mock-decks"

export default function CourseChangePage() {
  const router = useRouter()
  const { courseType, customSelectedDeckIds, reviewScope, setCourseType } = useCourseStore()

  // Local selection state (committed on "결정")
  const [selectedType, setSelectedType] = useState<CourseType>(courseType)

  useEffect(() => {
    setSelectedType(courseType)
  }, [courseType])

  const { courseDisplayName, selectionSummaryLines } = buildCourseSummary({
    categories: MOCK_CATEGORIES,
    selectedDeckIds: customSelectedDeckIds,
  })

  const hasSelectedDecks = customSelectedDeckIds.length > 0

  const handleConfirm = () => {
    setCourseType(selectedType)
    router.back()
  }

  const handleCancel = () => {
    router.back()
  }

  const handleSelectDecks = () => {
    router.push("/course/decks")
  }

  const reviewScopeLabel = reviewScope === "all_learned" ? "학습한 모든 단어" : "선택한 단어장만"

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-3 flex items-center justify-between">
        <button onClick={handleCancel} className="p-2 -ml-2">
          <ChevronLeft className="w-6 h-6 text-gray-700" />
        </button>
        <h1 className="font-bold text-gray-900">학습 코스 변경</h1>
        <div className="w-10" /> {/* Spacer */}
      </div>

      {/* Content */}
      <div className="flex-1 p-6">
        <h2 className="text-xl font-bold text-gray-900 text-center mb-8">어떤 코스로 학습할까요?</h2>

        <div className="space-y-4">
          {/* 통합 코스 Card */}
          <button
            onClick={() => setSelectedType("integrated")}
            className={`w-full text-left p-5 rounded-2xl border-2 transition-all ${
              selectedType === "integrated"
                ? "border-indigo-500 bg-indigo-50/50"
                : "border-gray-200 bg-white hover:border-gray-300"
            }`}
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="font-bold text-lg text-gray-900">통합 코스</span>
                  <span className="px-2 py-0.5 bg-orange-100 text-orange-600 text-xs font-medium rounded-full">
                    권장
                  </span>
                </div>
                <p className="text-sm text-gray-500">말해보카가 제공하는 모든 어휘 학습</p>
              </div>
              {selectedType === "integrated" && (
                <div className="w-6 h-6 bg-indigo-500 rounded-full flex items-center justify-center">
                  <Check className="w-4 h-4 text-white" />
                </div>
              )}
            </div>
          </button>

          {/* 커스텀 코스 Card */}
          <button
            onClick={() => setSelectedType("custom")}
            className={`w-full text-left p-5 rounded-2xl border-2 transition-all ${
              selectedType === "custom"
                ? "border-indigo-500 bg-indigo-50/50"
                : "border-gray-200 bg-white hover:border-gray-300"
            }`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex-1">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-lg text-gray-900">커스텀 코스</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      handleSelectDecks()
                    }}
                    className="flex items-center gap-1 text-indigo-600 text-sm font-medium hover:underline"
                  >
                    <Plus className="w-4 h-4" />
                    단어장 선택
                  </button>
                </div>
                {hasSelectedDecks ? (
                  <div className="space-y-1">
                    {selectionSummaryLines.map((line, idx) => (
                      <p key={idx} className="text-sm text-gray-500">
                        • {line}
                      </p>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-500">• 선택한 단어장 없음</p>
                )}
              </div>
              {selectedType === "custom" && (
                <div className="w-6 h-6 bg-indigo-500 rounded-full flex items-center justify-center ml-3">
                  <Check className="w-4 h-4 text-white" />
                </div>
              )}
            </div>

            {/* Review Scope */}
            <div className="flex items-center gap-2 mt-3">
              <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">복습 범위</span>
              <span className="text-sm text-gray-600">{reviewScopeLabel}</span>
            </div>
          </button>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="p-6 bg-white border-t border-gray-100">
        <div className="flex gap-3">
          <Button
            variant="secondary"
            className="flex-1 py-6 bg-gray-200 hover:bg-gray-300 text-gray-700"
            onClick={handleCancel}
          >
            취소
          </Button>
          <Button className="flex-1 py-6 bg-indigo-600 hover:bg-indigo-700" onClick={handleConfirm}>
            결정
          </Button>
        </div>
      </div>
    </div>
  )
}
