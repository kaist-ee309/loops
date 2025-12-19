"use client"

import { useRouter } from "next/navigation"
import { ChevronLeft, HelpCircle, Check } from "lucide-react"
import { useCourseStore } from "@/store/course-store"
import { deriveCounts, clampPercent } from "@/lib/review-ratio"

export default function ReviewRatioPage() {
  const router = useRouter()
  const {
    reviewRatioMode,
    customReviewRatioPercent,
    targetWordCount,
    setReviewRatioMode,
    setCustomReviewRatioPercent,
  } = useCourseStore()

  const { safeTarget, newCount, reviewCount, reviewPercent } = deriveCounts({
    mode: reviewRatioMode,
    targetWordCount,
    customReviewRatioPercent,
  })

  const clampedPercent = clampPercent(customReviewRatioPercent)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b px-4 py-4 flex items-center gap-3">
        <button onClick={() => router.back()} className="p-1">
          <ChevronLeft className="w-6 h-6" />
        </button>
        <h1 className="text-lg font-bold">복습 단어 비율</h1>
      </div>

      <div className="p-4 space-y-6">
        {/* Mode Toggle */}
        <div className="flex bg-gray-100 rounded-full p-1">
          <button
            className={`flex-1 py-2.5 px-4 rounded-full text-sm font-medium transition-colors flex items-center justify-center gap-1.5 ${
              reviewRatioMode === "normal" ? "bg-white text-indigo-600 shadow-sm" : "text-gray-500"
            }`}
            onClick={() => setReviewRatioMode("normal")}
          >
            {reviewRatioMode === "normal" && <Check className="w-4 h-4" />}
            일반 모드
          </button>
          <button
            className={`flex-1 py-2.5 px-4 rounded-full text-sm font-medium transition-colors flex items-center justify-center gap-1.5 ${
              reviewRatioMode === "custom" ? "bg-white text-indigo-600 shadow-sm" : "text-gray-500"
            }`}
            onClick={() => setReviewRatioMode("custom")}
          >
            {reviewRatioMode === "custom" && <Check className="w-4 h-4" />}
            커스텀 모드
          </button>
        </div>

        {/* Donut Chart */}
        <div className="flex justify-center py-8">
          <div className="relative w-48 h-48">
            {/* Donut ring using conic-gradient */}
            <div
              className="absolute inset-0 rounded-full"
              style={{
                background: `conic-gradient(
                  #f97316 0deg ${reviewPercent * 3.6}deg,
                  #e5e7eb ${reviewPercent * 3.6}deg 360deg
                )`,
              }}
            />
            {/* Inner white circle */}
            <div className="absolute inset-4 bg-white rounded-full flex flex-col items-center justify-center">
              <div className="text-sm text-gray-600 space-y-1 text-center">
                <p>
                  새로운 단어 <span className="font-bold text-gray-900">{newCount}</span> 개
                </p>
                <p>
                  복습할 단어 <span className="font-bold text-gray-900">{reviewCount}</span> 개
                </p>
              </div>
              <div className="mt-3 bg-gray-800 text-white text-xs px-3 py-1 rounded">하루 목표량</div>
              <div className="mt-1">
                <span className="text-2xl font-bold text-orange-500">0</span>
                <span className="text-gray-400">/{safeTarget}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Mode-specific content */}
        {reviewRatioMode === "normal" ? (
          /* Normal Mode Content */
          <div className="space-y-4">
            <p className="text-gray-700">
              오늘 복습할 단어가 더 있더라도,{" "}
              <span className="text-indigo-600 font-medium">새로운 단어가 최소 25%</span>는 나와요.
            </p>
            <p className="text-gray-600 text-sm">
              예를 들어, 나의 하루 목표량이 100개라면, 최소 25개는 새로운 단어로 구성돼요.
            </p>
            <p className="text-gray-400 text-xs">* 재도전 어휘는 복습 단어의 비율에 포함돼요.</p>

            {/* FAQ Section */}
            <div className="mt-6 bg-gray-100 rounded-xl p-4">
              <h3 className="font-bold text-gray-800 mb-3">Q. 복습을 못하고 그냥 넘어가면 어떻게 되죠?</h3>
              <ul className="space-y-2 text-sm text-gray-600">
                <li className="flex items-start gap-2">
                  <span className="text-gray-400">·</span>
                  <span>당일 복습하지 못한 단어도 차차 다시 나와요</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-gray-400">·</span>
                  <span>
                    복습 단어는 <span className="text-indigo-600 font-medium">지금 배우면 가장 잘 외워질 단어</span>부터
                    나와요.
                  </span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-gray-400">·</span>
                  <span>
                    새로운 단어를 학습하면서 알게 되는 다양한 예문들이 미리지 복습 단어를 다시 봤을 때{" "}
                    <span className="text-indigo-600 font-medium">더 잘 기억</span>할 수 있게
                  </span>
                </li>
              </ul>
            </div>
          </div>
        ) : (
          /* Custom Mode Content */
          <div className="space-y-4">
            {/* Custom ratio option */}
            <div className="bg-white rounded-xl border-2 border-indigo-500 p-4 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded-full bg-indigo-600 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-white" />
                  </div>
                  <span className="font-medium">복습 비율 직접 정하기</span>
                </div>
                <button className="p-1">
                  <HelpCircle className="w-5 h-5 text-gray-400" />
                </button>
              </div>

              {/* Slider with tooltip */}
              <div className="relative pt-6 pb-2">
                <div
                  className="absolute -top-1 transform -translate-x-1/2 bg-gray-800 text-white text-sm px-2 py-1 rounded"
                  style={{ left: `${clampedPercent}%` }}
                >
                  {customReviewRatioPercent}%
                </div>

                {/* Slider track */}
                <div className="relative h-3 bg-gray-200 rounded-full">
                  <div
                    className="absolute h-full bg-green-500 rounded-full"
                    style={{ width: `${customReviewRatioPercent}%` }}
                  />
                  {/* Slider thumb */}
                  <input
                    type="range"
                    min="0"
                    max="100"
                    step="5"
                    value={customReviewRatioPercent}
                    onChange={(e) => setCustomReviewRatioPercent(Number(e.target.value))}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                  />
                  <div
                    className="absolute top-1/2 -translate-y-1/2 w-6 h-6 bg-white border-2 border-green-500 rounded-full shadow-md flex items-center justify-center pointer-events-none"
                    style={{ left: `clamp(12px, calc(${customReviewRatioPercent}% - 12px), calc(100% - 12px))` }}
                  >
                    <div className="text-green-500 text-xs">≈</div>
                  </div>
                </div>

                {/* Labels */}
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                  <span>복습할 단어</span>
                  <span>새 단어</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
