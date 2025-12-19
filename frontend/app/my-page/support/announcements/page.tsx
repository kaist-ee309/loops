"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, Pin } from "lucide-react"
import { ANNOUNCEMENTS, CATEGORY_STYLES, type Announcement } from "@/lib/data/announcements-data"

export default function AnnouncementsPage() {
  const router = useRouter()
  const [selectedAnnouncement, setSelectedAnnouncement] = useState<Announcement | null>(null)

  // 중요 공지를 상단에 정렬
  const sortedAnnouncements = [...ANNOUNCEMENTS].sort((a, b) => {
    if (a.isImportant && !b.isImportant) return -1
    if (!a.isImportant && b.isImportant) return 1
    return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
  })

  // 상세 보기 화면
  if (selectedAnnouncement) {
    const style = CATEGORY_STYLES[selectedAnnouncement.category]
    return (
      <div className="min-h-screen bg-white">
        {/* Header */}
        <div className="border-b border-gray-200 px-4 py-4 flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => setSelectedAnnouncement(null)}>
            <ChevronLeft className="w-5 h-5 text-gray-700" />
          </Button>
          <h1 className="text-lg font-medium text-gray-900">공지사항</h1>
        </div>

        {/* Content */}
        <div className="p-4">
          <div className="flex items-center gap-2 mb-2">
            <span className={`px-2 py-1 rounded text-xs font-medium ${style.bg} ${style.text}`}>
              {selectedAnnouncement.category}
            </span>
            {selectedAnnouncement.isImportant && <Pin className="w-4 h-4 text-red-500" />}
          </div>
          <h2 className="text-xl font-bold text-gray-900 mb-2">{selectedAnnouncement.title}</h2>
          <p className="text-sm text-gray-500 mb-6">{selectedAnnouncement.createdAt}</p>
          <div className="text-gray-700 whitespace-pre-line leading-relaxed">{selectedAnnouncement.content}</div>
        </div>
      </div>
    )
  }

  // 목록 화면
  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <div className="border-b border-gray-200 px-4 py-4 flex items-center gap-3">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-5 h-5 text-gray-700" />
        </Button>
        <h1 className="text-lg font-medium text-gray-900">공지사항</h1>
      </div>

      {/* Announcements List */}
      <div className="divide-y divide-gray-100">
        {sortedAnnouncements.map((announcement) => {
          const style = CATEGORY_STYLES[announcement.category]
          return (
            <button
              key={announcement.id}
              onClick={() => setSelectedAnnouncement(announcement)}
              className="w-full flex items-center justify-between px-4 py-4 hover:bg-gray-50 transition-colors text-left"
            >
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className={`px-2 py-0.5 rounded text-xs font-medium ${style.bg} ${style.text}`}>
                    {announcement.category}
                  </span>
                  {announcement.isImportant && <Pin className="w-3 h-3 text-red-500" />}
                </div>
                <p className="text-base text-gray-900 truncate">{announcement.title}</p>
                <p className="text-sm text-gray-500 mt-1">{announcement.createdAt}</p>
              </div>
              <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0 ml-2" />
            </button>
          )
        })}
      </div>

      {sortedAnnouncements.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-gray-500">
          <p>등록된 공지사항이 없습니다.</p>
        </div>
      )}
    </div>
  )
}
