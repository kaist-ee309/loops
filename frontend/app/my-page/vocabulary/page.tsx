"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"
import { useSettings } from "@/components/settings-provider"
import type { Settings } from "@/lib/settings/types"

export default function VocabularySettingsPage() {
  const router = useRouter()
  const { settings, setSetting } = useSettings()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-xl font-bold text-gray-900">어휘학습</h1>
      </div>

      <div className="p-4 space-y-4">
        <div className="bg-white rounded-2xl p-4 space-y-4">
          <div className="space-y-2">
            <label className="block text-sm text-gray-700 font-medium">하루 목표 (단어 수)</label>
            <select
              value={settings.dailyGoal}
              onChange={(e) => setSetting("dailyGoal", Number(e.target.value) as Settings["dailyGoal"])}
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value={10}>10개 (가볍게)</option>
              <option value={20}>20개 (적당히)</option>
              <option value={30}>30개 (집중)</option>
              <option value={50}>50개 (고강도)</option>
            </select>
          </div>

          <div className="pt-2 border-t border-gray-100 space-y-2">
            <label className="block text-sm text-gray-700 font-medium">퀴즈 모드</label>
            <select
              value={settings.quizMode}
              onChange={(e) => setSetting("quizMode", e.target.value as Settings["quizMode"])}
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="flashcard">플래시카드</option>
              <option value="multiple-choice">객관식</option>
              <option value="typing">타이핑</option>
            </select>
          </div>

          <div className="pt-2 border-t border-gray-100 space-y-2">
            <label className="block text-sm text-gray-700 font-medium">난이도</label>
            <select
              value={settings.difficulty}
              onChange={(e) => setSetting("difficulty", e.target.value as Settings["difficulty"])}
              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="easy">쉬움</option>
              <option value="medium">보통</option>
              <option value="hard">어려움</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  )
}
