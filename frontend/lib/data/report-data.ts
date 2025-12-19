// 문제 보고 카테고리 정의
export const REPORT_CATEGORIES = [
  { id: "all", label: "전체" },
  { id: "bug", label: "버그" },
  { id: "content", label: "콘텐츠 오류" },
  { id: "payment", label: "결제 문제" },
  { id: "account", label: "계정 문제" },
  { id: "suggestion", label: "개선 제안" },
  { id: "other", label: "기타" },
]

export type ReportStatus = "pending" | "in-progress" | "resolved" | "closed"

// 상태별 스타일 설정 (백엔드 연동 시 이 부분만 수정하면 됨)
export const REPORT_STATUS_CONFIG: Record<
  ReportStatus,
  {
    label: string
    textColor: string
    bgColor: string
    borderColor: string
    cardBg: string
  }
> = {
  pending: {
    label: "대기중",
    textColor: "text-amber-600",
    bgColor: "bg-amber-100",
    borderColor: "border-gray-200",
    cardBg: "bg-white", // 흰색
  },
  "in-progress": {
    label: "처리중",
    textColor: "text-blue-600",
    bgColor: "bg-blue-100",
    borderColor: "border-blue-200",
    cardBg: "bg-blue-50", // 파란색
  },
  resolved: {
    label: "해결됨",
    textColor: "text-green-600",
    bgColor: "bg-green-100",
    borderColor: "border-green-200",
    cardBg: "bg-green-50", // 초록색
  },
  closed: {
    label: "종료",
    textColor: "text-gray-600",
    bgColor: "bg-gray-100",
    borderColor: "border-gray-300",
    cardBg: "bg-gray-50",
  },
}

export interface ReportItem {
  id: string
  category: string
  title: string
  description: string
  status: ReportStatus
  createdAt: string
  updatedAt?: string
  response?: string
}

// 백엔드 연동 시 이 배열 대신 API 응답 사용
export const SAMPLE_REPORTS: ReportItem[] = []

// ============================================
// 백엔드 연동 가이드
// ============================================
// 1. API 엔드포인트 예시:
//    - GET /api/reports - 사용자 리포트 목록 조회
//    - POST /api/reports - 새 리포트 제출
//    - DELETE /api/reports/:id - 리포트 삭제
//
// 2. 상태 업데이트 시:
//    - 백엔드에서 status 필드를 변경하면 자동으로 색상 반영
//    - pending(흰색) → in-progress(파란색) → resolved(초록색)
//
// 3. 답변 추가 시:
//    - response 필드에 답변 내용 추가
//    - updatedAt 필드 업데이트
// ============================================
