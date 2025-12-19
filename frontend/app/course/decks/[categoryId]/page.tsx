"use client"

import { useRouter } from "next/navigation"
import { ChevronLeft, ChevronRight, Check, Minus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { useCourseStore } from "@/store/course-store"
import { getCategoryById } from "@/lib/mock-decks"

export default function CategoryDetailPage({ params }: { params: { categoryId: string } }) {
  const { categoryId } = params
  const router = useRouter()
  const { customSelectedDeckIds, setSelectedDeckIds } = useCourseStore()

  const category = getCategoryById(categoryId)

  if (!category) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">카테고리를 찾을 수 없습니다.</p>
      </div>
    )
  }

  const deckIds = category.decks.map((d) => d.id)
  const selectedInCategory = deckIds.filter((id) => customSelectedDeckIds.includes(id))
  const selectedCount = selectedInCategory.length
  const totalCount = category.decks.length
  const isAllSelected = selectedCount === totalCount
  const isNoneSelected = selectedCount === 0
  const isIndeterminate = !isAllSelected && !isNoneSelected

  const handleSelectAll = () => {
    if (isAllSelected) {
      // Deselect all in this category
      setSelectedDeckIds(customSelectedDeckIds.filter((id) => !deckIds.includes(id)))
    } else {
      // Select all in this category
      const newIds = [...new Set([...customSelectedDeckIds, ...deckIds])]
      setSelectedDeckIds(newIds)
    }
  }

  const handleDeckToggle = (deckId: string) => {
    if (customSelectedDeckIds.includes(deckId)) {
      setSelectedDeckIds(customSelectedDeckIds.filter((id) => id !== deckId))
    } else {
      setSelectedDeckIds([...customSelectedDeckIds, deckId])
    }
  }

  const handleBack = () => {
    router.back()
  }

  const handleComplete = () => {
    router.back()
  }

  const isDeckSelected = (deckId: string) => customSelectedDeckIds.includes(deckId)

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-100 px-4 py-3 flex items-center">
        <button onClick={handleBack} className="p-2 -ml-2 text-gray-500">
          <ChevronLeft className="w-6 h-6" />
        </button>
        <span className="text-sm text-gray-500 ml-1">{category.title}</span>
      </div>

      {/* Select All Row */}
      <div className="bg-white border-b border-gray-100 px-4 py-4">
        <button onClick={handleSelectAll} className="flex items-center w-full">
          <div
            className={`w-6 h-6 rounded border-2 flex items-center justify-center mr-3 transition-colors ${
              isAllSelected
                ? "bg-indigo-500 border-indigo-500"
                : isIndeterminate
                  ? "bg-indigo-500 border-indigo-500"
                  : "border-gray-300 bg-white"
            }`}
          >
            {isAllSelected && <Check className="w-4 h-4 text-white" />}
            {isIndeterminate && <Minus className="w-4 h-4 text-white" />}
          </div>
          <span className="font-medium text-gray-900 flex-1 text-left">전체 선택</span>
          <span className="text-sm text-indigo-600 font-medium">
            {selectedCount} / {totalCount}
          </span>
        </button>
      </div>

      {/* Deck List */}
      <div className="flex-1 overflow-y-auto">
        <div className="divide-y divide-gray-100">
          {category.decks.map((deck) => {
            const isSelected = isDeckSelected(deck.id)
            return (
              <div key={deck.id} className="bg-white">
                <div className="flex items-center px-4 py-4">
                  {/* Checkbox */}
                  <button
                    onClick={() => handleDeckToggle(deck.id)}
                    className={`w-6 h-6 rounded border-2 flex items-center justify-center mr-3 transition-colors ${
                      isSelected ? "bg-indigo-500 border-indigo-500" : "border-gray-300 bg-white"
                    }`}
                  >
                    {isSelected && <Check className="w-4 h-4 text-white" />}
                  </button>

                  {/* Deck Icon/Thumbnail */}
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center mr-3">
                    <span className="text-xs font-bold text-indigo-600">{deck.title.slice(0, 2).toUpperCase()}</span>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-gray-900 truncate">{deck.title}</span>
                      <ChevronRight className="w-5 h-5 text-gray-300 flex-shrink-0 ml-2" />
                    </div>
                    <div className="flex items-center gap-4 mt-1">
                      <div className="flex items-center gap-1">
                        <div className="w-16 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-indigo-500 rounded-full"
                            style={{ width: `${deck.progressPercent}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-xs text-gray-500">
                        {deck.learnedWords} / {deck.totalWords.toLocaleString()}
                      </span>
                      <span className="text-xs text-gray-400">{deck.progressPercent}% 학습</span>
                    </div>
                  </div>
                </div>

                {/* Action Text */}
                <div className="px-4 pb-3 -mt-1">
                  <button
                    onClick={() => handleDeckToggle(deck.id)}
                    className={`text-sm font-medium ml-auto block text-right ${
                      isSelected ? "text-red-500" : "text-indigo-600"
                    }`}
                  >
                    {isSelected ? "- 코스에서 제외" : "+ 코스에 추가"}
                  </button>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="p-4 bg-white border-t border-gray-100">
        <div className="flex gap-3">
          <Button
            variant="secondary"
            className="flex-1 py-6 bg-gray-200 hover:bg-gray-300 text-gray-700"
            onClick={handleBack}
          >
            나가기
          </Button>
          <Button className="flex-1 py-6 bg-indigo-600 hover:bg-indigo-700" onClick={handleComplete}>
            선택 완료
          </Button>
        </div>
      </div>
    </div>
  )
}
