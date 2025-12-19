"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight } from "lucide-react"

const legalItems = [
  { label: "이용약관", path: "/my-page/support/legal/terms" },
  { label: "개인정보처리방침", path: "/my-page/support/legal/privacy" },
  { label: "글꼴 저작권", path: "/my-page/support/legal/fonts" },
]

export default function LegalPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-lg font-medium text-gray-900">법적 고지</h1>
      </div>

      {/* Menu List */}
      <div className="divide-y divide-gray-100">
        {legalItems.map((item) => (
          <button
            key={item.label}
            onClick={() => router.push(item.path)}
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
