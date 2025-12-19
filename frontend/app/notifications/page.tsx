"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft, Bell } from "lucide-react"

export default function NotificationsPage() {
  const router = useRouter()

  const notifications = [
    {
      id: 1,
      title: "복습할 단어가 20개 있어요!",
      message: "지금 복습하고 기억을 강화하세요",
      time: "10분 전",
      read: false,
    },
    {
      id: 2,
      title: "7일 연속 학습 달성!",
      message: "멋져요! 계속 이 페이스를 유지해보세요",
      time: "1시간 전",
      read: true,
    },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-xl font-bold text-gray-900">알림</h1>
      </div>

      <div className="p-4 space-y-3">
        {notifications.map((notif) => (
          <div key={notif.id} className={`bg-white rounded-xl p-4 ${!notif.read ? "border-2 border-indigo-200" : ""}`}>
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                <Bell className="w-5 h-5 text-indigo-600" />
              </div>
              <div className="flex-1">
                <div className="font-bold text-gray-900">{notif.title}</div>
                <div className="text-sm text-gray-600 mt-1">{notif.message}</div>
                <div className="text-xs text-gray-400 mt-2">{notif.time}</div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
