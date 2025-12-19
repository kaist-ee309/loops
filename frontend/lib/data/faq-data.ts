// FAQ 데이터 구조 - 나중에 백엔드 연동 시 API 응답으로 대체 가능
export interface FAQItem {
  id: string
  question: string
  answer: string
  category: "payment" | "account" | "membership" | "learning" | "technical" | "other"
}

export interface FAQCategory {
  id: string
  label: string
  icon?: string
}

export const FAQ_CATEGORIES: FAQCategory[] = [
  { id: "all", label: "전체" },
  { id: "payment", label: "결제" },
  { id: "account", label: "계정" },
  { id: "membership", label: "멤버십" },
  { id: "learning", label: "학습" },
  { id: "technical", label: "기술지원" },
  { id: "other", label: "기타" },
]

export const FAQ_DATA: FAQItem[] = [
  {
    id: "1",
    question: "결제 등록이 안 되어 있는데 결제가 되었어요. 어떻게 된 일인가요?",
    answer:
      "결제가 정상적으로 처리되었으나 시스템 반영이 지연될 수 있습니다. 잠시 후 다시 확인해주시고, 문제가 지속되면 고객센터로 문의해주세요.",
    category: "payment",
  },
  {
    id: "2",
    question: "기기를 바꾼 후 기존 계정으로 로그인할 수 없어요. 어떻게 찾아야 하나요?",
    answer:
      "가입 시 사용한 이메일 주소나 소셜 계정(Google, Kakao 등)으로 로그인을 시도해주세요. 비밀번호를 잊으셨다면 비밀번호 재설정 기능을 이용해주세요.",
    category: "account",
  },
  {
    id: "3",
    question: "현재 멤버십 구독 상태와 결제 계정 정보를 확인하고 싶어요.",
    answer: "마이페이지 > 계정관리에서 현재 멤버십 상태와 결제 정보를 확인할 수 있습니다.",
    category: "membership",
  },
  {
    id: "4",
    question: "학습 진도가 초기화되었어요. 복구할 수 있나요?",
    answer:
      "로그인된 계정이 맞는지 확인해주세요. 다른 계정으로 로그인된 경우 학습 진도가 다르게 보일 수 있습니다. 동일 계정인데 진도가 초기화된 경우 고객센터로 문의해주세요.",
    category: "learning",
  },
  {
    id: "5",
    question: "앱이 자주 종료되거나 오류가 발생해요.",
    answer: "앱을 최신 버전으로 업데이트해주세요. 문제가 지속되면 앱을 삭제 후 재설치하거나, 기기를 재부팅해보세요.",
    category: "technical",
  },
  {
    id: "6",
    question: "구독을 해지하고 싶어요. 어떻게 하나요?",
    answer:
      "마이페이지 > 계정관리 > 멤버십에서 구독 해지를 진행할 수 있습니다. 해지 후에도 결제 기간 동안은 서비스를 이용하실 수 있습니다.",
    category: "membership",
  },
  {
    id: "7",
    question: "단어 발음이 재생되지 않아요.",
    answer:
      "기기의 볼륨 설정과 음소거 모드를 확인해주세요. 마이페이지 > 음성 및 효과음 설정에서 자동재생이 활성화되어 있는지도 확인해주세요.",
    category: "technical",
  },
]

// 추천 질문 (메인에 표시할 질문들)
export const SUGGESTED_QUESTIONS = FAQ_DATA.slice(0, 3)
