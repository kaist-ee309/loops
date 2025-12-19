// ============================================================
// 법적 고지 데이터 - 백엔드 연동 시 API로 대체
// ============================================================

// 이용약관 데이터 타입
export interface TermsArticle {
  id: string
  title: string
  content: string
  items?: string[]
}

// 개인정보처리방침 데이터 타입
export interface PrivacySection {
  id: string
  title: string
  content: string
  items?: string[]
  table?: {
    headers: string[]
    rows: string[][]
  }
}

// 글꼴 저작권 데이터 타입
export interface FontLicense {
  id: string
  name: string
  license: string
  copyright: string
  url?: string
}

// ============================================================
// 이용약관 데이터
// ============================================================
export const TERMS_OF_SERVICE: TermsArticle[] = [
  {
    id: "article-1",
    title: "제1조 (목적)",
    content:
      '본 약관은 Loops(이하 "서비스")가 제공하는 영어 학습 애플리케이션 및 그와 관련된 부가 서비스를 이용함에 있어 "서비스"와 "회원"의 권리, "회원"과 "비회원"의 의무 및 책임 사항, 기타 필요한 사항을 규정함을 목적으로 합니다.',
  },
  {
    id: "article-2",
    title: "제2조 (정의)",
    content: "본 약관에서 사용하는 용어의 정의는 다음과 같습니다.",
    items: [
      '"서비스"는 "회원"이 "콘텐츠"를 활용하여 외국어 학습을 하도록 돕는 애플리케이션 서비스 "Loops"를 말합니다.',
      '"이용계약"은 "서비스" 회원가입을 위해 "회원"과 "서비스"간에 체결하는 계약을 말합니다.',
      '"회원"은 본 약관에 따라 "서비스"와 "이용계약"을 체결하고 "서비스"를 이용하는 자를 말합니다.',
      '"비회원"은 "서비스"와 "이용계약"을 체결하기 전에 "서비스"를 이용하는 자를 말합니다.',
      '"가입신청자"는 "서비스"의 "회원"이 되기 위해 "서비스"와 "이용계약"을 체결하고자 하는 자를 말합니다.',
      '"콘텐츠"란 "서비스"가 "회원"을 위해 제공하는 내용물 일체(텍스트, 음성, 영상, 네트워크 서비스를 포함하되 이에 한정되지 아니함)를 말합니다.',
    ],
  },
  {
    id: "article-3",
    title: "제3조 (약관의 효력 및 변경)",
    content: "본 약관의 효력 및 변경에 관한 사항은 다음과 같습니다.",
    items: [
      "본 약관은 서비스를 이용하고자 하는 모든 회원에게 적용됩니다.",
      "서비스는 필요한 경우 약관을 변경할 수 있으며, 변경된 약관은 서비스 내 공지사항을 통해 공지합니다.",
      "회원이 변경된 약관에 동의하지 않는 경우, 서비스 이용을 중단하고 탈퇴할 수 있습니다.",
    ],
  },
  {
    id: "article-4",
    title: "제4조 (서비스의 제공)",
    content: "서비스는 다음과 같은 서비스를 제공합니다.",
    items: [
      "영어 단어 학습 서비스",
      "FSRS 알고리즘 기반 반복 학습 시스템",
      "학습 통계 및 진도 관리 서비스",
      "기타 서비스가 정하는 서비스",
    ],
  },
  {
    id: "article-5",
    title: "제5조 (회원가입)",
    content: "회원가입에 관한 사항은 다음과 같습니다.",
    items: [
      "가입신청자는 서비스가 정한 가입 양식에 따라 회원정보를 기입한 후 본 약관에 동의한다는 의사표시를 함으로써 회원가입을 신청합니다.",
      "서비스는 가입신청자의 신청에 대하여 서비스 이용을 승낙함을 원칙으로 합니다.",
    ],
  },
]

// ============================================================
// 개인정보처리방침 데이터
// ============================================================
export const PRIVACY_POLICY: PrivacySection[] = [
  {
    id: "intro",
    title: "개인정보처리방침",
    content: 'Loops (이하 "서비스")는 대한민국 관련 법령에 의거하여 정한 개인정보처리방침을 준수하고 있습니다.',
  },
  {
    id: "section-1",
    title: "제 1조 수집하는 개인정보의 항목 및 수집 방법",
    content:
      "서비스는 회원가입, 서비스 제공 및 개선, 마케팅 및 프로모션 등을 목적으로 개인정보를 아래와 같이 요청 및 수집하고 있습니다.",
    items: [
      "회원가입 및 서비스 이용 과정에서 이용자가 개인정보 수집에 대해 동의를 하고 직접 정보를 입력하는 경우, 해당 개인정보를 수집합니다.",
      "개인정보 수집에 대해 동의하지 않을 경우 회원가입이 가능하지 않으며, 일부 서비스 이용이 제한될 수 있습니다.",
    ],
    table: {
      headers: ["구분", "수집항목", "수집 목적", "보유 기간"],
      rows: [
        ["회원가입", "이메일, 비밀번호, 성별, 출생 연도", "서비스 이용, 맞춤형 서비스 제공", "회원 탈퇴 후 1년"],
        [
          "간편가입",
          "SNS ID, 닉네임, 프로필 사진, 이메일",
          "서비스 이용, 맞춤형 서비스 제공 및 서비스 개선을 위한 분석",
          "회원 탈퇴 후 1년",
        ],
      ],
    },
  },
  {
    id: "section-2",
    title: "제 2조 개인정보의 보유 및 이용기간",
    content: "서비스는 원칙적으로 개인정보 수집 및 이용목적이 달성된 후에는 해당 정보를 지체 없이 파기합니다.",
    items: [
      "회원 탈퇴 시 개인정보는 즉시 삭제됩니다.",
      "단, 관계법령의 규정에 의하여 보존할 필요가 있는 경우 서비스는 관계법령에서 정한 일정한 기간 동안 회원정보를 보관합니다.",
    ],
  },
  {
    id: "section-3",
    title: "제 3조 개인정보의 파기절차 및 방법",
    content:
      "서비스는 개인정보 보유기간의 경과, 처리목적 달성 등 개인정보가 불필요하게 되었을 때에는 지체없이 해당 개인정보를 파기합니다.",
    items: [
      "전자적 파일 형태로 저장된 개인정보는 기록을 재생할 수 없는 기술적 방법을 사용하여 삭제합니다.",
      "종이에 출력된 개인정보는 분쇄기로 분쇄하거나 소각을 통하여 파기합니다.",
    ],
  },
]

// ============================================================
// 글꼴 저작권 데이터
// ============================================================
export const FONT_LICENSES: FontLicense[] = [
  {
    id: "pretendard",
    name: "Pretendard",
    license: "SIL Open Font License 1.1",
    copyright: "Copyright 2021 The Pretendard Project Authors",
    url: "https://github.com/orioncactus/pretendard",
  },
  {
    id: "noto-sans",
    name: "Noto Sans KR",
    license: "SIL Open Font License 1.1",
    copyright: "Copyright 2014-2021 Adobe (http://www.adobe.com/)",
    url: "https://fonts.google.com/noto/specimen/Noto+Sans+KR",
  },
  {
    id: "inter",
    name: "Inter",
    license: "SIL Open Font License 1.1",
    copyright: "Copyright 2020 The Inter Project Authors",
    url: "https://rsms.me/inter/",
  },
  {
    id: "roboto",
    name: "Roboto",
    license: "Apache License 2.0",
    copyright: "Copyright 2011 Google Inc.",
    url: "https://fonts.google.com/specimen/Roboto",
  },
  {
    id: "lato",
    name: "Lato",
    license: "SIL Open Font License 1.1",
    copyright: "Copyright 2010-2014 Łukasz Dziedzic",
    url: "https://fonts.google.com/specimen/Lato",
  },
]

// ============================================================
// 백엔드 연동용 API 함수 (추후 구현)
// ============================================================
// export async function fetchTermsOfService(): Promise<TermsArticle[]> {
//   const response = await fetch('/api/legal/terms')
//   return response.json()
// }
//
// export async function fetchPrivacyPolicy(): Promise<PrivacySection[]> {
//   const response = await fetch('/api/legal/privacy')
//   return response.json()
// }
//
// export async function fetchFontLicenses(): Promise<FontLicense[]> {
//   const response = await fetch('/api/legal/fonts')
//   return response.json()
// }
