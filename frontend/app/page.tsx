"use client"

import Link from "next/link"
import { Button } from "@/components/ui/button"
import { useRouter } from "next/navigation"

const DEV_MODE = true

export default function LandingPage() {
  const router = useRouter()

  const handleDevSkip = () => {
    localStorage.setItem(
      "authInfo",
      JSON.stringify({
        type: "guest",
        email: "devs@kaist.ac.kr",
        loginMethod: "dev_skip",
      }),
    )
    router.push("/dashboard")
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-background">
      {DEV_MODE && (
        <button
          onClick={handleDevSkip}
          className="absolute top-4 right-4 text-xs text-muted-foreground hover:text-foreground px-3 py-1.5 rounded-md hover:bg-accent transition-colors"
        >
          [DEV] Skip
        </button>
      )}
      {/* END DEV SKIP BUTTON */}

      <div className="max-w-md w-full text-center space-y-8">
        <div className="space-y-2">
          <h1 className="text-4xl font-bold tracking-tight text-indigo-600">Loops</h1>
          <p className="text-muted-foreground text-lg">
            과학적인 반복 학습으로
            <br />
            영단어를 영구적으로 기억하세요.
          </p>
        </div>

        <div className="space-y-4 pt-8">
          <Link href="/signup" className="block w-full">
            <Button size="lg" className="w-full text-lg">
              이메일로 시작하기
            </Button>
          </Link>

          <Link href="/login" className="block w-full">
            <Button variant="outline" size="lg" className="w-full text-lg bg-transparent">
              이미 계정이 있나요? 로그인
            </Button>
          </Link>
        </div>

        <div className="pt-8 text-sm text-muted-foreground">
          <p>FSRS 알고리즘 기반 학습 시스템</p>
        </div>
      </div>
    </div>
  )
}
