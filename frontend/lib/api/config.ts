// Base URL should not include /api/v1 to avoid duplication; path arguments carry it.
const DEFAULT_BASE_URL = "/_loops_api"

export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_LOOPS_API_BASE_URL || DEFAULT_BASE_URL
}
