/**
 * Shared utility for calculating new/review word counts based on review ratio mode
 * Used by ReviewRatioPage and StudyModal to ensure consistent calculations
 */

export type ReviewRatioMode = "normal" | "custom"

export interface DeriveCountsParams {
  mode: ReviewRatioMode
  targetWordCount: number | undefined
  customReviewRatioPercent: number
}

export interface DerivedCounts {
  safeTarget: number
  newCount: number
  reviewCount: number
  reviewPercent: number
}

/**
 * Derives new/review word counts based on mode and target
 * - Normal mode: guarantees minimum 25% new words
 * - Custom mode: uses the custom review percentage
 */
export function deriveCounts({ mode, targetWordCount, customReviewRatioPercent }: DeriveCountsParams): DerivedCounts {
  const safeTarget = Math.max(1, targetWordCount ?? 0)

  if (mode === "custom") {
    const reviewCount = Math.round(safeTarget * (customReviewRatioPercent / 100))
    const newCount = safeTarget - reviewCount
    const reviewPercent = customReviewRatioPercent
    return { safeTarget, newCount, reviewCount, reviewPercent }
  } else {
    // Normal mode: minimum 25% new words guaranteed
    const newCount = Math.max(Math.round(safeTarget * 0.25), 1)
    const reviewCount = safeTarget - newCount
    const reviewPercent = Math.round((reviewCount / safeTarget) * 100)
    return { safeTarget, newCount, reviewCount, reviewPercent }
  }
}

/**
 * Clamps a percentage value to prevent tooltip/thumb from going off-screen
 * @param percent - The raw percentage (0-100)
 * @param minClamp - Minimum clamped value (default 5)
 * @param maxClamp - Maximum clamped value (default 95)
 */
export function clampPercent(percent: number, minClamp = 5, maxClamp = 95): number {
  return Math.min(Math.max(percent, minClamp), maxClamp)
}
