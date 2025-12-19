"use client"

import { useRouter } from "next/navigation"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

const supportItems = [
  { label: "Loops 고객센터", path: "/my-page/support/faq" },
  { label: "수강증 발급", path: "", comingSoon: true },
  { label: "공지사항", path: "/my-page/support/announcements" },
  { label: "법적 고지", path: "/my-page/support/legal" },
  { label: "문제 보고", path: "/my-page/support/report" },
]

export default function SupportPage() {
  const router = useRouter()
  const [showComingSoon, setShowComingSoon] = useState(false)

  const handleItemClick = (item: (typeof supportItems)[0]) => {
    if (item.comingSoon) {
      setShowComingSoon(true)
      setTimeout(() => setShowComingSoon(false), 2000)
    } else {
      router.push(item.path)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-lg font-medium text-gray-900">고객지원</h1>
      </div>

      {showComingSoon && (
        <div className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gray-800 text-white px-6 py-3 rounded-lg shadow-lg z-50">
          준비중입니다!
        </div>
      )}

      {/* Menu List */}
      <div className="divide-y divide-gray-100">
        {supportItems.map((item) => (
          <button
            key={item.label}
            onClick={() => handleItemClick(item)}
            className="w-full flex items-center justify-between px-4 py-5 hover:bg-gray-50 transition-colors"
          >
            <span className="text-base text-gray-900">{item.label}</span>
            <ChevronRight className="w-5 h-5 text-gray-400" />
          </button>
        ))}
      </div>
    </div>
  )
}
