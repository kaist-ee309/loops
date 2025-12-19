const AUTH_STORAGE_KEY = "loops:auth"
export const AUTH_CHANGED_EVENT = "loops:auth-changed"

export interface AuthPayload {
  access_token?: string
  refresh_token?: string
  user?: {
    id: string
    email: string
    username?: string
  }
}

// In-memory cache for tokens
let tokenCache: { access_token?: string; refresh_token?: string } = {}

export function emitAuthChanged(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(AUTH_CHANGED_EVENT))
  }
}

export function loadAuth(): AuthPayload | null {
  if (typeof window === "undefined") return null

  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) return null

    const parsed = JSON.parse(raw)
    if (typeof parsed !== "object" || parsed === null) return null

    // Validate shape
    const payload: AuthPayload = {}
    if (typeof parsed.access_token === "string") payload.access_token = parsed.access_token
    if (typeof parsed.refresh_token === "string") payload.refresh_token = parsed.refresh_token
    if (parsed.user && typeof parsed.user === "object") payload.user = parsed.user

    // Populate cache
    tokenCache = {
      access_token: payload.access_token,
      refresh_token: payload.refresh_token,
    }

    return Object.keys(payload).length > 0 ? payload : null
  } catch {
    return null
  }
}

export function saveAuth(payload: AuthPayload): void {
  if (typeof window === "undefined") return

  // Update cache
  tokenCache = {
    access_token: payload.access_token,
    refresh_token: payload.refresh_token,
  }

  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(payload))
  emitAuthChanged()
}

export function clearAuth(): void {
  if (typeof window === "undefined") return

  tokenCache = {}
  localStorage.removeItem(AUTH_STORAGE_KEY)
  emitAuthChanged()
}

export function getAccessToken(): string | undefined {
  if (tokenCache.access_token) return tokenCache.access_token

  const auth = loadAuth()
  return auth?.access_token
}

export function getRefreshToken(): string | undefined {
  if (tokenCache.refresh_token) return tokenCache.refresh_token

  const auth = loadAuth()
  return auth?.refresh_token
}

export function setTokens(accessToken: string, refreshToken: string): void {
  if (typeof window === "undefined") return

  let user: AuthPayload["user"] = undefined
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (parsed?.user && typeof parsed.user === "object") {
        user = parsed.user
      }
    }
  } catch {
    // ignore parse errors
  }

  saveAuth({
    access_token: accessToken,
    refresh_token: refreshToken,
    user,
  })
}
