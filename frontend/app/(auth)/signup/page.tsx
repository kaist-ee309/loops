"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Loader2 } from "lucide-react"
import { useAuth } from "@/components/auth-provider"
import { getAuthFriendlyError, shouldSuggestLogin } from "@/lib/auth/error-messages"

export default function SignupPage() {
  const router = useRouter()
  const { register } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showLoginCta, setShowLoginCta] = useState(false)
  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const clearError = () => {
    setError(null)
    setShowLoginCta(false)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setShowLoginCta(false)

    try {
      await register(email, name, password)
      localStorage.setItem("signupNickname", name)
      router.push("/dashboard")
    } catch (err) {
      console.warn("[Auth] Register error:", err)
      setError(getAuthFriendlyError(err, "register"))
      setShowLoginCta(shouldSuggestLogin(err))
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white p-6 flex flex-col">
      <Link href="/" className="inline-flex items-center text-gray-500 mb-8">
        <ArrowLeft className="w-4 h-4 mr-2" />
        돌아가기
      </Link>

      <div className="flex-1 flex flex-col justify-center max-w-md mx-auto w-full space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-bold">환영합니다! 🎉</h1>
          <p className="text-gray-500">30초만에 가입하고 바로 시작하세요.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
              <p>{error}</p>
              {showLoginCta && (
                <Link
                  href="/login"
                  className="inline-block mt-2 text-indigo-600 hover:text-indigo-700 font-medium underline"
                >
                  로그인하러 가기
                </Link>
              )}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">이름</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => {
                setName(e.target.value)
                clearError()
              }}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="홍길동"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">이메일</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                clearError()
              }}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="hello@example.com"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">비밀번호</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => {
                setPassword(e.target.value)
                clearError()
              }}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="••••••••"
            />
          </div>

          <Button type="submit" className="w-full py-6 text-lg" disabled={isLoading}>
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "무료로 시작하기"}
          </Button>
        </form>
      </div>
    </div>
  )
}
