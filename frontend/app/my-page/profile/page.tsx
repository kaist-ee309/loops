"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ChevronLeft, Pencil, Clock, Flame, Calendar, Check, X } from "lucide-react"
import { useRouter } from "next/navigation"
import { useMe } from "@/features/me/useMe"

const LOCAL_NICKNAME_KEY = "signupNickname"

export default function ProfilePage() {
  const router = useRouter()
  const { displayName, profile } = useMe()
  const [nickname, setNickname] = useState("사용자")
  const [isEditingNickname, setIsEditingNickname] = useState(false)
  const [editNicknameValue, setEditNicknameValue] = useState("")

  const [motto, setMotto] = useState("Every word you learn opens a new door.")
  const [isEditingMotto, setIsEditingMotto] = useState(false)
  const [editMottoValue, setEditMottoValue] = useState("")

  useEffect(() => {
    const savedNickname = localStorage.getItem("userNickname")
    if (savedNickname) {
      setNickname(savedNickname)
    }
    if (!savedNickname) {
      const derived = profile?.nickname || profile?.name || profile?.username || displayName
      if (derived) {
        setNickname(derived)
      }
    }

    const savedMotto = localStorage.getItem("userMotto")
    if (savedMotto) {
      setMotto(savedMotto)
    }
  }, [profile, displayName])

  const handleEditNickname = () => {
    setEditNicknameValue(nickname)
    setIsEditingNickname(true)
  }

  const handleSaveNickname = () => {
    if (editNicknameValue.trim()) {
      setNickname(editNicknameValue.trim())
      localStorage.setItem("userNickname", editNicknameValue.trim())
      localStorage.setItem(LOCAL_NICKNAME_KEY, editNicknameValue.trim())
    }
    setIsEditingNickname(false)
  }

  const handleCancelNickname = () => {
    setIsEditingNickname(false)
    setEditNicknameValue("")
  }

  const handleEditMotto = () => {
    setEditMottoValue(motto)
    setIsEditingMotto(true)
  }

  const handleSaveMotto = () => {
    if (editMottoValue.trim()) {
      setMotto(editMottoValue.trim())
      localStorage.setItem("userMotto", editMottoValue.trim())
    }
    setIsEditingMotto(false)
  }

  const handleCancelMotto = () => {
    setIsEditingMotto(false)
    setEditMottoValue("")
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-indigo-100 via-purple-50 to-white">
      {/* Header */}
      <div className="bg-white px-4 py-4 flex items-center gap-3 border-b border-gray-200">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ChevronLeft className="w-6 h-6" />
        </Button>
        <h1 className="text-lg font-semibold text-gray-900">프로필 정보</h1>
      </div>

      {/* Profile Content */}
      <div className="px-6 pt-12 pb-8">
        <div className="relative mb-12">
          <div className="bg-white rounded-3xl px-6 py-4 shadow-sm inline-block max-w-[90%]">
            {isEditingMotto ? (
              <div className="flex items-center gap-2">
                <Input
                  value={editMottoValue}
                  onChange={(e) => setEditMottoValue(e.target.value)}
                  className="text-base italic min-w-[200px]"
                  placeholder="좋아하는 영어 좌우명을 입력하세요"
                  autoFocus
                  onKeyDown={(e) => {
                    if (e.key === "Enter") handleSaveMotto()
                    if (e.key === "Escape") handleCancelMotto()
                  }}
                />
                <button
                  onClick={handleSaveMotto}
                  className="flex-shrink-0 w-8 h-8 rounded-full bg-green-100 flex items-center justify-center hover:bg-green-200 transition-colors"
                >
                  <Check className="w-4 h-4 text-green-600" />
                </button>
                <button
                  onClick={handleCancelMotto}
                  className="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 flex items-center justify-center hover:bg-red-200 transition-colors"
                >
                  <X className="w-4 h-4 text-red-600" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-3">
                <p className="text-gray-800 text-base italic">&ldquo;{motto}&rdquo;</p>
                <button
                  onClick={handleEditMotto}
                  className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center hover:bg-indigo-200 transition-colors"
                  title="좌우명 편집"
                >
                  <Pencil className="w-4 h-4 text-indigo-600" />
                </button>
              </div>
            )}
          </div>
          <div className="absolute left-8 -bottom-2 w-0 h-0 border-l-[12px] border-l-transparent border-r-[12px] border-r-transparent border-t-[12px] border-t-white"></div>
        </div>

        {/* Gift Box Illustration */}
        <div className="flex justify-center mb-12">
          <div className="relative w-48 h-48">
            {/* Gift Box SVG */}
            <svg viewBox="0 0 200 200" className="w-full h-full">
              {/* Box body */}
              <rect x="40" y="80" width="120" height="100" fill="#C7B3E5" rx="4" />

              {/* Box lid */}
              <rect x="35" y="60" width="130" height="30" fill="#9B7FD4" rx="4" />

              {/* Vertical ribbon */}
              <rect x="90" y="60" width="20" height="120" fill="#7C5FB8" />

              {/* Bow left */}
              <ellipse cx="70" cy="50" rx="35" ry="25" fill="#8B6FC9" />

              {/* Bow right */}
              <ellipse cx="130" cy="50" rx="35" ry="25" fill="#8B6FC9" />

              {/* Bow center */}
              <circle cx="100" cy="50" r="12" fill="#7C5FB8" />
            </svg>
          </div>
        </div>

        {/* Nickname - 함수 이름 변경 반영 */}
        <div className="flex items-center justify-center gap-3 mb-16">
          {isEditingNickname ? (
            <div className="flex items-center gap-2">
              <Input
                value={editNicknameValue}
                onChange={(e) => setEditNicknameValue(e.target.value)}
                className="text-2xl font-bold text-center w-40"
                autoFocus
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleSaveNickname()
                  if (e.key === "Escape") handleCancelNickname()
                }}
              />
              <button
                onClick={handleSaveNickname}
                className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center hover:bg-green-200 transition-colors"
              >
                <Check className="w-5 h-5 text-green-600" />
              </button>
              <button
                onClick={handleCancelNickname}
                className="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center hover:bg-red-200 transition-colors"
              >
                <X className="w-5 h-5 text-red-600" />
              </button>
            </div>
          ) : (
            <>
              <h2 className="text-3xl font-bold text-gray-800">{nickname}</h2>
              <button
                onClick={handleEditNickname}
                className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center hover:bg-gray-300 transition-colors"
              >
                <Pencil className="w-5 h-5 text-gray-600" />
              </button>
            </>
          )}
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4">
          {/* Total Study Time */}
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mb-3">
              <Clock className="w-6 h-6 text-indigo-600" />
            </div>
            <p className="text-xs text-gray-600 mb-1 text-center">총 학습 시간</p>
            <p className="text-2xl font-bold text-gray-900">--</p>
          </div>

          {/* Consecutive Days */}
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center mb-3">
              <Flame className="w-6 h-6 text-orange-600" />
            </div>
            <p className="text-xs text-gray-600 mb-1 text-center">연속 학습일</p>
            <p className="text-2xl font-bold text-gray-900">0d</p>
          </div>

          {/* Accumulated Days */}
          <div className="flex flex-col items-center">
            <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center mb-3">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
            <p className="text-xs text-gray-600 mb-1 text-center">누적 학습일</p>
            <p className="text-2xl font-bold text-gray-900">0d</p>
          </div>
        </div>
      </div>
    </div>
  )
}
