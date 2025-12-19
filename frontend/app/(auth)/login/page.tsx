"use client"

import type React from "react"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Loader2 } from "lucide-react"
import { useAuth } from "@/components/auth-provider"
import { getAuthFriendlyError, shouldSuggestRegister } from "@/lib/auth/error-messages"

export default function LoginPage() {
  const router = useRouter()
  const { login } = useAuth()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showRegisterCta, setShowRegisterCta] = useState(false)
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setEmail(e.target.value)
    setError(null)
    setShowRegisterCta(false)
  }

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value)
    setError(null)
    setShowRegisterCta(false)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)
    setShowRegisterCta(false)

    try {
      await login(email, password)
      router.push("/dashboard")
    } catch (err) {
      console.warn("[Auth] Login error:", err)
      setError(getAuthFriendlyError(err, "login"))
      setShowRegisterCta(shouldSuggestRegister(err))
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
          <h1 className="text-2xl font-bold">다시 오셨군요!</h1>
          <p className="text-gray-500">오늘의 학습 목표를 달성해볼까요?</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl text-sm">
              <p>{error}</p>
              {showRegisterCta && (
                <Link
                  href="/signup"
                  className="inline-block mt-2 text-indigo-600 hover:text-indigo-700 font-medium underline"
                >
                  회원가입하러 가기
                </Link>
              )}
            </div>
          )}

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-700">이메일</label>
            <input
              type="email"
              required
              value={email}
              onChange={handleEmailChange}
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
              onChange={handlePasswordChange}
              className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 outline-none transition-all"
              placeholder="••••••••"
            />
          </div>

          <Button type="submit" className="w-full py-6 text-lg" disabled={isLoading}>
            {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : "로그인하기"}
          </Button>
        </form>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-gray-200" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-white px-2 text-gray-500">또는</span>
          </div>
        </div>

        <Button variant="outline" className="w-full py-6 bg-transparent" type="button">
          <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24">
            <path
              d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              fill="#4285F4"
            />
            <path
              d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              fill="#34A853"
            />
            <path
              d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              fill="#FBBC05"
            />
            <path
              d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              fill="#EA4335"
            />
          </svg>
          Google로 계속하기
        </Button>
      </div>
    </div>
  )
}
