export type Settings = {
  notificationsEnabled: boolean
  notificationTime: string // "09:00"
  studyReport: boolean
  leagueAlerts: boolean
  reviewReminder: boolean

  autoPlayAudio: boolean
  playbackSpeed: 0.75 | 1 | 1.25
  soundEffects: boolean

  darkMode: boolean

  dailyGoal: 10 | 20 | 30 | 50
  quizMode: "flashcard" | "multiple-choice" | "typing"
  difficulty: "easy" | "medium" | "hard"
}

export const DEFAULT_SETTINGS: Settings = {
  notificationsEnabled: true,
  notificationTime: "09:00",
  studyReport: true,
  leagueAlerts: true,
  reviewReminder: true,

  autoPlayAudio: true,
  playbackSpeed: 1,
  soundEffects: true,

  darkMode: false,

  dailyGoal: 20,
  quizMode: "flashcard",
  difficulty: "medium",
}

const VALID_PLAYBACK_SPEEDS = [0.75, 1, 1.25] as const
const VALID_DAILY_GOALS = [10, 20, 30, 50] as const
const VALID_QUIZ_MODES = ["flashcard", "multiple-choice", "typing"] as const
const VALID_DIFFICULTIES = ["easy", "medium", "hard"] as const

export function validateSettings(data: unknown): Settings {
  if (!data || typeof data !== "object") {
    return DEFAULT_SETTINGS
  }

  const obj = data as Record<string, unknown>

  try {
    // Only pick known keys, ignore unknown keys (like quizTypes/showMeaning from previous run)
    return {
      notificationsEnabled:
        typeof obj.notificationsEnabled === "boolean"
          ? obj.notificationsEnabled
          : DEFAULT_SETTINGS.notificationsEnabled,

      notificationTime:
        typeof obj.notificationTime === "string" && /^\d{2}:\d{2}$/.test(obj.notificationTime)
          ? obj.notificationTime
          : DEFAULT_SETTINGS.notificationTime,

      studyReport: typeof obj.studyReport === "boolean" ? obj.studyReport : DEFAULT_SETTINGS.studyReport,

      leagueAlerts: typeof obj.leagueAlerts === "boolean" ? obj.leagueAlerts : DEFAULT_SETTINGS.leagueAlerts,

      reviewReminder: typeof obj.reviewReminder === "boolean" ? obj.reviewReminder : DEFAULT_SETTINGS.reviewReminder,

      autoPlayAudio: typeof obj.autoPlayAudio === "boolean" ? obj.autoPlayAudio : DEFAULT_SETTINGS.autoPlayAudio,

      playbackSpeed: VALID_PLAYBACK_SPEEDS.includes(obj.playbackSpeed as 0.75 | 1 | 1.25)
        ? (obj.playbackSpeed as 0.75 | 1 | 1.25)
        : DEFAULT_SETTINGS.playbackSpeed,

      soundEffects: typeof obj.soundEffects === "boolean" ? obj.soundEffects : DEFAULT_SETTINGS.soundEffects,

      darkMode: typeof obj.darkMode === "boolean" ? obj.darkMode : DEFAULT_SETTINGS.darkMode,

      dailyGoal: VALID_DAILY_GOALS.includes(obj.dailyGoal as 10 | 20 | 30 | 50)
        ? (obj.dailyGoal as 10 | 20 | 30 | 50)
        : DEFAULT_SETTINGS.dailyGoal,

      quizMode: VALID_QUIZ_MODES.includes(obj.quizMode as Settings["quizMode"])
        ? (obj.quizMode as Settings["quizMode"])
        : DEFAULT_SETTINGS.quizMode,

      difficulty: VALID_DIFFICULTIES.includes(obj.difficulty as Settings["difficulty"])
        ? (obj.difficulty as Settings["difficulty"])
        : DEFAULT_SETTINGS.difficulty,
    }
  } catch {
    return DEFAULT_SETTINGS
  }
}
