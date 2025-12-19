"use client"

import { useState, useEffect, useRef } from "react"
import { Mic, Volume2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"

interface PronunciationSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  targetWord?: string
}

type PermissionState = "unknown" | "granted" | "denied"
type RecordState = "idle" | "recording" | "recorded"

// Mock phoneme breakdown for demonstration
function getPhonemes(word: string): string[] {
  const phonemeMap: Record<string, string[]> = {
    back: ["b", "æ", "k"],
    suspect: ["s", "ʌ", "s", "p", "ɛ", "k", "t"],
    innovation: ["ɪ", "n", "ə", "v", "eɪ", "ʃ", "ə", "n"],
    resilience: ["r", "ɪ", "z", "ɪ", "l", "i", "ə", "n", "s"],
  }
  return phonemeMap[word.toLowerCase()] || word.split("")
}

// Mock IPA for word
function getIPA(word: string): string {
  const ipaMap: Record<string, string> = {
    back: "'bæk",
    suspect: "sə'spɛkt",
    innovation: "ˌɪnəˈveɪʃən",
    resilience: "rɪˈzɪliəns",
  }
  return ipaMap[word.toLowerCase()] || `/${word}/`
}

export function PronunciationSheet({ open, onOpenChange, targetWord }: PronunciationSheetProps) {
  const [permission, setPermission] = useState<PermissionState>("unknown")
  const [recordState, setRecordState] = useState<RecordState>("idle")
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [score, setScore] = useState<number | null>(null)
  const [phonemeScores, setPhonemeScores] = useState<number[]>([])
  const [isPlaying, setIsPlaying] = useState(false)
  const [isPlayingNative, setIsPlayingNative] = useState(false)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<BlobPart[]>([])
  const streamRef = useRef<MediaStream | null>(null)

  const phonemes = targetWord ? getPhonemes(targetWord) : []
  const ipa = targetWord ? getIPA(targetWord) : ""

  // Cleanup on close
  useEffect(() => {
    if (!open) {
      setRecordState("idle")
      setScore(null)
      setPhonemeScores([])
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
        setAudioUrl(null)
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop())
        streamRef.current = null
      }
      mediaRecorderRef.current = null
      chunksRef.current = []
    }
  }, [open, audioUrl])

  const requestPermission = async () => {
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      setPermission("denied")
      return false
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      streamRef.current = stream
      setPermission("granted")
      return true
    } catch (err) {
      console.error("Microphone permission denied:", err)
      setPermission("denied")
      return false
    }
  }

  const startRecording = async () => {
    if (permission !== "granted") {
      const granted = await requestPermission()
      if (!granted) return
    }

    if (!streamRef.current) {
      const granted = await requestPermission()
      if (!granted) return
    }

    try {
      setScore(null)
      setPhonemeScores([])

      chunksRef.current = []
      const recorder = new MediaRecorder(streamRef.current!)

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "audio/webm" })
        if (audioUrl) {
          URL.revokeObjectURL(audioUrl)
        }
        const url = URL.createObjectURL(blob)
        setAudioUrl(url)

        // Mock score and phoneme scores
        const mockScore = 70 + Math.round(Math.random() * 25)
        setScore(mockScore)
        setPhonemeScores(phonemes.map(() => 60 + Math.round(Math.random() * 40)))
        setRecordState("recorded")
      }

      mediaRecorderRef.current = recorder
      recorder.start()
      setRecordState("recording")
    } catch (err) {
      console.error("Failed to start recording:", err)
    }
  }

  const stopRecording = () => {
    if (mediaRecorderRef.current && recordState === "recording") {
      mediaRecorderRef.current.stop()
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach((track) => track.stop())
      streamRef.current = null
    }
  }

  const handlePlayMine = () => {
    if (!audioUrl) return
    const audio = new Audio(audioUrl)
    setIsPlaying(true)
    audio.onended = () => setIsPlaying(false)
    audio.onerror = () => setIsPlaying(false)
    audio.play().catch(() => setIsPlaying(false))
  }

  const handlePlayNative = () => {
    setIsPlayingNative(true)
    console.log("Playing native pronunciation for:", targetWord)
    setTimeout(() => setIsPlayingNative(false), 1000)
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="h-[80vh] max-h-[700px] rounded-t-2xl flex flex-col">
        <SheetHeader className="flex flex-row items-center gap-2 pb-4 border-b shrink-0">
          <SheetTitle className="text-lg font-bold">발음 정밀 진단</SheetTitle>
          <span className="px-2 py-0.5 text-xs font-medium bg-purple-100 text-purple-600 rounded-full">beta</span>
        </SheetHeader>

        {permission === "denied" && (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 text-center px-6">
            <p className="text-sm text-gray-600">
              마이크 권한이 필요해요. 브라우저 설정에서 권한을 허용한 뒤 다시 시도해 주세요.
            </p>
            <Button
              variant="outline"
              className="mt-2 bg-transparent"
              onClick={() => {
                setPermission("unknown")
                requestPermission()
              }}
            >
              권한 다시 시도
            </Button>
          </div>
        )}

        {permission !== "denied" && (
          <>
            {targetWord && (
              <div className="text-center py-1 border-b shrink-0">
                <p className="text-xl font-bold text-gray-900">{targetWord}</p>
                <p className="text-xs text-gray-400">{ipa}</p>
              </div>
            )}

            <div className="py-1 border-b shrink-0">
              <div className="text-center">
                <p className="text-xs text-gray-500">정확도 총점</p>
                <p className="text-xl font-bold text-indigo-600">{score !== null ? score : "-"}</p>
              </div>
            </div>

            {phonemes.length > 0 && (
              <div className="flex-1 min-h-[150px] overflow-y-auto border-b">
                <table className="w-full text-sm px-4">
                  <thead className="sticky top-0 bg-white">
                    <tr className="text-gray-500">
                      <th className="text-left py-1 font-medium pl-4">발음</th>
                      <th className="text-center py-1 font-medium">정확도</th>
                      <th className="text-right py-1 font-medium pr-4">강의</th>
                    </tr>
                  </thead>
                  <tbody>
                    {phonemes.map((phoneme, idx) => (
                      <tr key={idx} className="border-t border-gray-100">
                        <td className="py-1.5 text-lg font-medium pl-4">{phoneme}</td>
                        <td className="py-1.5 text-center">
                          {phonemeScores[idx] !== undefined && (
                            <div className="flex items-center justify-center gap-2">
                              <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-indigo-500 transition-all"
                                  style={{ width: `${phonemeScores[idx]}%` }}
                                />
                              </div>
                              <span className="text-xs text-gray-500">{phonemeScores[idx]}%</span>
                            </div>
                          )}
                        </td>
                        <td className="py-1.5 text-right pr-4">
                          <Button variant="ghost" size="sm" className="text-indigo-500 text-xs h-6">
                            학습
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="shrink-0 flex flex-col items-center py-3 gap-1 px-6">
              <button
                onClick={recordState === "recording" ? stopRecording : startRecording}
                className={`w-14 h-14 rounded-full flex items-center justify-center shadow-lg transition-all active:scale-95 ${
                  recordState === "recording" ? "bg-red-500 animate-pulse" : "bg-indigo-500 hover:bg-indigo-600"
                }`}
              >
                <Mic className="w-5 h-5 text-white" />
              </button>
              <p className="text-xs text-gray-500">
                {recordState === "recording" ? "녹음 중... 탭하여 중지" : "여기를 누르고 발음해 보세요"}
              </p>

              <div className="flex items-center justify-center gap-16 mt-2">
                <button
                  onClick={handlePlayNative}
                  disabled={isPlayingNative}
                  className="flex flex-col items-center gap-0.5 text-indigo-500 disabled:opacity-50"
                >
                  <Volume2 className="w-5 h-5" />
                  <span className="text-xs">성우 발음 듣기</span>
                </button>

                <button
                  onClick={handlePlayMine}
                  disabled={!audioUrl || isPlaying}
                  className="flex flex-col items-center gap-0.5 text-indigo-500 disabled:opacity-50 disabled:text-gray-300"
                >
                  <Volume2 className="w-5 h-5" />
                  <span className="text-xs">나의 발음 듣기</span>
                </button>
              </div>
            </div>
          </>
        )}
      </SheetContent>
    </Sheet>
  )
}
