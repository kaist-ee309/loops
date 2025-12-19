// Mock data for deck categories and decks
// This will be replaced with real API data later

export interface Deck {
  id: string
  title: string
  subtitle?: string
  totalWords: number
  learnedWords: number
  progressPercent: number
}

export interface Category {
  id: string
  title: string
  description: string
  icon: string // emoji or icon name
  decks: Deck[]
}

export const MOCK_CATEGORIES: Category[] = [
  {
    id: "exam",
    title: "시험",
    description: "수능, TOEIC 등 공인영어시험 단어 모음",
    icon: "🎯",
    decks: [
      { id: "exam-1", title: "능률 VOCA 어원편", totalWords: 7082, learnedWords: 18, progressPercent: 0 },
      { id: "exam-2", title: "능률 VOCA 어원편 mini", totalWords: 3725, learnedWords: 3, progressPercent: 0 },
      { id: "exam-3", title: "수능 기출 단어", totalWords: 16982, learnedWords: 212, progressPercent: 1 },
      { id: "exam-4", title: "수능 핵심 단어장", totalWords: 3212, learnedWords: 3, progressPercent: 0 },
      { id: "exam-5", title: "TOEIC 단어장", totalWords: 6441, learnedWords: 50, progressPercent: 0 },
      { id: "exam-6", title: "공무원 영어 단어장(9급 전 2급)", totalWords: 9006, learnedWords: 98, progressPercent: 1 },
      { id: "exam-7", title: "TEPS 단어장", totalWords: 6366, learnedWords: 9, progressPercent: 0 },
      { id: "exam-8", title: "TOEFL 단어장", totalWords: 1935, learnedWords: 6, progressPercent: 0 },
      { id: "exam-9", title: "GRE 어휘집 (beta)", totalWords: 4349, learnedWords: 1, progressPercent: 0 },
      { id: "exam-10", title: "IELTS 단어장", totalWords: 4498, learnedWords: 35, progressPercent: 0 },
    ],
  },
  {
    id: "textbook",
    title: "교과서",
    description: "초등, 중등, 고등 영어 교과서 단어 모음",
    icon: "📚",
    decks: [
      { id: "textbook-1", title: "초등 필수 영단어", totalWords: 800, learnedWords: 0, progressPercent: 0 },
      { id: "textbook-2", title: "중학 영어 단어", totalWords: 2500, learnedWords: 0, progressPercent: 0 },
      { id: "textbook-3", title: "고등 영어 단어", totalWords: 4000, learnedWords: 0, progressPercent: 0 },
      { id: "textbook-4", title: "수능 영어 필수", totalWords: 3500, learnedWords: 0, progressPercent: 0 },
    ],
  },
  {
    id: "situation",
    title: "상황별",
    description: "비즈니스 등 특정한 상황별 단어 모음",
    icon: "💼",
    decks: [
      { id: "situation-1", title: "비즈니스 영어", totalWords: 1500, learnedWords: 0, progressPercent: 0 },
      { id: "situation-2", title: "여행 영어", totalWords: 800, learnedWords: 0, progressPercent: 0 },
      { id: "situation-3", title: "일상 회화", totalWords: 2000, learnedWords: 0, progressPercent: 0 },
      { id: "situation-4", title: "면접 영어", totalWords: 500, learnedWords: 0, progressPercent: 0 },
      { id: "situation-5", title: "이메일 영어", totalWords: 600, learnedWords: 0, progressPercent: 0 },
    ],
  },
  {
    id: "drama",
    title: "드라마",
    description: "유명 미국 드라마의 에피소드별 단어 모음",
    icon: "📺",
    decks: [
      { id: "drama-1", title: "프렌즈 시즌1", totalWords: 1200, learnedWords: 0, progressPercent: 0 },
      { id: "drama-2", title: "오피스 시즌1", totalWords: 1000, learnedWords: 0, progressPercent: 0 },
      { id: "drama-3", title: "브레이킹 배드", totalWords: 1500, learnedWords: 0, progressPercent: 0 },
      { id: "drama-4", title: "왕좌의 게임", totalWords: 2000, learnedWords: 0, progressPercent: 0 },
    ],
  },
  {
    id: "movie",
    title: "영화",
    description: "좋아하는 영화 대사들의 단어 모음",
    icon: "🎬",
    decks: [
      { id: "movie-1", title: "해리포터 시리즈", totalWords: 3000, learnedWords: 0, progressPercent: 0 },
      { id: "movie-2", title: "마블 시네마틱", totalWords: 2500, learnedWords: 0, progressPercent: 0 },
      { id: "movie-3", title: "디즈니 클래식", totalWords: 1500, learnedWords: 0, progressPercent: 0 },
      { id: "movie-4", title: "크리스토퍼 놀란", totalWords: 1800, learnedWords: 0, progressPercent: 0 },
    ],
  },
  {
    id: "youtube",
    title: "YouTube",
    description: "유튜브에 있는 일상 회화 단어 모음",
    icon: "▶️",
    decks: [
      { id: "youtube-1", title: "TED Talks", totalWords: 2000, learnedWords: 0, progressPercent: 0 },
      { id: "youtube-2", title: "영어 브이로그", totalWords: 1000, learnedWords: 0, progressPercent: 0 },
      { id: "youtube-3", title: "영어 뉴스", totalWords: 1500, learnedWords: 0, progressPercent: 0 },
      { id: "youtube-4", title: "팟캐스트 영어", totalWords: 1200, learnedWords: 0, progressPercent: 0 },
    ],
  },
]

export function getCategoryById(id: string): Category | undefined {
  return MOCK_CATEGORIES.find((cat) => cat.id === id)
}

export function getAllDeckIds(): string[] {
  return MOCK_CATEGORIES.flatMap((cat) => cat.decks.map((deck) => deck.id))
}
