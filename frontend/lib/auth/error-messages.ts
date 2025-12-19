import { ApiError } from "@/lib/api/http"

type AuthMode = "login" | "register"

/**
 * Converts auth errors to user-friendly Korean messages
 */
export function getAuthFriendlyError(err: unknown, mode: AuthMode): string {
  let status: number | undefined
  let detail: string | undefined

  // Extract status and detail from error
  if (err instanceof ApiError) {
    status = err.status
    detail = err.message
  } else if (err instanceof Error) {
    // Try to parse JSON from error message (legacy format)
    try {
      const parsed = JSON.parse(err.message)
      if (typeof parsed.detail === "string") {
        detail = parsed.detail
      }
    } catch {
      detail = err.message
    }
  }

  const detailLower = detail?.toLowerCase() ?? ""

  // Register-specific errors
  if (mode === "register") {
    if (status === 400 && detailLower.includes("already registered")) {
      return "이미 가입된 이메일이에요. 로그인해 주세요."
    }
    if (status === 400 && detailLower.includes("already exists")) {
      return "이미 가입된 이메일이에요. 로그인해 주세요."
    }
  }

  // Login-specific errors
  if (mode === "login") {
    if (status === 401 || detailLower.includes("invalid email or password") || detailLower.includes("incorrect")) {
      return "이메일 또는 비밀번호가 올바르지 않아요."
    }
    if (status === 404 || detailLower.includes("user not found") || detailLower.includes("not found")) {
      return "가입되지 않은 이메일이에요. 회원가입을 진행해 주세요."
    }
  }

  // Common errors
  if (status === 422 || detailLower.includes("validation")) {
    return "입력값을 확인해 주세요."
  }

  // Network/unknown errors
  if (!status || detailLower.includes("fetch") || detailLower.includes("network")) {
    return "서버 연결에 실패했어요. 잠시 후 다시 시도해 주세요."
  }

  // Fallback
  return mode === "login" ? "로그인에 실패했어요. 다시 시도해 주세요." : "회원가입에 실패했어요. 다시 시도해 주세요."
}

/**
 * Determines if the error suggests user should register
 */
export function shouldSuggestRegister(err: unknown): boolean {
  if (err instanceof ApiError) {
    const detailLower = err.message.toLowerCase()
    return err.status === 404 || detailLower.includes("user not found") || detailLower.includes("not found")
  }
  return false
}

/**
 * Determines if the error suggests user should login
 */
export function shouldSuggestLogin(err: unknown): boolean {
  if (err instanceof ApiError) {
    const detailLower = err.message.toLowerCase()
    return (
      (err.status === 400 && detailLower.includes("already")) ||
      detailLower.includes("already registered") ||
      detailLower.includes("already exists")
    )
  }
  return false
}
