"use client"

import type React from "react"
import { createContext, useContext, useState, useEffect, useCallback } from "react"
import {
  loadAuth,
  saveAuth,
  clearAuth as clearAuthStorage,
  type AuthPayload,
  AUTH_CHANGED_EVENT,
} from "@/lib/auth/storage"
import { apiFetch } from "@/lib/api/http"

interface User {
  id: string
  email: string
  username?: string
}

interface AuthContextValue {
  user: User | null
  isAuthed: boolean
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, username: string, password: string) => Promise<void>
  logout: () => Promise<void>
  getAccessToken: () => string | undefined
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

interface AuthProviderProps {
  children: React.ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [accessToken, setAccessToken] = useState<string | undefined>(undefined)
  const [isLoading, setIsLoading] = useState(true)

  const syncFromStorage = useCallback(() => {
    const auth = loadAuth()
    setAccessToken(auth?.access_token)
    setUser((auth?.user as User) ?? null)
  }, [])

  // On mount, load auth from storage and listen for auth changes
  useEffect(() => {
    syncFromStorage()
    setIsLoading(false)

    window.addEventListener(AUTH_CHANGED_EVENT, syncFromStorage)
    return () => {
      window.removeEventListener(AUTH_CHANGED_EVENT, syncFromStorage)
    }
  }, [syncFromStorage])

  const login = useCallback(async (email: string, password: string) => {
    const response = await apiFetch<{
      access_token: string
      refresh_token: string
      user: User
    }>("/api/v1/auth/login", {
      method: "POST",
      body: { email, password },
    })

    const payload: AuthPayload = {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      user: response.user,
    }
    saveAuth(payload)
    // State will be updated via AUTH_CHANGED_EVENT listener
  }, [])

  const register = useCallback(async (email: string, username: string, password: string) => {
    const response = await apiFetch<{
      access_token: string
      refresh_token: string
      user: User
    }>("/api/v1/auth/register", {
      method: "POST",
      body: { email, username, password },
    })

    const payload: AuthPayload = {
      access_token: response.access_token,
      refresh_token: response.refresh_token,
      user: response.user,
    }
    saveAuth(payload)
    if (username) {
      localStorage.setItem("signupNickname", username)
    }
    // State will be updated via AUTH_CHANGED_EVENT listener
  }, [])

  const logout = useCallback(async () => {
    try {
      await apiFetch("/api/v1/auth/logout", {
        method: "POST",
        auth: true,
      })
    } catch {
      // Ignore errors on logout
    } finally {
      clearAuthStorage()
      // State will be updated via AUTH_CHANGED_EVENT listener
    }
  }, [])

  const getAccessTokenFn = useCallback(() => {
    return accessToken
  }, [accessToken])

  const value: AuthContextValue = {
    user,
    isAuthed: !!accessToken,
    isLoading,
    login,
    register,
    logout,
    getAccessToken: getAccessTokenFn,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
