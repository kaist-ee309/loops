"use client"

import { Skeleton } from "@/components/ui/skeleton"
import { useMe } from "@/features/me/useMe"
import { cn } from "@/lib/utils"

interface UserDisplayNameProps {
  withSuffix?: boolean
  className?: string
  fallback?: string
  skeletonWidth?: string
}

export function UserDisplayName({ withSuffix = false, className, fallback = "사용자", skeletonWidth }: UserDisplayNameProps) {
  const { displayName, loading } = useMe()

  if (loading) {
    return <Skeleton className={cn("h-6 w-20", skeletonWidth, className)} />
  }

  const name = displayName || fallback
  return <span className={className}>{withSuffix ? `${name}님` : name}</span>
}
