# Loops API 문서 센터

> 영어 단어 학습 앱 - 백엔드 API 문서 모음
>
> 최종 업데이트: 2025-12-10

---

## 문서 목록

### 핵심 문서

| 문서                                    | 설명                                            |
| --------------------------------------- | ----------------------------------------------- |
| **[user-stories/](./user-stories/)**    | 8개 도메인 35개 기능의 상세 유저 스토리         |

### 시작하기

| 문서                             | 설명                          |
| -------------------------------- | ----------------------------- |
| **[COMMANDS.md](./COMMANDS.md)** | 자주 사용하는 명령어 모음     |
| **[../CLAUDE.md](../CLAUDE.md)** | AI 협업 가이드 및 개발 가이드 |

### 기술 문서

| 문서                                                             | 설명                           |
| ---------------------------------------------------------------- | ------------------------------ |
| **[DATABASE.md](./DATABASE.md)**                                 | 데이터베이스 스키마 및 ERD     |
| **[CARD_SELECTION_ALGORITHM.md](./CARD_SELECTION_ALGORITHM.md)** | 단어 카드 선정 알고리즘 가이드 |

### 배포 & 운영

| 문서                                           | 설명             |
| ---------------------------------------------- | ---------------- |
| **[DEPLOYMENT.md](./DEPLOYMENT.md)**           | 배포 가이드      |
| **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** | 문제 해결 가이드 |

### 프로젝트 관리

| 문서                                                 | 설명                                       |
| ---------------------------------------------------- | ------------------------------------------ |
| **[PROJECT_MANAGEMENT.md](./PROJECT_MANAGEMENT.md)** | GitHub Projects 설정, 이슈 관리, 협업 방법 |

### 데이터

| 문서                                           | 설명                          |
| ---------------------------------------------- | ----------------------------- |
| **[data_collecting.md](./data_collecting.md)** | 공개 데이터 소스 및 수집 방법 |

---

## 목적별 문서 찾기

### 처음 시작하는 개발자

1. [../CLAUDE.md](../CLAUDE.md) - 환경 설정 및 개발 가이드
2. [COMMANDS.md](./COMMANDS.md) - 기본 명령어
3. [DATABASE.md](./DATABASE.md) - DB 구조 이해
4. [user-stories/](./user-stories/) - 기능 이해

### 기능 개발자

1. [user-stories/](./user-stories/) - 기능 요구사항 및 API 명세
2. [DATABASE.md](./DATABASE.md) - 스키마 참조
3. [CARD_SELECTION_ALGORITHM.md](./CARD_SELECTION_ALGORITHM.md) - 알고리즘 이해

### DevOps / 인프라

1. [DEPLOYMENT.md](./DEPLOYMENT.md) - 배포 절차
2. [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결

### PM / 기획자

1. [user-stories/](./user-stories/) - 기능 유저스토리
2. [PROJECT_MANAGEMENT.md](./PROJECT_MANAGEMENT.md) - 프로젝트 관리 방법

---

## 유저 스토리 요약

8개 도메인의 35개 기능을 유저스토리 형태로 정리:

| 도메인                       | 기능 수 | 문서                                                   |
| ---------------------------- | ------- | ------------------------------------------------------ |
| 인증 (Authentication)        | 5       | [01-authentication.md](./user-stories/01-authentication.md) |
| 프로필 (Profile)             | 9       | [02-profile.md](./user-stories/02-profile.md)               |
| 단어 카드 (Vocabulary Cards) | 5       | [03-vocabulary-cards.md](./user-stories/03-vocabulary-cards.md) |
| 덱 (Decks)                   | 4       | [04-decks.md](./user-stories/04-decks.md)                   |
| 학습 진행 (Progress)         | 4       | [05-progress.md](./user-stories/05-progress.md)             |
| 퀴즈 (Quiz)                  | 3       | [06-quiz.md](./user-stories/06-quiz.md)                     |
| 통계 (Statistics)            | 3       | [07-statistics.md](./user-stories/07-statistics.md)         |
| 학습 세션 (Study Session)    | 2       | [08-study-session.md](./user-stories/08-study-session.md)   |

---

## 프로젝트 아키텍처

```text
loops-api/
├── src/
│   ├── app/
│   │   ├── api/          # API 라우트
│   │   ├── models/       # SQLModel 모델
│   │   │   ├── tables/   # 테이블 모델
│   │   │   └── schemas/  # Pydantic 스키마
│   │   ├── services/     # 비즈니스 로직
│   │   └── core/         # 인증, 보안
│   └── alembic/          # DB 마이그레이션
├── docs/                 # 문서
│   └── user-stories/     # 유저 스토리
└── tests/                # 테스트 코드
```

---

## 외부 리소스

### 기술 스택

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLModel**: https://sqlmodel.tiangolo.com/
- **Alembic**: https://alembic.sqlalchemy.org/
- **FSRS**: https://github.com/open-spaced-repetition/py-fsrs
- **Supabase**: https://supabase.com/

### 데이터 소스

- **COCA Frequency**: https://www.wordfrequency.info/samples.asp
- **Oxford 3000/5000**: https://www.oxfordlearnersdictionaries.com/wordlists/
- **NGSL/NAWL/BSL**: https://www.newgeneralservicelist.com/

---

## 문서 업데이트 히스토리

- **2025-12-10**: 문서 통합 - API.md, DEVELOPMENT.md, ROADMAP.md를 user-stories에 통합하여 삭제
- **2025-12-10**: user-stories/ 폴더 구조화 (8개 도메인별 파일)
- **2025-11-28**: CARD_SELECTION_ALGORITHM.md 추가
- **이전**: 초기 문서 작성
