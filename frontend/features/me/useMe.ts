"use client"

import { useEffect } from "react"
import { create } from "zustand"
import { getMeProfile, type MeProfile } from "@/lib/api/me"

const LOCAL_NICKNAME_KEY = "signupNickname"
const LEGACY_NICKNAME_KEY = "userNickname"

function isBannedName(value: string | null | undefined) {
  if (!value || typeof value !== "string") return false
  return value.trim().toLowerCase() === "me"
}

type LoadOptions = { force?: boolean }

type MeState = {
  profile: MeProfile | null
  loading: boolean
  error: unknown
  loaded: boolean
  load: (options?: LoadOptions) => Promise<void>
}

const useMeStore = create<MeState>((set, get) => ({
  profile: null,
  loading: false,
  error: null,
  loaded: false,
  load: async (options?: LoadOptions) => {
    const force = options?.force ?? false
    if (get().loading) return
    if (get().loaded && !force) return

    if (force) {
      set({ loaded: false, profile: null, error: null })
    }

    set({ loading: true, error: null })
    try {
      const profile = await getMeProfile()

      set({
        profile: profile ?? null,
        loaded: true,
      })
    } catch (err) {
      console.debug("[useMe] load failed", err)
      set({ error: err, profile: null, loaded: true })
    } finally {
      set({ loading: false })
    }
  },
}))

function getLocalNickname() {
  if (typeof window === "undefined") return null
  const legacy = localStorage.getItem(LEGACY_NICKNAME_KEY)
  const current = localStorage.getItem(LOCAL_NICKNAME_KEY)
  if (!current && legacy) {
    if (!isBannedName(legacy)) {
      localStorage.setItem(LOCAL_NICKNAME_KEY, legacy)
      return legacy
    }
    localStorage.removeItem(LEGACY_NICKNAME_KEY)
  }

  if (legacy && isBannedName(legacy)) {
    localStorage.removeItem(LEGACY_NICKNAME_KEY)
  }
  if (current && isBannedName(current)) {
    localStorage.removeItem(LOCAL_NICKNAME_KEY)
    return null
  }
  return current
}

function deriveDisplayName(profile: MeProfile | null, fallback = "사용자") {
  const localNick = getLocalNickname()
  if (profile) {
    const name = profile.nickname || profile.name || profile.username
    const trimmed = typeof name === "string" ? name.trim() : ""
    if (trimmed && !isBannedName(trimmed)) return trimmed
  }
  if (localNick) {
    const trimmedLocal = localNick.trim()
    if (trimmedLocal && !isBannedName(trimmedLocal)) return trimmedLocal
  }
  const email = (profile as { email?: string } | null | undefined)?.email
  if (email && typeof email === "string" && email.includes("@")) {
    const prefix = email.split("@")[0]?.trim()
    if (prefix && !isBannedName(prefix)) return prefix
  }
  return fallback
}

export function useMe() {
  const { profile, loading, load, error, loaded } = useMeStore()

  useEffect(() => {
    load()
  }, [load])

  const displayName = deriveDisplayName(profile)

  const refresh = (options?: LoadOptions) => load({ force: options?.force ?? true })

  return {
    profile,
    loading,
    loaded,
    error,
    displayName,
    refresh,
  }
}
