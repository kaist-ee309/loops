"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import { useSettings } from "@/components/settings-provider"

export default function DisplaySettingsPage() {
  const router = useRouter()
  const { settings, setSetting } = useSettings()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-xl font-bold text-gray-900">화면</h1>
      </div>

      <div className="p-4 space-y-4">
        <div className="bg-white rounded-2xl p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-gray-900">다크 모드</div>
              <div className="text-sm text-gray-500">야간 학습 시 눈의 피로를 줄여줘요</div>
            </div>
            <button
              onClick={() => setSetting("darkMode", !settings.darkMode)}
              className={cn(
                "w-12 h-7 rounded-full transition-colors relative",
                settings.darkMode ? "bg-indigo-600" : "bg-gray-300",
              )}
            >
              <div
                className={cn(
                  "absolute top-1 w-5 h-5 bg-white rounded-full transition-transform",
                  settings.darkMode ? "translate-x-6" : "translate-x-1",
                )}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
