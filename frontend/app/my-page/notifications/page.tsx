"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"
import { cn } from "@/lib/utils"
import { useSettings } from "@/components/settings-provider"

export default function NotificationsSettingsPage() {
  const router = useRouter()
  const { settings, setSetting } = useSettings()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-xl font-bold text-gray-900">알림</h1>
      </div>

      <div className="p-4 space-y-4">
        <div className="bg-white rounded-2xl p-4 space-y-4">
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

          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <div>
              <div className="font-medium text-gray-900">복습 리마인더</div>
              <div className="text-sm text-gray-500">복습 시간을 놓치면 다시 알려드려요</div>
            </div>
            <button
              onClick={() => setSetting("reviewReminder", !settings.reviewReminder)}
              className={cn(
                "w-12 h-7 rounded-full transition-colors relative",
                settings.reviewReminder ? "bg-indigo-600" : "bg-gray-300",
              )}
            >
              <div
                className={cn(
                  "absolute top-1 w-5 h-5 bg-white rounded-full transition-transform",
                  settings.reviewReminder ? "translate-x-6" : "translate-x-1",
                )}
              />
            </button>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <div>
              <div className="font-medium text-gray-900">학습 리포트</div>
              <div className="text-sm text-gray-500">주간 학습 리포트 알림</div>
            </div>
            <button
              onClick={() => setSetting("studyReport", !settings.studyReport)}
              className={cn(
                "w-12 h-7 rounded-full transition-colors relative",
                settings.studyReport ? "bg-indigo-600" : "bg-gray-300",
              )}
            >
              <div
                className={cn(
                  "absolute top-1 w-5 h-5 bg-white rounded-full transition-transform",
                  settings.studyReport ? "translate-x-6" : "translate-x-1",
                )}
              />
            </button>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-gray-100">
            <div>
              <div className="font-medium text-gray-900">리그 알림</div>
              <div className="text-sm text-gray-500">리그 업데이트 및 순위 변동 알림</div>
            </div>
            <button
              onClick={() => setSetting("leagueAlerts", !settings.leagueAlerts)}
              className={cn(
                "w-12 h-7 rounded-full transition-colors relative",
                settings.leagueAlerts ? "bg-indigo-600" : "bg-gray-300",
              )}
            >
              <div
                className={cn(
                  "absolute top-1 w-5 h-5 bg-white rounded-full transition-transform",
                  settings.leagueAlerts ? "translate-x-6" : "translate-x-1",
                )}
              />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
