"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Check } from "lucide-react"
import { cn } from "@/lib/utils"

const DECK_PRESETS = [
  {
    id: "toefl",
    name: "TOEFL 필수 단어장",
    description: "유학 준비를 위한 3,000개 핵심 단어",
    icon: "🎓",
    wordCount: 3000,
    difficulty: "고급",
  },
  {
    id: "toeic",
    name: "TOEIC 필수 단어장",
    description: "취업/승진을 위한 2,500개 필수 단어",
    icon: "💼",
    wordCount: 2500,
    difficulty: "중급",
  },
  {
    id: "ielts",
    name: "IELTS 필수 단어장",
    description: "이민/유학을 위한 2,800개 핵심 단어",
    icon: "✈️",
    wordCount: 2800,
    difficulty: "고급",
  },
  {
    id: "daily",
    name: "일상 회화 기초",
    description: "생활 필수 1,500개 단어",
    icon: "💬",
    wordCount: 1500,
    difficulty: "초급",
  },
  {
    id: "business",
    name: "비즈니스 영어",
    description: "업무 실무 2,000개 필수 단어",
    icon: "📊",
    wordCount: 2000,
    difficulty: "중급",
  },
  {
    id: "travel",
    name: "여행 영어",
    description: "여행 필수 1,000개 단어",
    icon: "🌎",
    wordCount: 1000,
    difficulty: "초급",
  },
]

export default function DeckSelectionPage() {
  const router = useRouter()
  const [selectedDecks, setSelectedDecks] = useState<string[]>(["daily"])

  const toggleDeck = (deckId: string) => {
    if (selectedDecks.includes(deckId)) {
      if (selectedDecks.length > 1) {
        setSelectedDecks(selectedDecks.filter((id) => id !== deckId))
      }
    } else {
      setSelectedDecks([...selectedDecks, deckId])
    }
  }

  const handleContinue = () => {
    // TODO: Send selected decks to backend
    console.log("[v0] Selected decks:", selectedDecks)
    router.push("/onboarding/complete")
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6 pb-24">
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-2 py-8">
          <h1 className="text-3xl font-bold text-gray-900">어떤 단어를 배우고 싶으세요?</h1>
          <p className="text-gray-500">원하는 단어장을 선택해주세요 (여러 개 가능)</p>
        </div>

        {/* Deck Grid */}
        <div className="grid gap-4">
          {DECK_PRESETS.map((deck) => {
            const isSelected = selectedDecks.includes(deck.id)
            return (
              <button
                key={deck.id}
                onClick={() => toggleDeck(deck.id)}
                className={cn(
                  "relative bg-white border-2 rounded-2xl p-6 text-left transition-all hover:shadow-md",
                  isSelected ? "border-indigo-500 bg-indigo-50" : "border-gray-200",
                )}
              >
                <div className="flex items-start gap-4">
                  <div className="text-4xl">{deck.icon}</div>
                  <div className="flex-1 space-y-2">
                    <div className="flex items-start justify-between">
                      <div>
                        <h3 className="font-bold text-lg text-gray-900">{deck.name}</h3>
                        <p className="text-sm text-gray-500">{deck.description}</p>
                      </div>
                      {isSelected && (
                        <div className="w-6 h-6 bg-indigo-500 rounded-full flex items-center justify-center flex-shrink-0">
                          <Check className="w-4 h-4 text-white" />
                        </div>
                      )}
                    </div>
                    <div className="flex gap-2">
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">
                        {deck.wordCount.toLocaleString()}개 단어
                      </span>
                      <span className="text-xs bg-gray-100 px-2 py-1 rounded-full text-gray-600">
                        {deck.difficulty}
                      </span>
                    </div>
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Fixed Bottom Button */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 p-4 shadow-lg">
        <div className="max-w-2xl mx-auto">
          <Button className="w-full py-6 text-lg" onClick={handleContinue}>
            {selectedDecks.length}개 단어장으로 시작하기
          </Button>
        </div>
      </div>
    </div>
  )
}
