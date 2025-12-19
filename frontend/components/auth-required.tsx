"use client"

import type React from "react"
import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "./auth-provider"
import { Loader2 } from "lucide-react"

interface AuthRequiredProps {
  children: React.ReactNode
}

export function AuthRequired({ children }: AuthRequiredProps) {
  const router = useRouter()
  const { isAuthed, isLoading } = useAuth()

  useEffect(() => {
    if (!isLoading && !isAuthed) {
      router.replace("/login")
    }
  }, [isAuthed, isLoading, router])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  if (!isAuthed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
      </div>
    )
  }

  return <>{children}</>
}
