// Wrong notes storage utilities for localStorage persistence

export interface WrongNote {
  id: string
  word: string
  ts: number
  userAnswer: string
  correctAnswer: string
  koSentence: string
  enSentenceWithBlank: string
}

const STORAGE_KEY = "loops:wrong-notes"

export function getWrongNotes(): WrongNote[] {
  if (typeof window === "undefined") return []
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    if (!Array.isArray(parsed)) return []
    return parsed
  } catch {
    return []
  }
}

export function saveWrongNote(note: Omit<WrongNote, "id" | "ts">): void {
  if (typeof window === "undefined") return

  const notes = getWrongNotes()

  // Check for duplicate (same word + sentence combination)
  const existingIndex = notes.findIndex(
    (n) => n.word === note.word && n.enSentenceWithBlank === note.enSentenceWithBlank,
  )

  const generateId = () => {
    if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
      return crypto.randomUUID()
    }
    return `${Date.now()}-${Math.random().toString(36).slice(2, 11)}`
  }

  const newNote: WrongNote = {
    ...note,
    id: existingIndex >= 0 ? notes[existingIndex].id : generateId(),
    ts: Date.now(),
  }

  if (existingIndex >= 0) {
    // Update existing note's timestamp
    notes[existingIndex] = newNote
  } else {
    // Add new note at the beginning
    notes.unshift(newNote)
  }

  // Keep only last 100 notes
  const trimmed = notes.slice(0, 100)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed))
}

export function deleteWrongNote(id: string): void {
  if (typeof window === "undefined") return
  const notes = getWrongNotes()
  const filtered = notes.filter((n) => n.id !== id)
  localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered))
}

export function clearAllWrongNotes(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem(STORAGE_KEY)
}
