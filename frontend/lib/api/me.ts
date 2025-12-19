import { apiFetch } from "@/lib/api/http"
import { ApiError } from "@/lib/api/http"

export interface MeProfile {
  id?: string
  email?: string
  name?: string
  nickname?: string
  username?: string
}

const unavailableEndpoints = new Set<string>()

async function tryEndpoint(path: string): Promise<MeProfile | null> {
  if (unavailableEndpoints.has(path)) return null
  try {
    return await apiFetch<MeProfile>(path, { auth: true })
  } catch (err) {
    const status = err instanceof ApiError ? err.status : (err as any)?.status ?? (err as any)?.response?.status
    if (status === 401 || status === 403) {
      throw err
    }
    if (status === 404) {
      unavailableEndpoints.add(path)
      console.debug("[getMeProfile] endpoint unavailable (404)", path)
      return null
    }
    console.debug("[getMeProfile] endpoint failed", path, err)
    throw err
  }
}

export async function getMeProfile(): Promise<MeProfile | null> {
  const candidates = ["/api/v1/profiles/me", "/api/v1/auth/me"]
  for (const path of candidates) {
    const res = await tryEndpoint(path)
    if (res) return res
  }
  return null
}
