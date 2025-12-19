"use client"

import type React from "react"
import { useState, useEffect, useRef, useMemo, useCallback } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/button"
import { useSettings } from "@/components/settings-provider"
import { useCourseStore } from "@/store/course-store"
import { Volume2, X, Mic, Lightbulb, Repeat, Check, XIcon, HelpCircle, Eye } from "lucide-react"
import { cn } from "@/lib/utils"
import { ActionBar } from "@/components/learn/action-bar"
import { WrongNotesSheet } from "@/components/learn/sheets/wrong-notes-sheet"
import { PlaceholderSheet } from "@/components/learn/sheets/placeholder-sheet"
import { PronunciationSheet } from "@/components/learn/sheets/pronunciation-sheet"
import { saveWrongNote } from "@/lib/wrong-notes"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { AuthRequired } from "@/components/auth-required"
import {
  startSession,
  getNextCard,
  submitAnswer,
  completeSession,
  type StudyCard,
  type SessionSummary,
  type SessionCompleteResponse,
  type QuizType,
} from "@/lib/api/study"
import { toast } from "@/components/ui/use-toast"

const FSRS_RATING = {
  AGAIN: 1,
  HARD: 2,
  GOOD: 3,
  EASY: 4,
}

type Card = StudyCard

type TypingViewModel = {
  koSentence: string
  enSentenceWithBlank: string
  answer: string
  explanation?: string | null
  exampleCandidates?: Array<{ koSentence: string; enSentenceWithBlank: string }>
}

interface SheetHandlers {
  openWrongNotes: () => void
  openAiQuestion: () => void
  openWordInfo: () => void
  openPronunciation: () => void
}

interface ModeProps extends SheetHandlers {
  card: Card
  cards: Card[]
  currentIndex: number
  onRate: (rating: number) => void
  playbackSpeed: number
  onUserAnswer?: (ans: string | null) => void
}

interface TypingModeProps extends ModeProps {
  typingView: TypingViewModel
}

function RatingButtons({ onRate }: { onRate: (rating: number) => void }) {
  return (
    <div className="grid grid-cols-4 gap-2">
      <div className="flex flex-col gap-1">
        <Button
          variant="destructive"
          className="h-14 bg-red-100 text-red-600 hover:bg-red-200 hover:text-red-700 border-0"
          onClick={() => onRate(FSRS_RATING.AGAIN)}
        >
          Again
        </Button>
        <span className="text-[10px] text-center text-gray-400 font-medium">10분 후</span>
      </div>
      <div className="flex flex-col gap-1">
        <Button
          variant="secondary"
          className="h-14 bg-orange-100 text-orange-600 hover:bg-orange-200 hover:text-orange-700 border-0"
          onClick={() => onRate(FSRS_RATING.HARD)}
        >
          Hard
        </Button>
        <span className="text-[10px] text-center text-gray-400 font-medium">1시간 후</span>
      </div>
      <div className="flex flex-col gap-1">
        <Button
          variant="secondary"
          className="h-14 bg-green-100 text-green-600 hover:bg-green-200 hover:text-green-700 border-0"
          onClick={() => onRate(FSRS_RATING.GOOD)}
        >
          Good
        </Button>
        <span className="text-[10px] text-center text-gray-400 font-medium">1일 후</span>
      </div>
      <div className="flex flex-col gap-1">
        <Button
          variant="default"
          className="h-14 bg-blue-100 text-blue-600 hover:bg-blue-200 hover:text-blue-700 border-0"
          onClick={() => onRate(FSRS_RATING.EASY)}
        >
          Easy
        </Button>
        <span className="text-[10px] text-center text-gray-400 font-medium">4일 후</span>
      </div>
    </div>
  )
}

function FlashcardMode({
  card,
  onRate,
  playbackSpeed,
  openWrongNotes,
  openAiQuestion,
  openWordInfo,
  openPronunciation,
}: ModeProps) {
  const { settings } = useSettings()
  const [isFlipped, setIsFlipped] = useState(false)
  const [showTutorial, setShowTutorial] = useState(true)
  const [currentExampleIndex, setCurrentExampleIndex] = useState(0)
  const [isGeneratingExample, setIsGeneratingExample] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [showPronunciationAnalysis, setShowPronunciationAnalysis] = useState(false)
  const prevIsFlipped = useRef(false)

  const questionText = typeof card.question === "string" ? card.question : card.question.sentence

  let answerText: string
  if (card.quiz_type === "word_to_meaning") {
    answerText = card.korean_meaning
  } else if (card.quiz_type === "meaning_to_word") {
    answerText = card.english_word
  } else if (card.quiz_type === "cloze" && typeof card.question === "object") {
    answerText = card.question.answer
  } else if (card.quiz_type === "listening") {
    answerText = card.english_word
  } else {
    answerText = card.korean_meaning
  }

  const mockExamples = [
    {
      sentence: `The word "${card.english_word}" means ${card.korean_meaning}.`,
      translation: `이 단어는 ${card.korean_meaning}을 의미합니다.`,
    },
    {
      sentence: `${card.english_word}: commonly used in academic contexts.`,
      translation: `${card.english_word}: 학문적 맥락에서 흔히 사용됩니다.`,
    },
    {
      sentence: `Example: This demonstrates the meaning of ${card.english_word}.`,
      translation: `예시: ${card.english_word}의 의미를 보여줍니다.`,
    },
  ]

  useEffect(() => {
    if (isFlipped && !prevIsFlipped.current && settings.autoPlayAudio) {
      playAudioWithSettings()
    }
    prevIsFlipped.current = isFlipped
  }, [isFlipped, settings.autoPlayAudio])

  useEffect(() => {
    setIsFlipped(false)
    setCurrentExampleIndex(0)
    setShowPronunciationAnalysis(false)
  }, [card])

  const handleFlip = () => {
    setIsFlipped(!isFlipped)
    if (showTutorial) setShowTutorial(false)
  }

  const playAudioWithSettings = () => {
    if (card.audio_url) {
      const audio = new Audio(card.audio_url)
      audio.playbackRate = playbackSpeed
      audio.play()
    } else if ("speechSynthesis" in window) {
      const utterance = new SpeechSynthesisUtterance(card.english_word)
      utterance.lang = "en-US"
      utterance.rate = playbackSpeed
      window.speechSynthesis.speak(utterance)
    }
  }

  const playAudio = (e: React.MouseEvent) => {
    e.stopPropagation()
    playAudioWithSettings()
  }

  const regenerateExample = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsGeneratingExample(true)
    setTimeout(() => {
      setCurrentExampleIndex((prev) => (prev + 1) % mockExamples.length)
      setIsGeneratingExample(false)
    }, 800)
  }

  const toggleRecording = (e: React.MouseEvent) => {
    e.stopPropagation()
    setIsRecording(!isRecording)
    if (!isRecording) {
      setTimeout(() => {
        setIsRecording(false)
        setShowPronunciationAnalysis(true)
      }, 2000)
    }
  }

  const currentExample = mockExamples[currentExampleIndex]
  const hasOtherExamples = mockExamples.length > 1

  const handleOtherExample = () => {
    if (hasOtherExamples) {
      setCurrentExampleIndex((prev) => (prev + 1) % mockExamples.length)
    }
  }

  return (
    <>
      <div className="flex-1 flex items-center justify-center p-4">
        <div
          className={cn(
            "relative w-full max-w-sm aspect-[3/4] transition-all duration-500 transform-style-3d cursor-pointer",
            isFlipped ? "rotate-y-180" : "",
          )}
          onClick={handleFlip}
        >
          {/* Front of card - show question */}
          <div className="absolute inset-0 bg-white rounded-3xl shadow-xl flex flex-col items-center justify-center p-8 backface-hidden border border-gray-100">
            <span className="text-4xl font-bold text-gray-900 mb-8">{questionText}</span>
            {showTutorial && (
              <div className="absolute bottom-8 animate-bounce text-gray-400 text-sm flex flex-col items-center">
                <span>👆</span>
                <span>탭해서 뒤집기</span>
              </div>
            )}
          </div>

          {/* Back of card - show answer + details */}
          <div className="absolute inset-0 bg-white rounded-3xl shadow-xl flex flex-col p-6 backface-hidden rotate-y-180 border border-gray-100 overflow-y-auto">
            <div className="flex-1 flex flex-col items-center justify-center text-center space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-center gap-2">
                  <h2 className="text-3xl font-bold text-gray-900">{card.english_word}</h2>
                  <button
                    onClick={playAudio}
                    className="p-2 rounded-full bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
                  >
                    <Volume2 className="w-5 h-5" />
                  </button>
                </div>
                <p className="text-gray-500 font-mono text-sm">{card.pronunciation_ipa ?? ""}</p>
              </div>
              <div className="flex gap-1 text-xs">
                <span className="px-3 py-1 rounded-full bg-indigo-100 text-indigo-600 font-medium">
                  {playbackSpeed}x
                </span>
              </div>
              <div className="w-12 h-1 bg-gray-100 rounded-full" />
              <div className="space-y-1">
                <p className="text-2xl font-bold text-indigo-600">{answerText}</p>
              </div>
              <div className="bg-gray-50 p-4 rounded-xl w-full text-left space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-gray-400 font-medium">예문 {currentExampleIndex + 1}</span>
                  <button
                    onClick={regenerateExample}
                    disabled={isGeneratingExample}
                    className="flex items-center gap-1 text-xs text-indigo-600 hover:text-indigo-700 disabled:opacity-50"
                  >
                    <Repeat className={cn("w-3 h-3", isGeneratingExample && "animate-spin")} />
                    {isGeneratingExample ? "생성 중..." : "새 예문"}
                  </button>
                </div>
                <p className="text-gray-800 font-medium">&quot;{currentExample.sentence}&quot;</p>
                <p className="text-gray-500 text-sm">{currentExample.translation}</p>
              </div>
              <button
                onClick={toggleRecording}
                className={cn(
                  "flex items-center gap-2 px-4 py-2 rounded-full transition-all",
                  isRecording ? "bg-red-100 text-red-600 animate-pulse" : "bg-gray-100 text-gray-600 hover:bg-gray-200",
                )}
              >
                <Mic className="w-4 h-4" />
                <span className="text-sm font-medium">{isRecording ? "녹음 중..." : "발음 연습"}</span>
              </button>
              {showPronunciationAnalysis && (
                <div className="bg-indigo-50 p-4 rounded-xl w-full text-left space-y-2 border border-indigo-100">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-indigo-900">발음 분석</span>
                    <span className="text-2xl font-bold text-indigo-600">85/100</span>
                  </div>
                  <div className="space-y-1">
                    <div className="text-xs text-indigo-700">
                      <Lightbulb className="w-3 h-3 inline mr-1" />
                      발음 팁
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation()
                      setShowPronunciationAnalysis(false)
                    }}
                    className="text-xs text-indigo-600 hover:underline"
                  >
                    닫기
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {isFlipped && (
        <ActionBar
          onOtherExample={handleOtherExample}
          onWrongNotes={openWrongNotes}
          onAiQuestion={openAiQuestion}
          onWordInfo={openWordInfo}
          onPronunciation={openPronunciation}
          otherExampleEnabled={hasOtherExamples}
        />
      )}

      {isFlipped && (
        <div className="shrink-0 p-4 pb-8 bg-white shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
          <Button className="w-full py-6 text-lg font-medium" onClick={() => onRate(FSRS_RATING.GOOD)}>
            제출하고 다음으로
          </Button>
        </div>
      )}
    </>
  )
}

function MultipleChoiceMode({
  card,
  currentIndex,
  onRate,
  openWrongNotes,
  openAiQuestion,
  openWordInfo,
  openPronunciation,
  onUserAnswer,
}: ModeProps) {
  const [selectedChoice, setSelectedChoice] = useState<string | null>(null)
  const [isRevealed, setIsRevealed] = useState(false)
  const [wasIncorrectSaved, setWasIncorrectSaved] = useState(false)
  const [exampleIndex, setExampleIndex] = useState(0)

  useEffect(() => {
    setSelectedChoice(null)
    setIsRevealed(false)
    setWasIncorrectSaved(false)
    setExampleIndex(0)
  }, [card, currentIndex])

  const choices = useMemo(() => {
    if (!card.options || card.options.length === 0) {
      return []
    }
    return [...card.options].sort(() => Math.random() - 0.5)
  }, [card])

  const mockExamples = useMemo(
    () => [
      { sentence: `The word "${card.english_word}" means ${card.korean_meaning}.` },
      { sentence: `${card.english_word}: commonly used in academic contexts.` },
      { sentence: `Example: This demonstrates the meaning of ${card.english_word}.` },
    ],
    [card],
  )

  const currentExample = mockExamples[exampleIndex]
  const hasOtherExamples = mockExamples.length > 1

  const handleReveal = () => {
    if (!selectedChoice) return
    setIsRevealed(true)
    onUserAnswer?.(selectedChoice)
    if (selectedChoice && selectedChoice !== card.korean_meaning && !wasIncorrectSaved) {
      setWasIncorrectSaved(true)
      saveWrongNote({
        word: card.english_word,
        userAnswer: selectedChoice,
        correctAnswer: card.korean_meaning,
        koSentence: "",
        enSentenceWithBlank: "",
      })
    }
  }

  const handleOtherExample = () => {
    if (hasOtherExamples) {
      setExampleIndex((prev) => (prev + 1) % mockExamples.length)
    }
  }

  const isCorrect = selectedChoice === card.korean_meaning
  const isAnswered = isRevealed

  const questionText = typeof card.question === "string" ? card.question : card.question.sentence

  if (choices.length === 0) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="text-center space-y-4 max-w-md">
          <div className="text-6xl">⚠️</div>
          <h2 className="text-xl font-bold text-gray-900">선택지를 불러올 수 없습니다</h2>
          <p className="text-gray-600">이 문제에 선택지가 없습니다. flip 모드로 학습해주세요.</p>
          <Button onClick={() => onRate(FSRS_RATING.GOOD)}>다음 카드로</Button>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="flex-1 flex flex-col items-center justify-center p-4 overflow-y-auto">
        <div className="w-full max-w-sm space-y-6">
          <div className="bg-white rounded-3xl shadow-xl p-8 text-center border border-gray-100">
            <span className="text-xs text-gray-400 mb-2 block">다음 단어의 뜻은?</span>
            <span className="text-4xl font-bold text-gray-900">{questionText}</span>
          </div>

          <div className="space-y-3">
            {choices.map((choice, idx) => {
              const isSelected = selectedChoice === choice
              const isCorrectChoice = choice === card.korean_meaning

              let buttonClass = "bg-white border-gray-200 text-gray-700 hover:border-indigo-300"
              if (isRevealed) {
                if (isCorrectChoice) {
                  buttonClass = "bg-green-50 border-green-500 text-green-700"
                } else if (isSelected && !isCorrectChoice) {
                  buttonClass = "bg-red-50 border-red-500 text-red-700"
                }
              } else if (isSelected) {
                buttonClass = "bg-indigo-50 border-indigo-500 text-indigo-700"
              }

              return (
                <button
                  key={idx}
                  onClick={() => !isRevealed && setSelectedChoice(choice)}
                  disabled={isRevealed}
                  className={cn(
                    "w-full p-4 rounded-xl border-2 text-left font-medium transition-all flex items-center justify-between",
                    buttonClass,
                  )}
                >
                  <span>{choice}</span>
                  {isRevealed && isCorrectChoice && <Check className="w-5 h-5 text-green-600" />}
                  {isRevealed && isSelected && !isCorrectChoice && <XIcon className="w-5 h-5 text-red-600" />}
                </button>
              )
            })}
          </div>

          {isAnswered && (
            <div className="mt-4 bg-gray-50 rounded-xl p-4 text-sm text-gray-700">
              <span className="text-xs text-gray-400 block mb-1">예문</span>
              <p>{currentExample.sentence}</p>
            </div>
          )}
        </div>
      </div>

      {isAnswered && (
        <ActionBar
          onOtherExample={handleOtherExample}
          onWrongNotes={openWrongNotes}
          onAiQuestion={openAiQuestion}
          onWordInfo={openWordInfo}
          onPronunciation={openPronunciation}
          otherExampleEnabled={hasOtherExamples}
        />
      )}

      <div className="shrink-0 p-4 pb-8 bg-white shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
        {!isRevealed ? (
          <Button className="w-full py-6 text-lg font-medium" onClick={handleReveal} disabled={!selectedChoice}>
            정답 확인
          </Button>
        ) : (
          <div className="space-y-4">
            <div
              className={cn(
                "text-center py-2 rounded-lg font-medium",
                isCorrect ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700",
              )}
            >
              {isCorrect ? "정답입니다!" : `오답! 정답: ${card.korean_meaning}`}
            </div>
            <RatingButtons onRate={onRate} />
          </div>
        )}
      </div>
    </>
  )
}

function SentenceTypingMode({
  card,
  typingView,
  onRate,
  openWrongNotes,
  openAiQuestion,
  openWordInfo,
  openPronunciation,
  onUserAnswer,
}: TypingModeProps) {
  const router = useRouter()
  const [typedSuffix, setTypedSuffix] = useState("")
  const [status, setStatus] = useState<"idle" | "correct" | "incorrect">("idle")
  const [revealedCount, setRevealedCount] = useState(0)
  const [usedHint, setUsedHint] = useState(false)
  const [showAnswer, setShowAnswer] = useState(false)
  const [wasIncorrect, setWasIncorrect] = useState(false)
  const [exampleIndex, setExampleIndex] = useState(0)
  const [showError, setShowError] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  const answer = (typingView.answer || "").trim()

  const examples =
    typingView.exampleCandidates && typingView.exampleCandidates.length > 0
      ? typingView.exampleCandidates
      : [
          {
            koSentence: typingView.koSentence,
            enSentenceWithBlank: typingView.enSentenceWithBlank,
          },
        ]

  const currentExample = useMemo(() => {
    if (examples.length === 0) {
      return { koSentence: typingView.koSentence, enSentenceWithBlank: typingView.enSentenceWithBlank }
    }
    const idx = exampleIndex % examples.length
    return examples[idx]
  }, [examples, exampleIndex, typingView.koSentence, typingView.enSentenceWithBlank])

  if (!answer) {
    return (
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="text-center space-y-4 max-w-md">
          <div className="text-6xl">⚠️</div>
          <h2 className="text-xl font-bold text-gray-900">타이핑 문제를 표시할 수 없습니다</h2>
          <p className="text-gray-600">홈으로 돌아가 다시 시도해주세요.</p>
          <Button onClick={() => router.push("/dashboard")}>홈으로</Button>
        </div>
      </div>
    )
  }

  const hintPrefix = answer.slice(0, revealedCount)
  const fullInput = hintPrefix + typedSuffix
  const normalizedAnswer = answer.trim().toLowerCase()

  const evaluateInput = useCallback(
    (nextFullInput: string) => {
      const trimmed = nextFullInput.trim().toLowerCase()

      // 1) Empty input → idle
      if (!trimmed) {
        setStatus("idle")
        setShowError(false)
        return
      }

      // 2) Correct answer
      if (trimmed === normalizedAnswer) {
        setStatus("correct")
        setShowError(false)
        inputRef.current?.blur()
        return
      }

      // 3) Still a prefix of the answer (in progress)
      if (normalizedAnswer.startsWith(trimmed)) {
        setStatus("idle")
        setShowError(false)
        return
      }

      // 4) Definite incorrect
      setStatus("incorrect")
      setShowError(true)

      if (!wasIncorrect) {
        setWasIncorrect(true)
      }
    },
    [normalizedAnswer, wasIncorrect],
  )

  useEffect(() => {
    setTypedSuffix("")
    setStatus("idle")
    setRevealedCount(0)
    setUsedHint(false)
    setShowAnswer(false)
    setWasIncorrect(false)
    setExampleIndex(0)
    setShowError(false)
    inputRef.current?.focus()
  }, [card])

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault()
    if (!fullInput.trim()) return
    evaluateInput(fullInput)
  }

  const handleInputChange = (value: string) => {
    // No hints yet - treat entire input as suffix
    if (revealedCount === 0) {
      setTypedSuffix(value)
      evaluateInput(value)
      onUserAnswer?.(value)
      return
    }

    const prefix = hintPrefix

    // User trying to delete into prefix - clear suffix only
    if (value.length <= prefix.length) {
      setTypedSuffix("")
      evaluateInput(prefix)
      onUserAnswer?.(prefix)
      return
    }

    // Input starts with prefix - extract suffix
    if (value.startsWith(prefix)) {
      const nextSuffix = value.slice(prefix.length)
      setTypedSuffix(nextSuffix)
      const nextFull = prefix + nextSuffix
      evaluateInput(nextFull)
      onUserAnswer?.(nextFull)
      return
    }

    // User modified prefix area - ignore (keep current suffix), still evaluate
    evaluateInput(fullInput)
    onUserAnswer?.(fullInput)
  }

  const handleHint = () => {
    if (revealedCount >= answer.length) return

    const newHintChar = answer[revealedCount]
    let nextSuffix = typedSuffix

    // If user already typed this char at the start of suffix, remove it
    if (typedSuffix.length > 0 && typedSuffix[0].toLowerCase() === newHintChar.toLowerCase()) {
      nextSuffix = typedSuffix.slice(1)
      setTypedSuffix(nextSuffix)
    }

    const nextRevealedCount = Math.min(revealedCount + 1, answer.length)
    setRevealedCount(nextRevealedCount)
    setUsedHint(true)

    // Evaluate with updated prefix + suffix
    const nextFullInput = answer.slice(0, nextRevealedCount) + nextSuffix
    evaluateInput(nextFullInput)
  }

  const handleShowAnswer = () => {
    setShowAnswer(true)
    onUserAnswer?.(answer)
  }

  const handleOtherExample = () => {
    if (examples.length > 1) {
      setExampleIndex((prev) => prev + 1)
    }
  }

  const blankDisplay = (() => {
    const visible = fullInput
    const maxLen = answer.length
    if (visible.length >= maxLen) return visible.slice(0, maxLen)
    const remaining = maxLen - visible.length
    return visible + "_".repeat(remaining)
  })()

  const renderSentence = () => {
    const sentence = currentExample.enSentenceWithBlank || "____"
    const parts = sentence.split("____")
    if (parts.length !== 2) {
      return <span>{sentence}</span>
    }

    return (
      <span className="text-xl leading-relaxed">
        {parts[0]}
        {showAnswer || status === "correct" ? (
          <span
            className={cn(
              "font-bold border-b-2 px-1",
              status === "correct" ? "text-green-600 border-green-500" : "text-indigo-600 border-indigo-500",
            )}
          >
            {answer}
          </span>
        ) : (
          <span
            className={cn(
              "inline-block min-w-[80px] border-b-2 px-2 py-1 mx-1 font-mono",
              status === "incorrect"
                ? "border-red-400 bg-red-50 text-red-700"
                : "border-indigo-300 bg-indigo-50 text-gray-900",
            )}
          >
            {blankDisplay}
          </span>
        )}
        {parts[1]}
      </span>
    )
  }

  const hasOtherExamples =
    examples.length > 1

  const showInputUI = status !== "correct" && !showAnswer
  const showActionBar = status === "correct" || showAnswer

  return (
    <>
      <div className="flex-1 flex flex-col overflow-y-auto p-4 bg-sky-50">
        <div className="bg-sky-100 rounded-2xl p-4 mb-4">
          <p className="text-lg text-gray-800 leading-relaxed">
            {currentExample.koSentence}
          </p>
        </div>

        {showError && (
          <div className="bg-red-100 text-red-700 rounded-xl p-3 mb-4 text-center font-medium">
            철자가 달라요. 다시 입력해 보거나, 필요하면 &apos;정답 보기&apos;를 눌러 확인해 보세요.
          </div>
        )}

        <div className="bg-white rounded-2xl p-6 shadow-sm mb-4">{renderSentence()}</div>
      </div>

      <div className="shrink-0 bg-white shadow-[0_-4px_20px_rgba(0,0,0,0.05)]">
        {showInputUI ? (
          <div className="p-4 pb-8 space-y-4">
            <input
              ref={inputRef}
              type="text"
              value={fullInput}
              onChange={(e) => handleInputChange(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              placeholder="영단어를 입력하세요"
              className={cn(
                "w-full p-4 rounded-xl border-2 text-center text-xl font-medium outline-none transition-colors",
                status === "incorrect"
                  ? "border-red-400 bg-red-50 text-red-700 focus:border-red-500"
                  : "border-gray-200 focus:border-indigo-500",
              )}
              autoFocus
            />

            <div className="flex flex-wrap gap-2">
              {revealedCount < answer.length && (
                <Button
                  variant="outline"
                  className="min-w-0 flex-1 basis-[calc(50%-0.25rem)] py-3 text-sm text-indigo-600 border-indigo-200 bg-transparent"
                  onClick={handleHint}
                >
                  <HelpCircle className="w-4 h-4 mr-1 shrink-0" />
                  <span className="truncate">
                    힌트 ({revealedCount}/{answer.length})
                  </span>
                </Button>
              )}

              {usedHint && (
                <Button
                  variant="outline"
                  className="min-w-0 flex-1 basis-[calc(50%-0.25rem)] py-3 text-sm text-orange-600 border-orange-200 bg-transparent"
                  onClick={handleShowAnswer}
                >
                  <Eye className="w-4 h-4 mr-1 shrink-0" />
                  <span className="truncate">정답 보기</span>
                </Button>
              )}
            </div>
          </div>
        ) : (
          <div className="space-y-0">
            <div className="p-4">
              {status === "correct" && (
                <div className="bg-green-100 text-green-700 rounded-xl p-3 text-center font-medium flex items-center justify-center gap-2">
                  <Check className="w-5 h-5" />
                  정답입니다!
                </div>
              )}
              {showAnswer && status !== "correct" && (
                <div className="bg-gray-100 rounded-xl p-4 text-center">
                  <p className="text-sm text-gray-500 mb-1">정답</p>
                  <p className="text-2xl font-bold text-indigo-600">{answer}</p>
                  {typingView.explanation && <p className="text-sm text-gray-600 mt-2">{typingView.explanation}</p>}
                </div>
              )}
            </div>

            {showActionBar && (
              <ActionBar
                onOtherExample={handleOtherExample}
                onWrongNotes={openWrongNotes}
                onAiQuestion={openAiQuestion}
                onWordInfo={openWordInfo}
                onPronunciation={openPronunciation}
                otherExampleEnabled={hasOtherExamples}
              />
            )}

            <div className="p-4 pt-0 pb-8">
              <RatingButtons onRate={onRate} />
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default function LearnPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const { settings } = useSettings()
  const { studyMode } = useCourseStore()

  const [sessionId, setSessionId] = useState<string | null>(null)
  const [currentCard, setCurrentCard] = useState<StudyCard | null>(null)
  const [cardsRemaining, setCardsRemaining] = useState(0)
  const [cardsCompleted, setCardsCompleted] = useState(0)
  const [startedAt, setStartedAt] = useState<string>("")
  const [studiedCount, setStudiedCount] = useState(0)
  const [correctCount, setCorrectCount] = useState(0)
  const [isLoadingSession, setIsLoadingSession] = useState(true)
  const [sessionSummary, setSessionSummary] = useState<SessionSummary | null>(null)
  const [sessionComplete, setSessionComplete] = useState<SessionCompleteResponse | null>(null)
  const [showSummary, setShowSummary] = useState(false)

  const [pendingUserAnswer, setPendingUserAnswer] = useState<string | null>(null)

  const [wrongNotesOpen, setWrongNotesOpen] = useState(false)
  const [aiQuestionOpen, setAiQuestionOpen] = useState(false)
  const [wordInfoOpen, setWordInfoOpen] = useState(false)
  const [pronunciationOpen, setPronunciationOpen] = useState(false)

  const [exitDialogOpen, setExitDialogOpen] = useState(false)
  const retryPayloadRef = useRef<{ payload: { session_id: string; card_id: number; answer: string }; rating: number } | null>(
    null,
  )
  const [submitError, setSubmitError] = useState<string | null>(null)

  const quizType: QuizType =
    studyMode === "mcq"
      ? "word_to_meaning"
      : studyMode === "typing"
        ? "cloze"
        : "word_to_meaning"

  useEffect(() => {
    const initSession = async () => {
      try {
        const urlSessionId = searchParams.get("sessionId")

        let activeSessionId: string

        if (urlSessionId) {
          activeSessionId = urlSessionId
          setSessionId(urlSessionId)
        } else {
          const response = await startSession({
            new_cards_limit: 20,
            review_cards_limit: 50,
          })
          activeSessionId = response.session_id
          setSessionId(response.session_id)
          setStartedAt(response.started_at)
        }

        const cardResponse = await getNextCard(activeSessionId, quizType)
        setCurrentCard(cardResponse.card)
        setCardsRemaining(cardResponse.cards_remaining)
        setCardsCompleted(cardResponse.cards_completed)
      } catch (error) {
        console.error("[v0] Session init error:", error)
      } finally {
        setIsLoadingSession(false)
      }
    }

    initSession()
  }, [searchParams, quizType, studyMode])

  useEffect(() => {
    setPendingUserAnswer(null)
  }, [currentCard?.id])

  const sheetHandlers: SheetHandlers = {
    openWrongNotes: () => setWrongNotesOpen(true),
    openAiQuestion: () => setAiQuestionOpen(true),
    openWordInfo: () => setWordInfoOpen(true),
    openPronunciation: () => setPronunciationOpen(true),
  }

  const total = cardsCompleted + cardsRemaining
  const progress = total > 0 ? (cardsCompleted / total) * 100 : 0
  const remainingCount = cardsRemaining

  const remainingLabel =
    remainingCount > 0
      ? `${remainingCount}문제를 풀어야 연속 학습을 달성할 수 있어요!`
      : "지금 나가도 오늘 목표는 이미 달성했어요!"

  type SubmitJob = {
    payload: { session_id: string; card_id: number; answer: string }
    rating: number
    card: StudyCard
  }

  const runSubmission = async (job: SubmitJob) => {
    const answerResponse = await submitAnswer(job.payload)

    setStudiedCount((prev) => prev + 1)
    if (job.rating !== FSRS_RATING.AGAIN) {
      setCorrectCount((prev) => prev + 1)
    }

    if (!answerResponse.is_correct && studyMode !== "flip") {
      saveWrongNote({
        word: job.card.english_word,
        meaning: job.card.korean_meaning,
        userAnswer: answerResponse.user_answer,
      })
    }

    const cardResponse = await getNextCard(job.payload.session_id, quizType)

    if (!cardResponse.card || cardResponse.cards_remaining === 0) {
      const complete = await completeSession(job.payload.session_id)
      setSessionComplete(complete)
      setSessionSummary(complete.session_summary)
      setShowSummary(true)
    } else {
      setTimeout(() => {
        setCurrentCard(cardResponse.card)
        setCardsRemaining(cardResponse.cards_remaining)
        setCardsCompleted(cardResponse.cards_completed)
      }, 300)
    }
    setSubmitError(null)
    retryPayloadRef.current = null
    setPendingUserAnswer(null)
  }

  const buildTypingView = (card: StudyCard): TypingViewModel => {
    const fromObject = (obj: Record<string, unknown>, key: string) =>
      typeof obj[key] === "string" ? (obj[key] as string) : null

    const ensureBlank = (text: string, targetAnswer: string) => {
      if (!text) return "____"
      if (text.includes("____")) return text
      if (targetAnswer && text.includes(targetAnswer)) {
        return text.replace(targetAnswer, "____")
      }
      return `${text} ____`
    }

    let answer = (card.english_word || card.korean_meaning || "").trim()
    let koSentence = (card.korean_meaning || "").trim()
    let enSentenceWithBlank = ""
    let explanation: string | null = null
    let exampleCandidates: Array<{ koSentence: string; enSentenceWithBlank: string }> | undefined

    if (card.question && typeof card.question === "object") {
      const q = card.question as Record<string, unknown>
      const maybeAnswer = fromObject(q, "answer") || fromObject(q, "target") || fromObject(q, "response")
      if (maybeAnswer) {
        answer = maybeAnswer.trim()
      }
      const maybeKo =
        fromObject(q, "koSentence") || fromObject(q, "ko_sentence") || fromObject(q, "korean_sentence") || koSentence
      if (maybeKo) {
        koSentence = maybeKo
      }
      const maybeEn =
        fromObject(q, "enSentenceWithBlank") ||
        fromObject(q, "en_sentence_with_blank") ||
        fromObject(q, "sentence") ||
        fromObject(q, "en_sentence")
      if (maybeEn) {
        enSentenceWithBlank = ensureBlank(maybeEn, answer)
      }
      const maybeExplanation =
        fromObject(q, "explanation") || fromObject(q, "hint") || fromObject(q, "detail") || null
      explanation = maybeExplanation

      if (Array.isArray((q as Record<string, unknown>).exampleCandidates)) {
        exampleCandidates = (
          q as { exampleCandidates: Array<{ koSentence: string; enSentenceWithBlank: string }> }
        ).exampleCandidates.map((c) => ({
          koSentence: (c.koSentence || koSentence || "").trim(),
          enSentenceWithBlank: ensureBlank(c.enSentenceWithBlank, answer),
        }))
      }
    } else if (typeof card.question === "string") {
      enSentenceWithBlank = ensureBlank(card.question, answer)
    }

    if (!enSentenceWithBlank) {
      enSentenceWithBlank = "____"
    }
    if (!koSentence) {
      koSentence = "문맥 정보가 제공되지 않았습니다."
    }
    if (!exampleCandidates || exampleCandidates.length === 0) {
      exampleCandidates = [{ koSentence, enSentenceWithBlank }]
    }

    return {
      koSentence,
      enSentenceWithBlank,
      answer,
      explanation,
      exampleCandidates,
    }
  }

  const handleRate = async (rating: number) => {
    if (!sessionId || !currentCard) return

    const allowMcqWithoutSelection = studyMode === "mcq" && (!currentCard.options || currentCard.options.length === 0)

    if (studyMode === "mcq" && !pendingUserAnswer && !allowMcqWithoutSelection) {
      return
    }
    if (studyMode === "typing" && !pendingUserAnswer) {
      return
    }

    let answer: string

    if (pendingUserAnswer) {
      answer = pendingUserAnswer
    } else {
      if (currentCard.quiz_type === "word_to_meaning") {
        answer = currentCard.korean_meaning || currentCard.english_word
      } else if (currentCard.quiz_type === "meaning_to_word") {
        answer = currentCard.english_word || currentCard.korean_meaning
      } else if (
        currentCard.quiz_type === "cloze" &&
        typeof currentCard.question === "object" &&
        currentCard.question !== null &&
        "answer" in currentCard.question &&
        typeof (currentCard.question as Record<string, unknown>).answer === "string"
      ) {
        answer = (currentCard.question as { answer: string }).answer
      } else {
        answer = currentCard.english_word || currentCard.korean_meaning
      }
    }
    if (!answer) {
      answer = ""
    }

    const submitPayload: SubmitJob = {
      payload: {
        session_id: sessionId,
        card_id: currentCard.id,
        answer,
      },
      rating,
      card: currentCard,
    }

    try {
      await runSubmission(submitPayload)
    } catch (error) {
      retryPayloadRef.current = submitPayload
      setSubmitError("서버 오류로 제출에 실패했습니다. 다시 시도해주세요.")
      toast({
        title: "제출에 실패했습니다",
        description: "서버 오류로 제출하지 못했습니다. 다시 시도해주세요.",
        variant: "destructive",
      })
    }
  }

  const handleRetrySubmit = async () => {
    const job = retryPayloadRef.current
    if (!job) return
    try {
      await runSubmission(job)
    } catch (error) {
      setSubmitError("재시도에 실패했습니다. 네트워크를 확인한 뒤 다시 시도해주세요.")
      toast({
        title: "재시도에 실패했습니다",
        description: "네트워크 상태를 확인한 뒤 다시 시도해주세요.",
        variant: "destructive",
      })
    }
  }

  const handleExit = () => {
    setExitDialogOpen(false)
    router.push("/dashboard")
  }

  if (isLoadingSession) {
    return (
      <AuthRequired>
        <div className="flex h-screen flex-col overflow-hidden bg-gradient-to-b from-blue-50 to-purple-50">
          <div className="flex items-center justify-center flex-1">
            <div className="text-center">
              <div className="text-lg font-medium text-gray-700">학습 세션을 준비하는 중...</div>
            </div>
          </div>
        </div>
      </AuthRequired>
    )
  }

  if (showSummary && sessionSummary) {
    const accuracyPct =
      sessionSummary.accuracy <= 1 ? Math.round(sessionSummary.accuracy * 100) : Math.round(sessionSummary.accuracy)

    return (
      <AuthRequired>
        <div className="flex h-screen flex-col overflow-hidden bg-gradient-to-b from-blue-50 to-purple-50">
          <div className="flex items-center justify-center flex-1 p-6">
            <div className="bg-white rounded-2xl shadow-lg p-8 max-w-md w-full space-y-6">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-gray-900">학습 완료!</h2>
                <p className="text-gray-600 mt-2">오늘도 고생하셨습니다</p>
              </div>

              <div className="space-y-3">
                <div className="flex justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">학습한 카드</span>
                  <span className="font-semibold text-gray-900">{sessionSummary.total_cards}개</span>
                </div>
                {studyMode !== "flip" && (
                  <>
                    <div className="flex justify-between p-4 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">정답</span>
                      <span className="font-semibold text-green-600">{sessionSummary.correct}개</span>
                    </div>
                    <div className="flex justify-between p-4 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">오답</span>
                      <span className="font-semibold text-red-600">{sessionSummary.wrong}개</span>
                    </div>
                    <div className="flex justify-between p-4 bg-gray-50 rounded-lg">
                      <span className="text-gray-600">정답률</span>
                      <span className="font-semibold text-gray-900">{accuracyPct}%</span>
                    </div>
                  </>
                )}
                <div className="flex justify-between p-4 bg-gray-50 rounded-lg">
                  <span className="text-gray-600">학습 시간</span>
                  <span className="font-semibold text-gray-900">
                    {Math.floor(sessionSummary.duration_seconds / 60)}분
                  </span>
                </div>
                {sessionComplete?.xp && (
                  <div className="flex justify-between p-4 bg-indigo-50 rounded-lg">
                    <span className="text-indigo-900 font-medium">획득 경험치</span>
                    <span className="font-bold text-indigo-600">{sessionComplete.xp.total_xp} XP</span>
                  </div>
                )}
              </div>

              <Button onClick={() => router.push("/dashboard")} className="w-full h-12 text-lg">
                홈으로
              </Button>
            </div>
          </div>
        </div>
      </AuthRequired>
    )
  }

  if (!currentCard) {
    return (
      <AuthRequired>
        <div className="flex h-screen flex-col overflow-hidden bg-gradient-to-b from-blue-50 to-purple-50">
          <div className="flex items-center justify-center flex-1">
            <div className="text-center">
              <div className="text-lg font-medium text-gray-700">카드를 불러올 수 없습니다</div>
              <Button onClick={() => router.push("/dashboard")} className="mt-4">
                홈으로
              </Button>
            </div>
          </div>
        </div>
      </AuthRequired>
    )
  }

  const typingView = currentCard ? buildTypingView(currentCard) : null

  const modeProps: ModeProps = {
    card: currentCard,
    cards: [currentCard],
    currentIndex: 0,
    onRate: handleRate,
    playbackSpeed: settings.playbackSpeed,
    onUserAnswer: setPendingUserAnswer,
    ...sheetHandlers,
  }

  return (
    <AuthRequired>
      <div className="h-screen bg-gray-100 flex flex-col overflow-hidden">
        <div className="bg-white px-4 py-3 flex items-center justify-between shadow-sm z-10 shrink-0">
          <Button variant="ghost" size="icon" onClick={() => setExitDialogOpen(true)}>
            <X className="w-5 h-5 text-gray-500" />
          </Button>
          <div className="flex-1 mx-4">
            <div className="flex justify-between text-xs text-gray-500 mb-1">
              <span>오늘의 학습</span>
              <span>
                {total - cardsRemaining} / {total}
              </span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500 transition-all duration-300" style={{ width: `${progress}%` }} />
            </div>
          </div>
          <div className="w-10" />
        </div>

        {submitError && (
          <div className="px-4 pt-3">
            <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-3 flex items-center justify-between gap-3">
              <span className="text-sm">{submitError}</span>
              <div className="flex gap-2 shrink-0">
                <Button size="sm" variant="destructive" onClick={handleRetrySubmit}>
                  재시도
                </Button>
                <Button size="sm" variant="outline" onClick={() => setSubmitError(null)}>
                  닫기
                </Button>
              </div>
            </div>
          </div>
        )}

        {studyMode === "flip" && currentCard && <FlashcardMode {...modeProps} />}
        {studyMode === "mcq" && currentCard && <MultipleChoiceMode {...modeProps} />}
        {studyMode === "typing" && currentCard && typingView && (
          <SentenceTypingMode {...modeProps} typingView={typingView} />
        )}
        {studyMode === "typing" && currentCard && !typingView && (
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center space-y-4 max-w-md">
              <div className="text-6xl">⚠️</div>
              <h2 className="text-xl font-bold text-gray-900">타이핑 문제를 표시할 수 없습니다</h2>
              <p className="text-gray-600">홈으로 돌아가 다시 시도해주세요.</p>
              <Button onClick={() => router.push("/dashboard")}>홈으로</Button>
            </div>
          </div>
        )}
        {studyMode !== "flip" && studyMode !== "mcq" && studyMode !== "typing" && (
          <div className="flex-1 flex items-center justify-center p-6">
            <div className="text-center space-y-4 max-w-md">
              <div className="text-6xl">⚠️</div>
              <h2 className="text-xl font-bold text-gray-900">지원되지 않는 학습 모드입니다</h2>
              <p className="text-gray-600">홈으로 돌아가 다시 시도해주세요.</p>
              <Button onClick={() => router.push("/dashboard")}>홈으로</Button>
            </div>
          </div>
        )}

        <WrongNotesSheet open={wrongNotesOpen} onOpenChange={setWrongNotesOpen} />
        <PlaceholderSheet open={aiQuestionOpen} onOpenChange={setAiQuestionOpen} title="AI 질문 답변" />
        <PlaceholderSheet open={wordInfoOpen} onOpenChange={setWordInfoOpen} title="단어 정보" />
        {currentCard && (
          <PronunciationSheet
            open={pronunciationOpen}
            onOpenChange={setPronunciationOpen}
            targetWord={currentCard.english_word}
          />
        )}

        <AlertDialog open={exitDialogOpen} onOpenChange={setExitDialogOpen}>
          <AlertDialogContent className="max-w-sm rounded-2xl">
            <AlertDialogHeader className="text-center">
              <AlertDialogTitle className="text-lg font-bold">이대로 가시겠어요?</AlertDialogTitle>
              <AlertDialogDescription className="mt-2 text-sm text-gray-600">{remainingLabel}</AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter className="flex flex-row gap-2 sm:flex-row">
              <AlertDialogAction className="flex-1 bg-gray-200 text-gray-700 hover:bg-gray-300" onClick={handleExit}>
                나가기
              </AlertDialogAction>
              <AlertDialogAction className="flex-1" onClick={() => setExitDialogOpen(false)}>
                이어서 하기
              </AlertDialogAction>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </AuthRequired>
  )
}
