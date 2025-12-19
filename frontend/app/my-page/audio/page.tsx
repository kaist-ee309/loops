"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import { useSettings } from "@/components/settings-provider"

export default function AudioSettingsPage() {
  const router = useRouter()
  const { settings, setSetting } = useSettings()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-xl font-bold text-gray-900">음성 및 효과음</h1>
      </div>

      <div className="p-4 space-y-4">
        <div className="bg-white rounded-2xl p-4 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-gray-900">자동 재생</div>
              <div className="text-sm text-gray-500">카드를 뒤집으면 발음이 자동으로 재생돼요</div>
            </div>
            <button
              onClick={() => setSetting("autoPlayAudio", !settings.autoPlayAudio)}
              className={cn(
                "w-12 h-7 rounded-full transition-colors relative",
                settings.autoPlayAudio ? "bg-indigo-600" : "bg-gray-300",
              )}
            >
              <div
                className={cn(
                  "absolute top-1 w-5 h-5 bg-white rounded-full transition-transform",
                  settings.autoPlayAudio ? "translate-x-6" : "translate-x-1",
                )}
              />
            </button>
          </div>

          <div className="pt-2 border-t border-gray-100 space-y-2">
            <label className="block text-sm text-gray-700 font-medium">재생 속도</label>
            <div className="flex gap-2">
              {([0.75, 1, 1.25] as const).map((speed) => (
                <button
                  key={speed}
                  onClick={() => setSetting("playbackSpeed", speed)}
                  className={cn(
                    "flex-1 py-2 rounded-lg font-medium transition-colors text-sm",
                    settings.playbackSpeed === speed
                      ? "bg-indigo-100 text-indigo-600 border-2 border-indigo-600"
                      : "bg-gray-100 text-gray-600 border-2 border-transparent",
                  )}
                >
                  {speed}x
                </button>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <div>
              <div className="font-medium text-gray-900">효과음</div>
              <div className="text-sm text-gray-500">학습 중 효과음 재생</div>
            </div>
            <button
              onClick={() => setSetting("soundEffects", !settings.soundEffects)}
              className={cn(
                "w-12 h-7 rounded-full transition-colors relative",
                settings.soundEffects ? "bg-indigo-600" : "bg-gray-300",
              )}
            >
              <div
                className={cn(
                  "absolute top-1 w-5 h-5 bg-white rounded-full transition-transform",
                  settings.soundEffects ? "translate-x-6" : "translate-x-1",
                )}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
