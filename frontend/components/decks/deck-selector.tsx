"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { getDecks, getSelectedDecks, updateSelectedDecks, type Deck } from "@/lib/api/decks"
import { Button } from "@/components/ui/button"
import { Check, AlertCircle, X, RefreshCw } from "lucide-react"

interface SelectionState {
  selectAll: boolean
  selectedIds: Set<number>
}

export function DeckSelector() {
  const [decks, setDecks] = useState<Deck[]>([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  const [selection, setSelection] = useState<SelectionState>({
    selectAll: false,
    selectedIds: new Set(),
  })

  const [lastSaved, setLastSaved] = useState<SelectionState>({
    selectAll: false,
    selectedIds: new Set(),
  })

  const selectAllRef = useRef<HTMLInputElement>(null)

  // Derived state
  const allIds = decks.map((d) => d.id)
  const isIndeterminate =
    !selection.selectAll && selection.selectedIds.size > 0 && selection.selectedIds.size < decks.length
  const isAllChecked = selection.selectAll || (decks.length > 0 && selection.selectedIds.size === decks.length)

  const effectiveChecked = useCallback(
    (id: number) => {
      return selection.selectAll ? true : selection.selectedIds.has(id)
    },
    [selection.selectAll, selection.selectedIds],
  )

  useEffect(() => {
    if (selectAllRef.current) {
      selectAllRef.current.indeterminate = isIndeterminate
    }
  }, [isIndeterminate])

  const loadData = useCallback(async () => {
    setLoading(true)
    setError(null)

    try {
      const [loadedDecks, selectedState] = await Promise.all([getDecks(), getSelectedDecks()])

      setDecks(loadedDecks)

      const initialSelection: SelectionState = {
        selectAll: selectedState.select_all,
        selectedIds: new Set(selectedState.deck_ids),
      }
      setSelection(initialSelection)
      setLastSaved(initialSelection)
    } catch {
      setError("서버 연결에 실패했습니다. 다시 시도해주세요.")
      setDecks([])
      const emptyState: SelectionState = { selectAll: false, selectedIds: new Set() }
      setSelection(emptyState)
      setLastSaved(emptyState)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleSelectAllChange = () => {
    if (isAllChecked) {
      setSelection({ selectAll: false, selectedIds: new Set() })
    } else {
      setSelection({ selectAll: true, selectedIds: new Set() })
    }
  }

  const handleDeckToggle = (id: number) => {
    if (selection.selectAll) {
      const newIds = new Set(allIds.filter((deckId) => deckId !== id))
      setSelection({ selectAll: false, selectedIds: newIds })
    } else {
      const newIds = new Set(selection.selectedIds)
      if (newIds.has(id)) {
        newIds.delete(id)
      } else {
        newIds.add(id)
      }
      setSelection({ selectAll: false, selectedIds: newIds })
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    setSuccess(false)

    try {
      const isAll = selection.selectAll || (decks.length > 0 && selection.selectedIds.size === decks.length)

      if (isAll) {
        await updateSelectedDecks({ select_all: true })
        // Update lastSaved with normalized state
        setLastSaved({ selectAll: true, selectedIds: new Set() })
        // Also normalize current selection state
        setSelection({ selectAll: true, selectedIds: new Set() })
      } else {
        await updateSelectedDecks({ select_all: false, deck_ids: Array.from(selection.selectedIds) })
        setLastSaved({ selectAll: false, selectedIds: new Set(selection.selectedIds) })
      }

      setSuccess(true)
      setTimeout(() => setSuccess(false), 2000)
    } catch (err) {
      setSelection({ ...lastSaved, selectedIds: new Set(lastSaved.selectedIds) })
      setError(err instanceof Error ? err.message : "저장에 실패했습니다.")
    } finally {
      setSaving(false)
    }
  }

  const getDeckName = (deck: Deck) => deck.name || deck.title || `Deck ${deck.id}`

  return (
    <div className="space-y-4">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0" />
              <span className="text-sm text-red-700">{error}</span>
            </div>
            <button onClick={() => setError(null)}>
              <X className="w-4 h-4 text-red-600" />
            </button>
          </div>
          {/* Retry button when load failed */}
          {decks.length === 0 && !loading && (
            <Button variant="outline" size="sm" onClick={loadData} className="mt-2 w-full bg-transparent">
              <RefreshCw className="w-4 h-4 mr-2" />
              다시 시도
            </Button>
          )}
        </div>
      )}

      {success && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 flex items-center gap-2">
          <Check className="w-5 h-5 text-green-600 flex-shrink-0" />
          <span className="text-sm text-green-700">저장되었습니다.</span>
        </div>
      )}

      <div className="bg-white rounded-2xl overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-100">
          <label className="flex items-center gap-3 cursor-pointer">
            <input
              ref={selectAllRef}
              type="checkbox"
              checked={isAllChecked}
              onChange={handleSelectAllChange}
              disabled={loading || decks.length === 0}
              className="w-5 h-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 disabled:opacity-50"
            />
            <div className="flex-1">
              <span className="font-medium text-gray-900">전체 선택</span>
              {isIndeterminate && <span className="ml-2 text-xs text-gray-500">일부 선택됨</span>}
            </div>
          </label>
        </div>

        {loading && (
          <div className="divide-y divide-gray-100">
            {[1, 2, 3].map((i) => (
              <div key={i} className="px-4 py-3 flex items-center gap-3">
                <div className="w-5 h-5 bg-gray-200 rounded animate-pulse" />
                <div className="h-4 bg-gray-200 rounded w-32 animate-pulse" />
              </div>
            ))}
          </div>
        )}

        {!loading && decks.length === 0 && !error && (
          <div className="px-4 py-8 text-center text-gray-500">덱이 없습니다.</div>
        )}

        {!loading && decks.length > 0 && (
          <div className="divide-y divide-gray-100">
            {decks.map((deck) => (
              <label key={deck.id} className="flex items-center gap-3 px-4 py-3 cursor-pointer hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={effectiveChecked(deck.id)}
                  onChange={() => handleDeckToggle(deck.id)}
                  className="w-5 h-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
                <span className="text-gray-900">{getDeckName(deck)}</span>
              </label>
            ))}
          </div>
        )}
      </div>

      <Button
        onClick={handleSave}
        disabled={saving || loading || decks.length === 0}
        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white"
      >
        {saving ? "저장 중..." : "저장"}
      </Button>
    </div>
  )
}
