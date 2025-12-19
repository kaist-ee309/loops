"use client"

import { createContext, useContext, useEffect, useState, type ReactNode } from "react"
import { type Settings, DEFAULT_SETTINGS, validateSettings } from "@/lib/settings/types"

const STORAGE_KEY = "loops:settings"

interface SettingsContextType {
  settings: Settings
  setSetting: <K extends keyof Settings>(key: K, value: Settings[K]) => void
  updateSettings: (partial: Partial<Settings>) => void
  resetSettings: () => void
}

const SettingsContext = createContext<SettingsContextType | null>(null)

function loadSettings(): Settings {
  if (typeof window === "undefined") {
    return DEFAULT_SETTINGS
  }

  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) {
      return DEFAULT_SETTINGS
    }

    const parsed = JSON.parse(stored)
    return validateSettings(parsed)
  } catch {
    // If JSON parsing fails, return defaults
    return DEFAULT_SETTINGS
  }
}

function saveSettings(settings: Settings): void {
  if (typeof window === "undefined") return

  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(settings))
  } catch {
    // Ignore storage errors (e.g., quota exceeded)
  }
}

export function SettingsProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<Settings>(DEFAULT_SETTINGS)
  const [isLoaded, setIsLoaded] = useState(false)

  // Load settings on mount (client-side only)
  useEffect(() => {
    const loaded = loadSettings()
    setSettings(loaded)
    setIsLoaded(true)
  }, [])

  // Save settings whenever they change (after initial load)
  useEffect(() => {
    if (isLoaded) {
      saveSettings(settings)
    }
  }, [settings, isLoaded])

  const setSetting = <K extends keyof Settings>(key: K, value: Settings[K]) => {
    setSettings((prev) => ({ ...prev, [key]: value }))
  }

  const updateSettings = (partial: Partial<Settings>) => {
    setSettings((prev) => ({ ...prev, ...partial }))
  }

  const resetSettings = () => {
    setSettings(DEFAULT_SETTINGS)
  }

  return (
    <SettingsContext.Provider value={{ settings, setSetting, updateSettings, resetSettings }}>
      {children}
    </SettingsContext.Provider>
  )
}

export function useSettings(): SettingsContextType {
  const context = useContext(SettingsContext)
  if (!context) {
    throw new Error("useSettings must be used within a SettingsProvider")
  }
  return context
}
