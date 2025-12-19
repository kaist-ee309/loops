"use client"

import type React from "react"
import { useState, useMemo, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChevronLeft, Plus, Clock, CheckCircle, ChevronUp, ChevronDown } from "lucide-react"
import { FAQ_DATA, FAQ_CATEGORIES, type FAQItem } from "@/lib/data/faq-data"

interface SavedQuestion {
  id: string
  category: string
  question: string
  status: "pending" | "answered"
  answer?: string
  createdAt: string
  answeredAt?: string
}

export default function FAQPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState("all")
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [savedQuestions, setSavedQuestions] = useState<SavedQuestion[]>([])
  const [expandedSavedId, setExpandedSavedId] = useState<string | null>(null)
  const [showSaveConfirm, setShowSaveConfirm] = useState(false)

  useEffect(() => {
    const saved = localStorage.getItem("savedFAQQuestions")
    if (saved) {
      setSavedQuestions(JSON.parse(saved))
    }
  }, [])

  useEffect(() => {
    if (savedQuestions.length > 0) {
      localStorage.setItem("savedFAQQuestions", JSON.stringify(savedQuestions))
    }
  }, [savedQuestions])

  const filteredFAQs = useMemo(() => {
    return FAQ_DATA.filter((faq) => {
      const matchesCategory = selectedCategory === "all" || faq.category === selectedCategory
      return matchesCategory
    })
  }, [selectedCategory])

  const handleQuestionClick = (id: string) => {
    setExpandedId(expandedId === id ? null : id)
  }

  const handleSaveQuestion = () => {
    if (searchQuery.trim() === "") return

    const newQuestion: SavedQuestion = {
      id: Date.now().toString(),
      category: selectedCategory,
      question: searchQuery.trim(),
      status: "pending",
      createdAt: new Date().toISOString(),
    }

    setSavedQuestions([...savedQuestions, newQuestion])
    setShowSaveConfirm(true)
    setSearchQuery("")

    setTimeout(() => setShowSaveConfirm(false), 3000)

    // TODO: 백엔드 연동 시 여기서 API 호출
    console.log("저장된 질문:", newQuestion)
  }

  const handleDeleteQuestion = (id: string) => {
    const updated = savedQuestions.filter((q) => q.id !== id)
    setSavedQuestions(updated)
    if (updated.length === 0) {
      localStorage.removeItem("savedFAQQuestions")
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && searchQuery.trim() !== "") {
      handleSaveQuestion()
    }
  }

  const pendingCount = savedQuestions.filter((q) => q.status === "pending").length
  const answeredCount = savedQuestions.filter((q) => q.status === "answered").length

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-lg font-medium text-gray-900">Loops FAQ</h1>
      </div>

      {/* Hero Section */}
      <div className="bg-gradient-to-b from-gray-50 to-white px-4 py-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Loops FAQ</h2>
        <p className="text-gray-600">Loops FAQ로 궁금증을 해결해 보세요!</p>
      </div>

      {/* Search Section */}
      <div className="bg-gray-100 px-4 py-6">
        <div className="relative">
          <Input
            type="text"
            placeholder="무엇이든 물어보세요"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full pl-4 pr-12 py-3 rounded-full bg-white border-0 shadow-sm"
          />
          {searchQuery.trim() !== "" && (
            <Button
              variant="ghost"
              size="icon"
              onClick={handleSaveQuestion}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-violet-600 hover:text-violet-700"
            >
              <Plus className="w-5 h-5" />
            </Button>
          )}
        </div>
        {showSaveConfirm && (
          <p className="text-sm text-green-600 mt-2 text-center">
            질문이 저장되었습니다! (
            {selectedCategory === "all" ? "전체" : FAQ_CATEGORIES.find((c) => c.id === selectedCategory)?.label})
          </p>
        )}
      </div>

      {/* Category Filter */}
      <div className="px-4 py-3 flex gap-2 overflow-x-auto scrollbar-hide">
        {FAQ_CATEGORIES.map((category) => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            className={`px-4 py-2 rounded-full text-sm whitespace-nowrap transition-colors ${
              selectedCategory === category.id
                ? "bg-violet-600 text-white"
                : "bg-gray-100 text-gray-700 hover:bg-gray-200"
            }`}
          >
            {category.label}
          </button>
        ))}
      </div>

      {/* FAQ List */}
      <div className="px-4 py-4">
        <div className="flex justify-between items-center mb-4">
          <h3 className="font-medium text-gray-900">자주 묻는 질문</h3>
          <p className="text-sm text-gray-500">{filteredFAQs.length}개의 질문</p>
        </div>
        <div className="space-y-2">
          {filteredFAQs.map((faq) => (
            <FAQAccordionItem
              key={faq.id}
              faq={faq}
              isExpanded={expandedId === faq.id}
              onToggle={() => handleQuestionClick(faq.id)}
            />
          ))}
          {filteredFAQs.length === 0 && (
            <div className="text-center py-8 text-gray-500">해당 카테고리에 질문이 없습니다.</div>
          )}
        </div>
      </div>

      {savedQuestions.length > 0 && (
        <div className="px-4 py-4 border-t border-gray-200">
          <div className="flex justify-between items-center mb-4">
            <h3 className="font-medium text-gray-900">내가 저장한 질문</h3>
            <div className="flex gap-3 text-xs">
              <span className="flex items-center gap-1 text-amber-600">
                <Clock className="w-3 h-3" /> 대기중 {pendingCount}
              </span>
              <span className="flex items-center gap-1 text-green-600">
                <CheckCircle className="w-3 h-3" /> 답변완료 {answeredCount}
              </span>
            </div>
          </div>
          <div className="space-y-2">
            {savedQuestions.map((sq) => (
              <SavedQuestionItem
                key={sq.id}
                question={sq}
                isExpanded={expandedSavedId === sq.id}
                onToggle={() => setExpandedSavedId(expandedSavedId === sq.id ? null : sq.id)}
                onDelete={() => handleDeleteQuestion(sq.id)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function FAQAccordionItem({
  faq,
  isExpanded,
  onToggle,
}: {
  faq: FAQItem
  isExpanded: boolean
  onToggle: () => void
}) {
  return (
    <div className="border border-gray-200 rounded-xl overflow-hidden">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between p-4 text-left hover:bg-gray-50 transition-colors"
      >
        <span className="text-sm text-gray-900 pr-4">{faq.question}</span>
        {isExpanded ? (
          <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
        ) : (
          <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
        )}
      </button>
      {isExpanded && (
        <div className="px-4 pb-4 pt-0">
          <p className="text-sm text-gray-600 leading-relaxed bg-gray-50 p-3 rounded-lg">{faq.answer}</p>
        </div>
      )}
    </div>
  )
}

function SavedQuestionItem({
  question,
  isExpanded,
  onToggle,
  onDelete,
}: {
  question: SavedQuestion
  isExpanded: boolean
  onToggle: () => void
  onDelete: () => void
}) {
  const isPending = question.status === "pending"

  return (
    <div
      className={`border rounded-xl overflow-hidden ${
        isPending ? "border-amber-200 bg-amber-50" : "border-green-200 bg-green-50"
      }`}
    >
      <button onClick={onToggle} className="w-full flex items-center justify-between p-4 text-left">
        <div className="flex-1 pr-4">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-gray-500">
              {question.category === "all" ? "전체" : FAQ_CATEGORIES.find((c) => c.id === question.category)?.label}
            </span>
            {isPending ? (
              <span className="flex items-center gap-1 text-xs text-amber-600 bg-amber-100 px-2 py-0.5 rounded-full">
                <Clock className="w-3 h-3" /> 대기중
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs text-green-600 bg-green-100 px-2 py-0.5 rounded-full">
                <CheckCircle className="w-3 h-3" /> 답변완료
              </span>
            )}
          </div>
          <p className="text-sm text-gray-900">{question.question}</p>
          <p className="text-xs text-gray-400 mt-1">{new Date(question.createdAt).toLocaleDateString("ko-KR")}</p>
        </div>
        {question.status === "answered" ? (
          isExpanded ? (
            <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0" />
          ) : (
            <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0" />
          )
        ) : (
          <button
            onClick={(e) => {
              e.stopPropagation()
              onDelete()
            }}
            className="text-xs text-gray-400 hover:text-red-500"
          >
            삭제
          </button>
        )}
      </button>
      {/* 답변완료 시 답변 내용 표시 */}
      {isExpanded && question.status === "answered" && question.answer && (
        <div className="px-4 pb-4 pt-0">
          <div className="bg-white p-3 rounded-lg border border-green-200">
            <p className="text-xs text-green-600 mb-1">
              답변일: {question.answeredAt && new Date(question.answeredAt).toLocaleDateString("ko-KR")}
            </p>
            <p className="text-sm text-gray-700 leading-relaxed">{question.answer}</p>
          </div>
        </div>
      )}
    </div>
  )
}
