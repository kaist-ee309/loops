// 공지사항 데이터 타입 정의
// 나중에 백엔드 API 응답으로 대체 가능

export interface Announcement {
  id: string
  title: string
  content: string
  category: "공지" | "업데이트" | "이벤트" | "점검"
  createdAt: string
  isImportant: boolean
}

// 샘플 데이터 - 백엔드 연동 시 API로 대체
export const ANNOUNCEMENTS: Announcement[] = [
  {
    id: "1",
    title: "Loops 서비스 오픈 안내",
    content:
      "안녕하세요, Loops 팀입니다.\n\n과학적인 반복 학습으로 영단어를 영구적으로 기억할 수 있는 Loops 서비스가 정식 오픈되었습니다.\n\nFSRS 알고리즘 기반의 학습 시스템으로 효율적인 영단어 암기를 경험해보세요.\n\n감사합니다.",
    category: "공지",
    createdAt: "2024-12-06",
    isImportant: true,
  },
  {
    id: "2",
    title: "v1.0.1 업데이트 안내",
    content:
      "안녕하세요, Loops 팀입니다.\n\n다음과 같은 업데이트가 진행되었습니다.\n\n- 학습 화면 UI 개선\n- 음성 자동재생 기능 추가\n- 효과음 설정 기능 추가\n- 버그 수정\n\n더 나은 서비스를 위해 노력하겠습니다.\n감사합니다.",
    category: "업데이트",
    createdAt: "2024-12-05",
    isImportant: false,
  },
  {
    id: "3",
    title: "12월 학습 챌린지 이벤트",
    content:
      "안녕하세요, Loops 팀입니다.\n\n12월 학습 챌린지 이벤트를 진행합니다!\n\n이벤트 기간: 2024.12.01 ~ 2024.12.31\n\n매일 30개 이상 단어 학습 시 특별 보상을 드립니다.\n\n많은 참여 부탁드립니다!",
    category: "이벤트",
    createdAt: "2024-12-01",
    isImportant: false,
  },
  {
    id: "4",
    title: "서버 점검 안내 (12/10)",
    content:
      "안녕하세요, Loops 팀입니다.\n\n서비스 안정화를 위한 서버 점검이 예정되어 있습니다.\n\n점검 일시: 2024.12.10 (화) 02:00 ~ 06:00\n\n점검 시간 동안 서비스 이용이 제한됩니다.\n이용에 불편을 드려 죄송합니다.",
    category: "점검",
    createdAt: "2024-12-04",
    isImportant: true,
  },
]

// 카테고리별 스타일
export const CATEGORY_STYLES: Record<Announcement["category"], { bg: string; text: string }> = {
  공지: { bg: "bg-blue-100", text: "text-blue-700" },
  업데이트: { bg: "bg-green-100", text: "text-green-700" },
  이벤트: { bg: "bg-purple-100", text: "text-purple-700" },
  점검: { bg: "bg-orange-100", text: "text-orange-700" },
}
