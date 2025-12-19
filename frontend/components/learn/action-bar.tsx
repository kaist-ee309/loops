"use client"

import { MessageCircleQuestion, BookOpen, Mic, FileText, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"

interface ActionBarProps {
  onOtherExample: () => void
  onWrongNotes: () => void
  onAiQuestion: () => void
  onWordInfo: () => void
  onPronunciation: () => void
  otherExampleEnabled?: boolean
}

export function ActionBar({
  onOtherExample,
  onWrongNotes,
  onAiQuestion,
  onWordInfo,
  onPronunciation,
  otherExampleEnabled = true,
}: ActionBarProps) {
  const actions = [
    { icon: RefreshCw, label: "다른 예문", onClick: onOtherExample, disabled: !otherExampleEnabled },
    { icon: BookOpen, label: "오답 노트", onClick: onWrongNotes, disabled: false },
    { icon: MessageCircleQuestion, label: "AI 질문", onClick: onAiQuestion, disabled: false },
    { icon: FileText, label: "단어 정보", onClick: onWordInfo, disabled: false },
    { icon: Mic, label: "발음 진단", onClick: onPronunciation, disabled: false },
  ]

  return (
    <div className="flex justify-around py-3 border-t border-gray-100">
      {actions.map(({ icon: Icon, label, onClick, disabled }) => (
        <Button
          key={label}
          variant="ghost"
          className={`flex flex-col items-center gap-1 h-auto py-2 px-2 ${
            disabled ? "text-gray-300 cursor-not-allowed" : "text-gray-600 hover:text-indigo-600 hover:bg-indigo-50"
          }`}
          onClick={disabled ? undefined : onClick}
          disabled={disabled}
        >
          <Icon className="w-5 h-5" />
          <span className="text-[10px]">{label}</span>
        </Button>
      ))}
    </div>
  )
}
