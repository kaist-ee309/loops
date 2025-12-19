"use client"

import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft } from "lucide-react"

export default function UpdateHistoryPage() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-xl font-bold text-gray-900">업데이트 히스토리</h1>
      </div>

      <div className="p-4">
        <div className="bg-white rounded-2xl p-6">
          <div className="space-y-4">
            <div className="border-b border-gray-100 pb-4">
              <div className="font-bold text-gray-900 mb-1">앱 버전: 1.2.369</div>
              <div className="text-sm text-gray-500">로이드가 실험 중인 기능들</div>
            </div>
            <div className="text-gray-600 text-sm">최신 업데이트 내역이 여기에 표시됩니다.</div>
          </div>
        </div>
      </div>
    </div>
  )
}
