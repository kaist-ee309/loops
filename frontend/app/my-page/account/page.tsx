"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { ChevronLeft, ChevronRight, MessageCircle, Copy, Check, Plus, Mail, User } from "lucide-react"
import { useRouter } from "next/navigation"

type AuthProvider = "guest" | "email" | "google" | "kakao" | "naver" | "apple" | "facebook" | "other"

type AuthInfo = {
  type: AuthProvider
  email: string
  loginMethod: string
}

const PROVIDER_STYLES: Record<
  string,
  {
    icon: React.ReactNode
    label: string
    bgColor: string
    textColor: string
    borderColor?: string
  }
> = {
  guest: {
    icon: <User className="w-6 h-6 text-gray-600" />,
    label: "게스트 계정",
    bgColor: "bg-gray-200",
    textColor: "text-gray-900",
  },
  email: {
    icon: <Mail className="w-6 h-6 text-blue-600" />,
    label: "이메일 계정",
    bgColor: "bg-blue-100",
    textColor: "text-blue-900",
  },
  google: {
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24">
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
    ),
    label: "Google 계정",
    bgColor: "bg-white",
    textColor: "text-gray-900",
    borderColor: "border border-gray-200",
  },
  kakao: {
    icon: <MessageCircle className="w-6 h-6 text-gray-900" />,
    label: "카카오 계정",
    bgColor: "bg-[#FEE500]",
    textColor: "text-gray-900",
  },
  naver: {
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24">
        <path fill="#fff" d="M16.273 12.845L7.376 0H0v24h7.727V11.155L16.624 24H24V0h-7.727z" />
      </svg>
    ),
    label: "네이버 계정",
    bgColor: "bg-[#03C75A]",
    textColor: "text-white",
  },
  apple: {
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="currentColor">
        <path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09l.01-.01zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z" />
      </svg>
    ),
    label: "Apple 계정",
    bgColor: "bg-black",
    textColor: "text-white",
  },
  facebook: {
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="#fff">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
      </svg>
    ),
    label: "Facebook 계정",
    bgColor: "bg-[#1877F2]",
    textColor: "text-white",
  },
}

const DEFAULT_PROVIDER_STYLE = {
  icon: <Mail className="w-6 h-6 text-gray-500" />,
  label: "기타 계정",
  bgColor: "bg-gray-100",
  textColor: "text-gray-700",
}

function getProviderStyle(type: AuthProvider) {
  return PROVIDER_STYLES[type] || DEFAULT_PROVIDER_STYLE
}

export default function AccountPage() {
  const router = useRouter()
  const [copied, setCopied] = useState(false)
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)
  const [learningPurpose, setLearningPurpose] = useState("")
  const [showPurposeSelect, setShowPurposeSelect] = useState(false)
  const [authInfo, setAuthInfo] = useState<AuthInfo | null>(null)
  const [accountCode, setAccountCode] = useState("")

  useEffect(() => {
    const savedAuth = localStorage.getItem("authInfo")
    if (savedAuth) {
      setAuthInfo(JSON.parse(savedAuth))
    }

    const savedPurpose = localStorage.getItem("learningPurpose")
    if (savedPurpose) {
      setLearningPurpose(savedPurpose)
    } else {
      setLearningPurpose("미설정")
    }

    const savedCode = localStorage.getItem("accountCode")
    if (savedCode) {
      setAccountCode(savedCode)
    } else {
      const newCode = "LOOPS-" + Math.random().toString(36).substring(2, 10).toUpperCase()
      localStorage.setItem("accountCode", newCode)
      setAccountCode(newCode)
    }
  }, [])

  const handleCopyCode = () => {
    navigator.clipboard.writeText(accountCode)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleLogout = () => {
    localStorage.removeItem("authInfo")
    router.push("/")
  }

  const handleDeleteAccount = () => {
    localStorage.clear()
    router.push("/")
  }

  const handlePurposeSelect = (purpose: string) => {
    setLearningPurpose(purpose)
    localStorage.setItem("learningPurpose", purpose)
    setShowPurposeSelect(false)
  }

  const purposes = ["취업/시험 준비", "업무/실무 활용", "여행/취미", "기타"]

  const providerStyle = authInfo ? getProviderStyle(authInfo.type) : null

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white px-4 py-4 flex items-center gap-3 border-b border-gray-200">
        <button onClick={() => router.back()} className="p-1">
          <ChevronLeft className="w-6 h-6" />
        </button>
        <h1 className="text-lg font-bold">계정 관리</h1>
      </div>

      <div className="p-4 space-y-4">
        {/* 계정 코드 섹션 */}
        <div className="bg-white rounded-2xl overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100">
            <h2 className="font-bold text-gray-900">계정 코드</h2>
          </div>
          <div className="p-4 flex items-center justify-between">
            <span className="text-gray-700">Loops 고유 계정 코드</span>
            <Button
              variant="outline"
              size="sm"
              onClick={handleCopyCode}
              className="flex items-center gap-2 bg-transparent"
            >
              {copied ? (
                <>
                  <Check className="w-4 h-4" />
                  복사됨
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  코드 복사하기
                </>
              )}
            </Button>
          </div>
        </div>

        {/* 계정 연결 섹션 */}
        <div className="bg-white rounded-2xl overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100">
            <h2 className="font-bold text-gray-900">계정 연결</h2>
          </div>

          {/* 로그아웃 */}
          <div className="p-4 flex items-center justify-between border-b border-gray-100">
            <span className="text-gray-700">로그아웃하고 싶으세요?</span>
            <Button variant="outline" size="sm" onClick={handleLogout}>
              로그아웃
            </Button>
          </div>

          <div className="p-4 space-y-3">
            <span className="text-sm text-gray-500">연결된 계정</span>

            {authInfo && providerStyle && (
              <div className={`${providerStyle.bgColor} ${providerStyle.borderColor || ""} rounded-xl overflow-hidden`}>
                <div className="p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {providerStyle.icon}
                    <span className={`font-medium ${providerStyle.textColor}`}>{providerStyle.label}</span>
                  </div>
                  {authInfo.type !== "guest" && (
                    <button className={`flex items-center gap-1 text-sm ${providerStyle.textColor} opacity-80`}>
                      연결해제
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  )}
                </div>
                <div className="px-4 pb-4">
                  <span className={`text-sm ${providerStyle.textColor} opacity-80`}>이메일: {authInfo.email}</span>
                </div>
              </div>
            )}

            {authInfo?.type !== "guest" && (
              <button className="w-full border-2 border-dashed border-gray-300 rounded-xl p-4 flex items-center justify-center gap-2 text-gray-500 hover:bg-gray-50 transition-colors">
                <Plus className="w-5 h-5" />
                추가 계정 연결하기
                <span className="w-5 h-5 rounded-full bg-gray-300 text-white text-xs flex items-center justify-center">
                  ?
                </span>
              </button>
            )}

            {authInfo?.type === "guest" && (
              <div className="bg-violet-50 rounded-xl p-4 text-center">
                <p className="text-sm text-violet-700 mb-3">
                  게스트 상태입니다. 학습 데이터를 저장하려면 계정을 연결하세요.
                </p>
                <Button size="sm" onClick={() => router.push("/signup")} className="bg-violet-600 hover:bg-violet-700">
                  계정 연결하기
                </Button>
              </div>
            )}
          </div>
        </div>

        {/* 계정 관리 섹션 */}
        <div className="bg-white rounded-2xl overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100">
            <h2 className="font-bold text-gray-900">계정 관리</h2>
          </div>

          <button
            onClick={() => setShowPurposeSelect(true)}
            className="w-full p-4 flex items-center justify-between border-b border-gray-100 hover:bg-gray-50 transition-colors"
          >
            <span className="text-gray-700">학습 목적</span>
            <div className="flex items-center gap-1 text-gray-500">
              <span>{learningPurpose}</span>
              <ChevronRight className="w-4 h-4" />
            </div>
          </button>

          <button
            onClick={() => setShowDeleteConfirm(true)}
            className="w-full p-4 text-left text-gray-700 hover:bg-gray-50 transition-colors"
          >
            탈퇴하기
          </button>
        </div>
      </div>

      {/* 학습 목적 선택 모달 */}
      {showPurposeSelect && (
        <div className="fixed inset-0 bg-black/50 flex items-end justify-center z-50">
          <div className="bg-white w-full max-w-lg rounded-t-2xl">
            <div className="p-4 border-b border-gray-200 flex items-center justify-between">
              <h3 className="font-bold text-lg">학습 목적 선택</h3>
              <button onClick={() => setShowPurposeSelect(false)} className="text-gray-500">
                취소
              </button>
            </div>
            <div className="p-2">
              {purposes.map((purpose) => (
                <button
                  key={purpose}
                  onClick={() => handlePurposeSelect(purpose)}
                  className={`w-full p-4 text-left rounded-xl transition-colors ${
                    learningPurpose === purpose ? "bg-violet-100 text-violet-700" : "hover:bg-gray-100"
                  }`}
                >
                  {purpose}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* 탈퇴 확인 모달 */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white w-full max-w-sm rounded-2xl p-6">
            <h3 className="font-bold text-lg mb-2">정말 탈퇴하시겠습니까?</h3>
            <p className="text-gray-600 text-sm mb-6">탈퇴 시 모든 학습 데이터가 삭제되며 복구할 수 없습니다.</p>
            <div className="flex gap-3">
              <Button variant="outline" className="flex-1 bg-transparent" onClick={() => setShowDeleteConfirm(false)}>
                취소
              </Button>
              <Button variant="destructive" className="flex-1" onClick={handleDeleteAccount}>
                탈퇴하기
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
