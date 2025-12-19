import type { Category } from "@/lib/mock-decks"

export type SummaryInput = {
  categories: Category[]
  selectedDeckIds: string[]
}

export type SummaryOutput = {
  courseDisplayName: string
  selectionSummaryLines: string[]
}

/**
 * Builds a course summary from selected deck IDs.
 *
 * Rules:
 * - courseDisplayName:
 *   - 0 selected: ""
 *   - 1 selected: deck name
 *   - 2-3 fully selected categories only: "시험, 교과서"
 *   - Otherwise: "first 외 N개"
 *
 * - selectionSummaryLines:
 *   - Max 3 lines
 *   - If > 3 entries: [entry1, entry2, "외 N개"]
 */
export function buildCourseSummary(input: SummaryInput): SummaryOutput {
  const { categories, selectedDeckIds } = input
  const selectedSet = new Set(selectedDeckIds)

  if (selectedSet.size === 0) {
    return { courseDisplayName: "", selectionSummaryLines: [] }
  }

  // Build ordered entries following categories/decks array order
  const fullySelectedCategories: string[] = []
  const partialSelectedDecks: { categoryId: string; deckName: string }[] = []

  for (const category of categories) {
    const categoryDeckIds = category.decks.map((d) => d.id)
    const selectedInCategory = categoryDeckIds.filter((id) => selectedSet.has(id))

    if (selectedInCategory.length === 0) continue

    if (selectedInCategory.length === categoryDeckIds.length) {
      // Fully selected category
      fullySelectedCategories.push(category.title)
    } else {
      // Partial selection - add individual decks
      for (const deck of category.decks) {
        if (selectedSet.has(deck.id)) {
          partialSelectedDecks.push({ categoryId: category.id, deckName: deck.title })
        }
      }
    }
  }

  // Build tokens for courseDisplayName
  // Tokens: fully selected categories as category name, partial decks as deck name
  const tokens: string[] = [...fullySelectedCategories, ...partialSelectedDecks.map((d) => d.deckName)]

  // Build entries for selectionSummaryLines
  // Entries: fully selected categories, then partial decks
  const entries: string[] = [...fullySelectedCategories, ...partialSelectedDecks.map((d) => d.deckName)]

  // Calculate courseDisplayName
  let courseDisplayName = ""
  if (tokens.length === 1) {
    courseDisplayName = tokens[0]
  } else if (
    fullySelectedCategories.length >= 2 &&
    fullySelectedCategories.length <= 3 &&
    partialSelectedDecks.length === 0
  ) {
    // 2-3 fully selected categories only
    courseDisplayName = fullySelectedCategories.join(", ")
  } else if (tokens.length >= 2) {
    courseDisplayName = `${tokens[0]} 외 ${tokens.length - 1}개`
  }

  // Calculate selectionSummaryLines (max 3 lines)
  let selectionSummaryLines: string[]
  if (entries.length <= 3) {
    selectionSummaryLines = entries
  } else {
    // Show first 2, then "외 N개"
    selectionSummaryLines = [entries[0], entries[1], `외 ${entries.length - 2}개`]
  }

  return { courseDisplayName, selectionSummaryLines }
}
