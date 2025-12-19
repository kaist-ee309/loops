"use client"

import { usePathname, useRouter } from "next/navigation"
import { Home, BarChart3, User } from "lucide-react"
import { cn } from "@/lib/utils"

export function BottomTabNav() {
  const pathname = usePathname()
  const router = useRouter()

  const tabs = [
    { name: "홈", icon: Home, path: "/dashboard" },
    { name: "학습 통계", icon: BarChart3, path: "/statistics" },
    { name: "마이페이지", icon: User, path: "/my-page" },
  ]

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-card border-t border-border safe-area-inset-bottom z-50">
      <div className="flex justify-around items-center h-16">
        {tabs.map((tab) => {
          const Icon = tab.icon
          const isActive = pathname === tab.path
          return (
            <button
              key={tab.path}
              onClick={() => router.push(tab.path)}
              className={cn(
                "flex flex-col items-center justify-center flex-1 h-full transition-colors",
                isActive ? "text-indigo-600" : "text-muted-foreground",
              )}
            >
              <Icon className={cn("w-6 h-6", isActive && "fill-indigo-100")} />
              <span className="text-xs mt-1 font-medium">{tab.name}</span>
            </button>
          )
        })}
      </div>
    </nav>
  )
}
