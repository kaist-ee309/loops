import { apiFetch } from "./http"

// Types
export interface Deck {
  id: number
  name?: string
  title?: string
  [key: string]: unknown // allow unknown fields
}

export interface SelectedDecksState {
  select_all: boolean
  deck_ids: number[]
}

// API Functions
export async function getDecks(params?: { skip?: number; limit?: number }): Promise<Deck[]> {
  const query = new URLSearchParams()
  if (params?.skip !== undefined) query.set("skip", String(params.skip))
  if (params?.limit !== undefined) query.set("limit", String(params.limit))

  const queryString = query.toString()
  const path = `/api/v1/decks${queryString ? `?${queryString}` : ""}`

  const res = await apiFetch<Deck[] | { items: Deck[] } | { decks: Deck[] }>(path, {
    method: "GET",
    auth: true,
  })

  // Normalize response to Deck[]
  if (Array.isArray(res)) {
    return res
  }
  if ("items" in res && Array.isArray(res.items)) {
    return res.items
  }
  if ("decks" in res && Array.isArray(res.decks)) {
    return res.decks
  }
  return []
}

export async function getSelectedDecks(): Promise<SelectedDecksState> {
  const res = await apiFetch<Partial<SelectedDecksState>>("/api/v1/decks/selected-decks", {
    method: "GET",
    auth: true,
  })

  // Normalize missing deck_ids to []
  return {
    select_all: res.select_all ?? false,
    deck_ids: res.deck_ids ?? [],
  }
}

export async function updateSelectedDecks(payload: { select_all: boolean; deck_ids?: number[] }): Promise<void> {
  const body = payload.select_all ? { select_all: true } : { select_all: false, deck_ids: payload.deck_ids ?? [] }

  await apiFetch("/api/v1/decks/selected-decks", {
    method: "PUT",
    auth: true,
    body,
  })
}
