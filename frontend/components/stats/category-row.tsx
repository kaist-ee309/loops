"use client"

import type React from "react"

import { ChevronRight } from "lucide-react"

interface CategoryRowProps {
  icon: React.ReactNode
  title: string
  rightLabel: string
  progressPercent: number
  subLabel: string
  onClick?: () => void
}

export function CategoryRow({ icon, title, rightLabel, progressPercent, subLabel, onClick }: CategoryRowProps) {
  const normalized = typeof progressPercent === "number" && Number.isFinite(progressPercent) ? progressPercent : 0
  const safeProgress = Math.min(100, Math.max(0, normalized))

  return (
    <div className="flex flex-col gap-2 py-3 border-b border-gray-100 last:border-b-0 cursor-pointer" onClick={onClick}>
      {/* Top row: icon, title, right label, chevron */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center shrink-0">{icon}</div>
        <span className="font-semibold text-gray-900 flex-1">{title}</span>
        <div className="flex items-center gap-1 text-sm text-indigo-600">
          <span>{rightLabel}</span>
          <ChevronRight className="w-4 h-4" />
        </div>
      </div>

      {/* Progress bar */}
      <div className="ml-[52px]">
        <div className="h-2 rounded-full bg-gray-100 overflow-hidden">
          <div className="h-full bg-yellow-400 rounded-full transition-all" style={{ width: `${safeProgress}%` }} />
        </div>
      </div>

      {/* Sub label */}
      <div className="ml-[52px] text-sm text-gray-500">{subLabel}</div>
    </div>
  )
}
