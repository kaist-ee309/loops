import { getApiBaseUrl } from "./config"
import { getAccessToken, getRefreshToken, setTokens, clearAuth } from "@/lib/auth/storage"

interface ApiFetchOptions extends Omit<RequestInit, "body"> {
  auth?: boolean
  body?: unknown
}

export class ApiError extends Error {
  status: number
  data: unknown
  bodyText?: string
  constructor(message: string, status: number, data: unknown, bodyText?: string) {
    super(message)
    this.name = "ApiError"
    this.status = status
    this.data = data
    this.bodyText = bodyText
  }
}

function joinUrl(baseUrl: string, path: string): string {
  // Remove trailing slash from baseUrl
  let base = baseUrl.replace(/\/+$/, "")

  // Ensure path starts with a single /
  const rawPath = path ?? ""
  let p = rawPath.startsWith("/") ? rawPath : `/${rawPath}`
  const queryIndex = p.search(/[?#]/)
  const pathPart = queryIndex === -1 ? p : p.slice(0, queryIndex)
  const suffix = queryIndex === -1 ? "" : p.slice(queryIndex)
  const normalizedPath = pathPart.replace(/^\/+/, "/").replace(/\/{2,}/g, "/")
  p = `${normalizedPath}${suffix}`

  // Prevent /api/api duplication: if base ends with /api and path starts with /api/
  if (base.endsWith("/api") && (p.startsWith("/api/") || p === "/api")) {
    base = base.slice(0, -4) // Remove trailing /api from base
  }

  return `${base}${p}`
}

const loggedUrls = new Set<string>()

async function parseErrorResponse(res: Response): Promise<{ message: string; data: unknown; bodyText?: string }> {
  let data: unknown = null
  let message = `${res.status} ${res.statusText}`
  let rawText: string | undefined

  try {
    const text = await res.text()
    rawText = text
    if (!text) return { message, data }

    // Try to parse as JSON
    try {
      data = JSON.parse(text)
      // Extract detail field if it's a string
      if (typeof data === "object" && data !== null && "detail" in data) {
        const detail = (data as { detail: unknown }).detail
        if (typeof detail === "string") {
          message = detail
        }
      }
    } catch {
      // Not JSON, use text as message if meaningful
      if (text.length < 200) {
        message = text
      }
    }
  } catch {
    // Could not read response body
  }

  return { message, data, bodyText: rawText }
}

let isRefreshing = false
let refreshPromise: Promise<boolean> | null = null

async function refreshTokens(): Promise<boolean> {
  const refreshToken = getRefreshToken()
  if (!refreshToken) return false

  try {
    const res = await fetch(`${getApiBaseUrl()}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    })

    if (!res.ok) return false

    const data = await res.json()
    if (data.access_token && data.refresh_token) {
      setTokens(data.access_token, data.refresh_token)
      return true
    }
    return false
  } catch {
    return false
  }
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { auth = false, body, ...restOptions } = options

  const baseUrl = getApiBaseUrl()
  const url = joinUrl(baseUrl, path)

  const headers: HeadersInit = {
    ...(restOptions.headers || {}),
  }

  // Set Content-Type for JSON bodies
  if (body && typeof body === "object" && !(body instanceof FormData)) {
    ;(headers as Record<string, string>)["Content-Type"] = "application/json"
  }

  if (auth) {
    const accessToken = getAccessToken()
    if (!accessToken) {
      throw new ApiError("Unauthorized: missing access token", 401, { reason: "missing_access_token" })
    }
    ;(headers as Record<string, string>)["Authorization"] = `Bearer ${accessToken}`
  }

  const fetchOptions: RequestInit = {
    ...restOptions,
    headers,
    body: body && typeof body === "object" && !(body instanceof FormData) ? JSON.stringify(body) : (body as BodyInit),
  }

  let res: Response
  try {
    res = await fetch(url, fetchOptions)
  } catch (err) {
    if (!loggedUrls.has(url)) {
      loggedUrls.add(url)
      console.debug("[apiFetch] Network error", { url, error: (err as Error).message })
    }
    throw err
  }

  // Handle 401 - attempt token refresh
  if (res.status === 401 && auth) {
    const refreshToken = getRefreshToken()
    if (refreshToken) {
      // Prevent multiple simultaneous refresh attempts
      if (!isRefreshing) {
        isRefreshing = true
        refreshPromise = refreshTokens().finally(() => {
          isRefreshing = false
          refreshPromise = null
        })
      }

      const refreshSuccess = await refreshPromise
      if (refreshSuccess) {
        // Retry original request with new token
        const newAccessToken = getAccessToken()
        if (newAccessToken) {
          ;(headers as Record<string, string>)["Authorization"] = `Bearer ${newAccessToken}`
        }
        res = await fetch(url, { ...fetchOptions, headers })
      } else {
        clearAuth()
        throw new ApiError("Session expired. Please login again.", 401, null)
      }
    } else {
      clearAuth()
      throw new ApiError("Unauthorized", 401, null)
    }
  }

  if (!res.ok) {
    const { message, data, bodyText } = await parseErrorResponse(res)
    if (!loggedUrls.has(url)) {
      loggedUrls.add(url)
      console.debug("[apiFetch] Request failed", {
        url,
        status: res.status,
        contentType: res.headers.get("content-type"),
      })
    }
    throw new ApiError(message, res.status, data, bodyText)
  }

  // Handle empty responses
  const text = await res.text()
  if (!text) return {} as T

  return JSON.parse(text) as T
}
