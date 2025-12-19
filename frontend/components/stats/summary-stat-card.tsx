import type React from "react"
import { Skeleton } from "@/components/ui/skeleton"

interface SummaryStatCardProps {
  icon: React.ReactNode
  label: string
  value: string
  isLoading?: boolean
}

export function SummaryStatCard({ icon, label, value, isLoading }: SummaryStatCardProps) {
  if (isLoading) {
    return <Skeleton className="h-20 rounded-2xl" />
  }

  return (
    <div className="bg-white rounded-2xl shadow-sm px-4 py-3 flex items-center gap-3">
      <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center shrink-0">{icon}</div>
      <div className="flex flex-col">
        <span className="text-xs text-gray-500">{label}</span>
        <span className="text-lg font-semibold text-gray-900">{value}</span>
      </div>
    </div>
  )
}
