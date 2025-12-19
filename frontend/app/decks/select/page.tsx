"use client"

import { ArrowLeft } from "lucide-react"
import { useRouter } from "next/navigation"
import { DeckSelector } from "@/components/decks/deck-selector"

export default function DeckSelectPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white px-4 py-4 flex items-center gap-3 border-b border-gray-200">
        <button onClick={() => router.back()} className="p-1">
          <ArrowLeft className="w-5 h-5 text-gray-600" />
        </button>
        <h1 className="text-lg font-bold text-gray-900">단어장 선택</h1>
      </div>

      <div className="p-4">
        <DeckSelector />
      </div>
    </div>
  )
}
