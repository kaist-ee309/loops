"use client"

import { useState, useEffect } from "react"
import { X, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet"
import { getWrongNotes, deleteWrongNote, type WrongNote } from "@/lib/wrong-notes"

interface WrongNotesSheetProps {
  open: boolean
  onOpenChange: (open: boolean) => void
}

export function WrongNotesSheet({ open, onOpenChange }: WrongNotesSheetProps) {
  const [notes, setNotes] = useState<WrongNote[]>([])

  useEffect(() => {
    if (open) {
      setNotes(getWrongNotes())
    }
  }, [open])

  const handleDelete = (id: string) => {
    deleteWrongNote(id)
    setNotes(getWrongNotes())
  }

  const formatDate = (ts: number) => {
    const date = new Date(ts)
    return `${date.getMonth() + 1}/${date.getDate()} ${date.getHours()}:${String(date.getMinutes()).padStart(2, "0")}`
  }

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="bottom" className="h-[70vh] rounded-t-2xl">
        <SheetHeader className="flex flex-row items-center justify-between pb-4 border-b">
          <SheetTitle className="text-lg font-bold">오답 노트</SheetTitle>
          <Button variant="ghost" size="icon" onClick={() => onOpenChange(false)}>
            <X className="w-5 h-5" />
          </Button>
        </SheetHeader>

        <div className="overflow-y-auto h-[calc(100%-60px)] py-4">
          {notes.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-gray-400">
              <BookOpen className="w-12 h-12 mb-3" />
              <p>아직 오답 기록이 없습니다</p>
            </div>
          ) : (
            <div className="space-y-3">
              {notes.map((note) => (
                <div key={note.id} className="bg-gray-50 rounded-xl p-4 relative">
                  <Button
                    variant="ghost"
                    size="icon"
                    className="absolute top-2 right-2 w-8 h-8 text-gray-400 hover:text-red-500"
                    onClick={() => handleDelete(note.id)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>

                  <div className="flex items-baseline gap-2 mb-2">
                    <span className="text-lg font-bold text-indigo-600">{note.word}</span>
                    <span className="text-xs text-gray-400">{formatDate(note.ts)}</span>
                  </div>

                  <p className="text-sm text-gray-600 mb-1">
                    <span className="text-gray-400">입력:</span>{" "}
                    <span className="text-red-500 line-through">{note.userAnswer}</span>
                  </p>

                  <p className="text-sm text-gray-600">
                    <span className="text-gray-400">정답:</span>{" "}
                    <span className="text-green-600 font-medium">{note.correctAnswer}</span>
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  )
}

// Re-export BookOpen for the empty state
import { BookOpen } from "lucide-react"
