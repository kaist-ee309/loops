"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Loader2 } from "lucide-react"

export default function OnboardingCompletePage() {
  const router = useRouter()

  useEffect(() => {
    // Simulate loading initial deck
    const timer = setTimeout(() => {
      router.push("/learn")
    }, 2000)

    return () => clearTimeout(timer)
  }, [router])

  return (
    <div className="min-h-screen bg-white flex flex-col items-center justify-center p-6 text-center space-y-6">
      <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center mb-4">
        <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
      </div>

      <div className="space-y-2">
        <h1 className="text-2xl font-bold">맞춤 단어장을 만들고 있어요</h1>
        <p className="text-gray-500">
          준호님을 위한 첫 20개 단어가 준비되고 있습니다.
          <br />
          잠시만 기다려주세요!
        </p>
      </div>
    </div>
  )
}
