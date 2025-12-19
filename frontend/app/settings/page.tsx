"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Bell, Volume2, Moon, Globe } from "lucide-react"
import { cn } from "@/lib/utils"
import { useSettings } from "@/components/settings-provider"
import type { Settings } from "@/lib/settings/types"

export default function SettingsPage() {
  const router = useRouter()
  const { settings, setSetting } = useSettings()

  return (
    <div className="min-h-screen bg-gray-50 pb-20">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.push("/dashboard")}>
          <ArrowLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-xl font-bold text-gray-900">설정</h1>
      </div>

      <div className="p-4 space-y-6">
        {/* Notification Settings */}
        <div className="bg-white rounded-2xl p-4 space-y-4">
          <div className="flex items-center gap-2 text-gray-700 font-bold">
            <Bell className="w-5 h-5" />
            <span>알림 설정</span>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <div className="font-medium text-gray-900">복습 알림</div>
                <div className="text-sm text-gray-500">복습할 단어가 있을 때 알려드려요</div>
              </div>
              <button
                onClick={() => setSetting("notificationsEnabled", !settings.notificationsEnabled)}
                className={cn(
                  "w-12 h-7 rounded-full transition-colors relative",
                  settings.notificationsEnabled ? "bg-indigo-600" : "bg-gray-300",
                )}
              >
                <div
                  className={cn(
                    "absolute top-1 w-5 h-5 bg-white rounded-full transition-transform",
                    settings.notificationsEnabled ? "translate-x-6" : "translate-x-1",
                  )}
                />
              </button>
            </div>

            {settings.notificationsEnabled && (
              <div className="ml-4 space-y-2">
                <label className="block text-sm text-gray-700 font-medium">알림 시간</label>
                <input
                  type="time"
                  value={settings.notificationTime}
                  onChange={(e) => setSetting("notificationTime", e.target.value)}
                  className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
                <p className="text-xs text-gray-400">매일 이 시간에 복습 알림을 보내드려요</p>
              </div>
            )}
          </div>
        </div>

        {/* Audio Settings */}
        <div className="bg-white rounded-2xl p-4 space-y-4">
          <div className="flex items-center gap-2 text-gray-700 font-bold">
            <Volume2 className="w-5 h-5" />
            <span>발음 설정</span>
          </div>

          <div className="space-y-3">
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

            <div className="space-y-2">
              <label className="block text-sm text-gray-700 font-medium">재생 속도</label>
              <div className="flex gap-2">
                {([0.75, 1, 1.25] as const).map((speed) => (
                  <button
                    key={speed}
                    onClick={() => setSetting("playbackSpeed", speed)}
                    className={cn(
                      "flex-1 py-2 rounded-lg font-medium transition-colors",
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
          </div>
        </div>

        {/* Study Settings */}
        <div className="bg-white rounded-2xl p-4 space-y-4">
          <div className="flex items-center gap-2 text-gray-700 font-bold">
            <Globe className="w-5 h-5" />
            <span>학습 설정</span>
          </div>

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
        </div>

        {/* Appearance */}
        <div className="bg-white rounded-2xl p-4 space-y-4">
          <div className="flex items-center gap-2 text-gray-700 font-bold">
            <Moon className="w-5 h-5" />
            <span>화면 설정</span>
          </div>

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
