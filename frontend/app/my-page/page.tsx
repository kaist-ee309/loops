"use client"
import { useState } from "react"
import { Button } from "@/components/ui/button"
import { ChevronRight, Sun, Bell, Volume2, Star, BookOpen, HelpCircle, Globe, Info, User, Library } from "lucide-react"
import { BottomTabNav } from "@/components/bottom-tab-nav"
import { useRouter } from "next/navigation"
import { useAuth } from "@/components/auth-provider"
import { UserDisplayName } from "@/components/user-display-name"

export default function MyPage() {
  const router = useRouter()
  const { isAuthed, logout } = useAuth()

  const settingsGroups = [
    {
      title: "설정",
      items: [
        { icon: Library, label: "단어장 선택", description: "학습에 사용할 단어장을 선택", path: "/decks/select" },
        { icon: Sun, label: "화면", description: "다크 모드 설정, 학습 화면 테마", path: "/my-page/display" },
        {
          icon: Bell,
          label: "알림",
          description: "학습 시간 및 학습 리포트, 리그 알림",
          path: "/my-page/notifications",
        },
        { icon: Volume2, label: "음성 및 효과음", description: "학습 음성 및 효과음 설정", path: "/my-page/audio" },
        { icon: Star, label: "즐겨찾기", description: "홈에 표시할 학습 모드 설정", path: "/my-page/favorites" },
        {
          icon: BookOpen,
          label: "어휘학습",
          description: "퀴즈 방식, 단어장 변경, 난이도 및 복습 단어 비율 조정",
          path: "/my-page/vocabulary",
        },
        {
          icon: HelpCircle,
          label: "고객지원",
          description: "고객센터, 수강증/출석확인 발급, 공지사항",
          path: "/my-page/support",
        },
        { icon: Globe, label: "언어", description: "기본 언어 설정", path: "/my-page/language" },
        { icon: Info, label: "업데이트 히스토리", description: "로이드가 실험 중인 기능들", path: "/my-page/updates" },
      ],
    },
  ]

  const handleLogout = async () => {
    await logout()
    router.push("/login")
  }

  return (
    <div className="min-h-screen bg-gray-100 pb-20">
      {/* Header */}
      <div className="bg-white px-4 py-4 flex items-center justify-between border-b border-gray-200">
        <h1 className="text-xl font-bold text-gray-900">
          <UserDisplayName />
        </h1>
        <Button variant="ghost" size="icon">
          <Bell className="w-5 h-5 text-yellow-500 fill-yellow-500" />
        </Button>
      </div>

      <div className="p-4 space-y-4">
        {/* Profile Button */}
        <div className="bg-white rounded-2xl overflow-hidden">
          <button
            onClick={() => router.push("/my-page/profile")}
            className="w-full flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors"
          >
            <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
              <User className="w-5 h-5 text-gray-600" />
            </div>
            <div className="flex-1 text-left">
              <div className="font-medium text-gray-900">프로필 정보</div>
              <div className="text-xs text-gray-500 mt-0.5">나의 프로필 및 학습 통계</div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
          </button>
        </div>

        {isAuthed ? (
          // Logout Button
          <div className="bg-white rounded-2xl overflow-hidden">
            <button
              onClick={handleLogout}
              className="w-full flex items-center justify-center p-4 text-red-600 font-medium hover:bg-gray-50 transition-colors"
            >
              로그아웃
            </button>
          </div>
        ) : (
          // Guest Warning Card
          <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
            <div className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-orange-500 text-white flex items-center justify-center flex-shrink-0 mt-0.5">
                ⚠
              </div>
              <div className="flex-1">
                <div className="font-bold text-orange-900 mb-1">현재 게스트 상태입니다.</div>
                <div className="text-sm text-orange-700 mb-3">
                  말해보기를 해당 기기에서 삭제하면 학습 데이터를 읽을 수 없어요! 회원가입 해서 학습 내용을 안전하게
                  보관하세요!
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <Button
                    variant="outline"
                    className="bg-white border-orange-300 text-orange-700 hover:bg-orange-50"
                    onClick={() => router.push("/login")}
                  >
                    기존 계정으로 로그인
                  </Button>
                  <Button
                    className="bg-orange-500 text-white hover:bg-orange-600"
                    onClick={() => router.push("/signup")}
                  >
                    회원가입
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Settings Sections */}
        {settingsGroups.map((group) => (
          <div key={group.title} className="bg-white rounded-2xl overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100">
              <h2 className="font-bold text-gray-900">{group.title}</h2>
            </div>
            <div className="divide-y divide-gray-100">
              {group.items.map((item) => {
                const Icon = item.icon
                return (
                  <button
                    key={item.label}
                    onClick={() => router.push(item.path)}
                    className="w-full flex items-center gap-4 p-4 hover:bg-gray-50 transition-colors"
                  >
                    <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
                      <Icon className="w-5 h-5 text-gray-600" />
                    </div>
                    <div className="flex-1 text-left">
                      <div className="font-medium text-gray-900">{item.label}</div>
                      <div className="text-xs text-gray-500 mt-0.5">{item.description}</div>
                    </div>
                    <ChevronRight className="w-5 h-5 text-gray-400 flex-shrink-0" />
                  </button>
                )
              })}
            </div>
          </div>
        ))}
      </div>

      <BottomTabNav />
    </div>
  )
}
