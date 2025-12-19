# 학습 (Study) API

> FSRS 기반 학습 세션 + 퀴즈 + 스트릭/XP 통합
>
> 최종 업데이트: 2025-12-10

---

## 엔드포인트 요약

| 분류 | 메서드 | 엔드포인트 | 설명 |
|------|--------|-----------|------|
| 조회 | GET | `/overview` | 신규/복습 카드 수 + 복습 예정 목록 |
| 조회 | GET | `/cards/{card_id}` | 개별 카드 FSRS 진행 상세 |
| 세션 | POST | `/session/start` | 세션 시작 |
| 세션 | POST | `/session/card` | 다음 카드 조회 (퀴즈 유형 지정) |
| 세션 | POST | `/session/answer` | 정답 제출 + FSRS 업데이트 |
| 세션 | POST | `/session/complete` | 세션 완료 + XP/스트릭 반영 |

---

## 학습 플로우

```text
1. GET /overview → 오늘 학습할 카드 수 확인
2. POST /session/start → session_id 발급
3. POST /session/card → 문제 조회 (반복)
4. POST /session/answer → 정답 제출 (반복)
5. POST /session/complete → XP/스트릭 반영
```

---

## 조회 API

### GET /overview

학습 현황 개요 조회

**쿼리**: `?limit=50` (복습 카드 최대 수, 1~100)

**응답**:

```json
{
  "new_cards_count": 150,
  "review_cards_count": 45,
  "total_available": 195,
  "due_cards": [
    {
      "card_id": 1234,
      "english_word": "decide",
      "korean_meaning": "결정하다",
      "next_review_date": "2025-12-09T00:00:00Z",
      "card_state": "REVIEW"
    }
  ]
}
```

### GET /cards/{card_id}

개별 카드 FSRS 진행 조회

**응답**:

```json
{
  "card_id": 1234,
  "card_state": "REVIEW",
  "stability": 15.2,
  "difficulty": 4.5,
  "scheduled_days": 7,
  "next_review_date": "2025-12-17T00:00:00Z",
  "accuracy_rate": 80.0
}
```

---

## 세션 API

### POST /session/start

**요청**:

```json
{
  "new_cards_limit": 30,
  "review_cards_limit": 30
}
```

**응답**:

```json
{
  "session_id": "uuid",
  "total_cards": 25,
  "new_cards_count": 8,
  "review_cards_count": 17
}
```

### POST /session/card

**요청**:

```json
{
  "session_id": "uuid",
  "quiz_type": "word_to_meaning"
}
```

**퀴즈 유형**: `word_to_meaning`, `meaning_to_word`, `cloze`, `listening`

**응답**:

```json
{
  "card": {
    "id": 1234,
    "question": "decide",
    "options": ["결정하다", "나누다", "설명하다", "요청하다"]
  },
  "cards_remaining": 19,
  "cards_completed": 5
}
```

### POST /session/answer

**요청**:

```json
{
  "session_id": "uuid",
  "card_id": 1234,
  "answer": "결정하다"
}
```

**응답**:

```json
{
  "is_correct": true,
  "correct_answer": "결정하다",
  "next_review_date": "2025-12-17T00:00:00Z",
  "card_state": "review"
}
```

### POST /session/complete

**요청**:

```json
{
  "session_id": "uuid",
  "duration_seconds": 300
}
```

**응답**:

```json
{
  "session_summary": {
    "total_cards": 20,
    "correct_count": 16,
    "accuracy_rate": 80.0
  },
  "streak": {
    "current_streak": 7,
    "is_new_record": false
  },
  "daily_goal": {
    "goal": 20,
    "completed": 21,
    "is_achieved": true
  },
  "xp": {
    "base_xp": 160,
    "bonus_xp": 50,
    "total_xp": 210
  }
}
```

---

## 핵심 개념

### 카드 상태 (FSRS)

| 상태 | 설명 |
|------|------|
| `NEW` | 미학습 카드 |
| `LEARNING` | 학습 중 (단기 기억) |
| `REVIEW` | 복습 단계 (장기 기억) |
| `RELEARNING` | 재학습 (복습 중 오답) |

### XP 계산

- 기본: 정답당 10XP
- 보너스: 정확도 80%+ 시 +50XP

### 스트릭

- 어제 학습 → 연속일 +1
- 어제 미학습 → 1로 리셋

---

## 신규 기능

### US-STUDY-01: 학습 세션 설정 프리뷰 (신규)

#### 스토리

**사용자로서**, 학습 설정(단어 개수, 복습 비율)에 따른 카드 구성을 미리 확인할 수 있다.
**그래서** 학습 시작 전 "새 단어 8개, 복습 12개"와 같은 정보를 볼 수 있다.

#### 상세 정보

| 항목 | 내용 |
|------|------|
| **엔드포인트** | `POST /api/v1/study/session/preview` (신규) |
| **엔드포인트** | `GET /api/v1/study/overview` (확장: `daily_goal` 추가) |
| **인증 필요** | 예 |
| **상태** | 🔲 미구현 |
| **GitHub** | [#46](https://github.com/ee309-team-goat/loops-api/issues/46) |

#### 요청/응답 예시 - 프리뷰

**요청:**

```
POST /api/v1/study/session/preview
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "total_cards": 20,
  "review_ratio": 0.6
}
```

**응답 (200 OK):**

```json
{
  "available": {
    "new_cards": 50,
    "review_cards": 25,
    "relearning_cards": 5
  },
  "allocation": {
    "new_cards": 8,
    "review_cards": 12,
    "total": 20
  },
  "message": null
}
```

#### Overview 확장

**응답 (200 OK) - 확장:**

```json
{
  "new_cards_count": 50,
  "review_cards_count": 25,
  "total_available": 75,
  "due_cards": [...],
  "daily_goal": {
    "goal": 30,
    "completed": 15,
    "progress": 50.0,
    "is_completed": false
  }
}
```

---

### US-STUDY-02: Typing 모드 힌트 기능 (신규)

#### 스토리

**사용자로서**, 빈칸 채우기 문제에서 힌트를 사용하여 정답 글자를 하나씩 볼 수 있다.
**그래서** 어려운 단어도 힌트를 통해 학습할 수 있다.

#### 상세 정보

| 항목 | 내용 |
|------|------|
| **엔드포인트** | `POST /api/v1/study/session/answer` (확장) |
| **인증 필요** | 예 |
| **변경 사항** | `hint_count`, `revealed_answer` 필드 추가 |
| **상태** | 🔲 미구현 |
| **GitHub** | [#52](https://github.com/ee309-team-goat/loops-api/issues/52) |

#### 힌트 사용 시 점수 계산

| 상태 | FSRS Rating | 점수 |
|------|-------------|------|
| 정답 (힌트 없음) | 3 (Good) | 100점 |
| 정답 (힌트 사용) | 2 (Hard) | 100 - (힌트 수 × 20)점 |
| 정답 공개 사용 | 1 (Again) | 0점 |
| 오답 | 1 (Again) | 0점 |

#### 요청 스키마 확장

```json
{
  "session_id": "uuid",
  "card_id": 1234,
  "answer": "contract",
  "response_time_ms": 5000,
  "hint_count": 2,
  "revealed_answer": false
}
```

---

### US-STUDY-03: 오답 노트 기록 (신규)

#### 스토리

**사용자로서**, 틀린 문제들의 상세 기록을 확인하고 복습할 수 있다.
**그래서** 자주 틀리는 단어를 집중적으로 학습할 수 있다.

#### 상세 정보

| 항목 | 내용 |
|------|------|
| **엔드포인트** | `GET /api/v1/study/wrong-answers` (신규) |
| **엔드포인트** | `PATCH /api/v1/study/wrong-answers/{id}/reviewed` (신규) |
| **인증 필요** | 예 |
| **상태** | 🔲 미구현 |
| **GitHub** | [#53](https://github.com/ee309-team-goat/loops-api/issues/53) |

#### 데이터 모델

```python
class WrongAnswer(SQLModel, table=True):
    id: int
    user_id: UUID
    card_id: int
    session_id: UUID | None

    user_answer: str
    correct_answer: str
    quiz_type: str

    created_at: datetime
    reviewed: bool = False
    reviewed_at: datetime | None = None
```

#### 요청/응답 예시

**요청:**

```
GET /api/v1/study/wrong-answers?limit=20&reviewed=false
Authorization: Bearer {access_token}
```

**응답 (200 OK):**

```json
{
  "wrong_answers": [
    {
      "id": 1,
      "card": {
        "id": 123,
        "english_word": "contract",
        "korean_meaning": "계약"
      },
      "user_answer": "contrat",
      "correct_answer": "contract",
      "quiz_type": "cloze",
      "created_at": "2024-12-10T10:30:00Z",
      "reviewed": false
    }
  ],
  "total": 15,
  "unreviewed_count": 10
}
```

---

### US-STUDY-04: 세션 중단 및 상태 조회 (신규)

#### 스토리

**사용자로서**, 학습 중 뒤로가기 시 남은 문제 수와 목표 달성 정보를 확인하고 중단을 선택할 수 있다.
**그래서** 의도치 않은 학습 중단을 방지하고 진행 상황을 저장할 수 있다.

#### 상세 정보

| 항목 | 내용 |
|------|------|
| **엔드포인트** | `GET /api/v1/study/session/{session_id}/status` (신규) |
| **엔드포인트** | `POST /api/v1/study/session/{session_id}/abandon` (신규) |
| **인증 필요** | 예 |
| **상태** | 🔲 미구현 |
| **GitHub** | [#54](https://github.com/ee309-team-goat/loops-api/issues/54) |

#### 세션 상태 조회

**요청:**

```
GET /api/v1/study/session/{session_id}/status
Authorization: Bearer {access_token}
```

**응답 (200 OK):**

```json
{
  "session_id": "...",
  "status": "active",
  "total_cards": 20,
  "completed_cards": 8,
  "remaining_cards": 12,
  "correct_count": 6,
  "wrong_count": 2,
  "started_at": "2024-12-10T10:00:00Z",
  "elapsed_seconds": 300,
  "daily_goal": {
    "goal": 30,
    "completed_today": 15,
    "remaining_for_goal": 15,
    "will_complete_goal": false
  }
}
```

#### 세션 중단

**요청:**

```
POST /api/v1/study/session/{session_id}/abandon
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "save_progress": true
}
```

**응답 (200 OK):**

```json
{
  "session_id": "...",
  "status": "abandoned",
  "summary": {
    "total_cards": 20,
    "completed_cards": 8,
    "correct_count": 6,
    "wrong_count": 2,
    "duration_seconds": 300
  },
  "progress_saved": true,
  "message": "학습 진행 상황이 저장되었습니다."
}
```

---

### US-STUDY-05: 발음 진단 (신규)

#### 스토리

**사용자로서**, 내 발음을 녹음하여 평가받고 네이티브 발음과 비교할 수 있다.
**그래서** 정확한 발음을 학습할 수 있다.

#### 상세 정보

| 항목 | 내용 |
|------|------|
| **엔드포인트** | `POST /api/v1/study/pronunciation/evaluate` (신규) |
| **인증 필요** | 예 |
| **입력** | 오디오 파일 (wav/m4a/webm) |
| **출력** | 점수 (0-100), 등급, 피드백 |
| **상태** | 🔲 미구현 |
| **GitHub** | [#56](https://github.com/ee309-team-goat/loops-api/issues/56) |

#### 점수 등급

| 점수 | 등급 | 라벨 |
|------|------|------|
| 90-100 | `excellent` | 완벽해요! |
| 75-89 | `good` | 좋아요! |
| 60-74 | `fair` | 조금 더 연습해요 |
| 0-59 | `needs_practice` | 다시 도전해보세요 |

#### 요청/응답 예시

**요청:**

```
POST /api/v1/study/pronunciation/evaluate
Authorization: Bearer {access_token}
Content-Type: multipart/form-data

audio_file: (binary)
card_id: 123
```

**응답 (200 OK):**

```json
{
  "card_id": 123,
  "word": "innovation",
  "pronunciation_ipa": "/ˌɪnəˈveɪʃən/",

  "score": 78,
  "grade": "good",

  "feedback": {
    "overall": "발음이 좋습니다! 강세 위치에 조금 더 신경 쓰면 완벽해요.",
    "stress": "'va' 음절에 강세를 더 주세요.",
    "sounds": [
      {"phoneme": "ʃ", "score": 65, "tip": "'sh' 소리를 더 부드럽게"}
    ]
  },

  "native_audio_url": "https://...",
  "user_audio_url": "https://..."
}
```

#### 구현 단계

| Phase | 내용 |
|-------|------|
| Phase 1 | Mock API - 랜덤 점수 + 고정 피드백 반환 |
| Phase 2 | Azure/Google Speech API 연동 |
| Phase 3 | 발음 기록 저장 및 통계 |

---

## 관련 파일

- `src/app/api/study.py`
- `src/app/services/study_session_service.py`
- `src/app/models/schemas/study.py`
