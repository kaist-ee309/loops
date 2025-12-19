# 프로필 (Profile) 유저 스토리

> 사용자 프로필, 설정, 레벨, 스트릭 관리
>
> 최종 업데이트: 2025-12-10

---

## 개요

프로필 도메인은 사용자의 학습 설정, 진행 상황, 스트릭(연속 학습일), 레벨 정보를 관리합니다.
Supabase Auth의 사용자 ID(UUID)를 기본 키로 사용하여 인증 시스템과 연동됩니다.

### 주요 특징

- **개인화 설정**: 일일 목표, 테마, 알림 등 사용자 맞춤 설정
- **스트릭 시스템**: 연속 학습 동기 부여를 위한 스트릭 추적
- **레벨 시스템**: CEFR 기반 학습 숙련도 측정
- **실시간 진행 상황**: 오늘의 학습 진행률 실시간 확인

### 프로필 데이터 구조

```
Profile
├── 기본 정보 (id, created_at, updated_at)
├── 학습 설정 (daily_goal, select_all_decks)
├── 앱 설정 (timezone, theme, notification_enabled)
├── 스트릭 (current_streak, longest_streak, last_study_date)
└── 통계 (total_study_time_minutes)
```

---

## US-PROFILE-01: 내 프로필 조회

### 스토리

**사용자로서**, 내 프로필 정보를 조회할 수 있다.
**그래서** 내 학습 설정과 통계를 확인할 수 있다.

### 상세 정보

| 항목           | 내용                                     |
| -------------- | ---------------------------------------- |
| **엔드포인트** | `GET /api/v1/profiles/me`                |
| **인증 필요**  | 예                                       |
| **출력**       | ID, 학습 설정, 스트릭 정보, 총 학습 시간 |
| **상태**       | ✅ 구현 완료                             |

### 반환 데이터

| 필드                       | 타입     | 설명                            |
| -------------------------- | -------- | ------------------------------- |
| `id`                       | UUID     | Supabase Auth 사용자 ID         |
| `select_all_decks`         | boolean  | 전체 덱 학습 여부               |
| `daily_goal`               | integer  | 일일 학습 목표 카드 수          |
| `timezone`                 | string   | 사용자 타임존                   |
| `theme`                    | string   | 테마 (light/dark/auto)          |
| `notification_enabled`     | boolean  | 알림 활성화 여부                |
| `current_streak`           | integer  | 현재 연속 학습일                |
| `longest_streak`           | integer  | 최장 연속 학습일                |
| `last_study_date`          | date     | 마지막 학습일                   |
| `total_study_time_minutes` | integer  | 총 학습 시간 (분)               |
| `created_at`               | datetime | 계정 생성일                     |
| `updated_at`               | datetime | 마지막 수정일                   |

### 요청/응답 예시

**요청:**

```
GET /api/v1/profiles/me
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "select_all_decks": true,
  "daily_goal": 20,
  "timezone": "Asia/Seoul",
  "theme": "dark",
  "notification_enabled": true,
  "current_streak": 7,
  "longest_streak": 15,
  "last_study_date": "2025-12-10",
  "total_study_time_minutes": 450,
  "created_at": "2025-11-01T10:00:00Z",
  "updated_at": "2025-12-10T08:30:00Z"
}
```

---

## US-PROFILE-02: 오늘의 학습 진행 상황 조회

### 스토리

**사용자로서**, 오늘 학습한 카드 수와 일일 목표 달성률을 확인할 수 있다.
**그래서** 오늘의 학습 목표를 관리할 수 있다.

### 상세 정보

| 항목           | 내용                                                       |
| -------------- | ---------------------------------------------------------- |
| **엔드포인트** | `GET /api/v1/profiles/me/today-progress`                   |
| **인증 필요**  | 예                                                         |
| **출력**       | 총 복습 횟수, 정답/오답 수, 정확도, 일일 목표, 목표 달성률 |
| **상태**       | ✅ 구현 완료                                               |

### 비즈니스 규칙

1. **날짜 기준**: 사용자의 타임존 기준 오늘 00:00 ~ 23:59
2. **복습 집계**: 오늘 수행한 모든 카드 복습 결과 집계
3. **목표 진행률**: `(완료 수 / 일일 목표) * 100`

### 반환 데이터 설명

| 필드            | 타입    | 설명                           |
| --------------- | ------- | ------------------------------ |
| `total_reviews` | integer | 오늘 총 복습 횟수              |
| `correct_count` | integer | 정답 횟수                      |
| `wrong_count`   | integer | 오답 횟수                      |
| `accuracy_rate` | float   | 정확도 (%)                     |
| `daily_goal`    | integer | 설정된 일일 목표               |
| `goal_progress` | float   | 목표 달성률 (%, 최대 100 초과) |

### 요청/응답 예시

**성공 응답:**

```json
{
  "total_reviews": 12,
  "correct_count": 10,
  "wrong_count": 2,
  "accuracy_rate": 83.3,
  "daily_goal": 20,
  "goal_progress": 60.0
}
```

### UI 활용 예시

```
오늘의 학습
━━━━━━━━━━━━━━━━━━━━━━━━━
[████████░░░░░░░░░░░░] 60%
12 / 20 카드 완료

정확도: 83.3% (10/12)
```

---

## US-PROFILE-03: 일일 목표 조회

### 스토리

**사용자로서**, 내 일일 학습 목표와 오늘 완료한 카드 수를 확인할 수 있다.
**그래서** 남은 학습량을 파악할 수 있다.

### 상세 정보

| 항목           | 내용                                 |
| -------------- | ------------------------------------ |
| **엔드포인트** | `GET /api/v1/profiles/me/daily-goal` |
| **인증 필요**  | 예                                   |
| **출력**       | 일일 목표, 오늘 완료 수              |
| **상태**       | ✅ 구현 완료                         |

### 요청/응답 예시

**성공 응답:**

```json
{
  "daily_goal": 20,
  "completed_today": 12
}
```

---

## US-PROFILE-04: 사용자 설정 조회

### 스토리

**사용자로서**, 내 학습 및 앱 설정을 조회할 수 있다.
**그래서** 현재 설정 상태를 확인할 수 있다.

### 상세 정보

| 항목           | 내용                                                  |
| -------------- | ----------------------------------------------------- |
| **엔드포인트** | `GET /api/v1/profiles/me/config`                      |
| **인증 필요**  | 예                                                    |
| **출력**       | 일일 목표, 전체 덱 선택 여부, 타임존, 테마, 알림 설정 |
| **상태**       | ✅ 구현 완료                                          |

### 설정 항목 상세

| 설정                   | 타입    | 기본값  | 설명                   |
| ---------------------- | ------- | ------- | ---------------------- |
| `daily_goal`           | integer | 20      | 일일 학습 목표 (1~1000)|
| `select_all_decks`     | boolean | true    | 전체 덱에서 학습       |
| `timezone`             | string  | "UTC"   | 타임존 (IANA 형식)     |
| `theme`                | string  | "auto"  | 테마 설정              |
| `notification_enabled` | boolean | true    | 푸시 알림 활성화       |

### 요청/응답 예시

**성공 응답:**

```json
{
  "daily_goal": 20,
  "select_all_decks": false,
  "timezone": "Asia/Seoul",
  "theme": "dark",
  "notification_enabled": true
}
```

---

## US-PROFILE-05: 사용자 설정 수정

### 스토리

**사용자로서**, 내 학습 및 앱 설정을 변경할 수 있다.
**그래서** 개인화된 학습 환경을 구성할 수 있다.

### 상세 정보

| 항목           | 내용                                                             |
| -------------- | ---------------------------------------------------------------- |
| **엔드포인트** | `PUT /api/v1/profiles/me/config`                                 |
| **인증 필요**  | 예                                                               |
| **입력**       | 일일 목표, 전체 덱 선택, 타임존, 테마, 알림 설정 (부분 업데이트) |
| **상태**       | ✅ 구현 완료                                                     |

### 유효성 검사 규칙

| 필드                   | 규칙                                  |
| ---------------------- | ------------------------------------- |
| `daily_goal`           | 1 ~ 1000 사이의 정수                  |
| `select_all_decks`     | boolean                               |
| `timezone`             | IANA 타임존 문자열 (예: "Asia/Seoul") |
| `theme`                | "light", "dark", "auto" 중 하나       |
| `notification_enabled` | boolean                               |

### 요청/응답 예시

**요청 (부분 업데이트):**

```json
{
  "daily_goal": 30,
  "theme": "light"
}
```

**성공 응답 (200 OK):**

```json
{
  "daily_goal": 30,
  "select_all_decks": false,
  "timezone": "Asia/Seoul",
  "theme": "light",
  "notification_enabled": true
}
```

---

## US-PROFILE-06: 사용자 레벨 조회

### 스토리

**사용자로서**, 내 학습 숙련도 레벨과 CEFR 등급을 확인할 수 있다.
**그래서** 내 영어 실력 수준을 파악할 수 있다.

### 상세 정보

| 항목           | 내용                                                               |
| -------------- | ------------------------------------------------------------------ |
| **엔드포인트** | `GET /api/v1/profiles/me/level`                                    |
| **인증 필요**  | 예                                                                 |
| **출력**       | 레벨 (1.0~10.0), CEFR 등급, 총 복습 횟수, 정확도, 마스터한 카드 수 |
| **상태**       | ✅ 구현 완료                                                       |

### 레벨 계산 알고리즘

1. **입력 데이터**:
   - 최근 50회 복습의 정답률
   - 전체 정확도
   - 마스터한 카드의 평균 난이도

2. **레벨 공식**:
   ```
   level = (recent_accuracy * 0.4) + (overall_accuracy * 0.3) + (mastered_difficulty * 0.3)
   ```

3. **CEFR 매핑**:
   | 레벨 범위 | CEFR |
   |-----------|------|
   | 1.0 ~ 2.0 | A1   |
   | 2.1 ~ 3.5 | A2   |
   | 3.6 ~ 5.0 | B1   |
   | 5.1 ~ 7.0 | B2   |
   | 7.1 ~ 8.5 | C1   |
   | 8.6 ~ 10.0| C2   |

### 요청/응답 예시

**성공 응답:**

```json
{
  "level": 5.4,
  "cefr_level": "B2",
  "total_reviews": 523,
  "accuracy_rate": 78.5,
  "mastered_cards": 142,
  "level_description": "중급 상위 - 대부분의 일상 대화를 이해하고 자신의 의견을 표현할 수 있습니다."
}
```

---

## US-PROFILE-07: 프로필 수정

### 스토리

**사용자로서**, 내 프로필 정보를 수정할 수 있다.
**그래서** 개인 정보를 최신 상태로 유지할 수 있다.

### 상세 정보

| 항목           | 내용                        |
| -------------- | --------------------------- |
| **엔드포인트** | `PATCH /api/v1/profiles/me` |
| **인증 필요**  | 예                          |
| **입력**       | 수정할 필드 (부분 업데이트) |
| **상태**       | ✅ 구현 완료                |

### 수정 가능 필드

- `daily_goal`
- `select_all_decks`
- `timezone`
- `theme`
- `notification_enabled`

### 요청/응답 예시

**요청:**

```json
{
  "daily_goal": 25,
  "notification_enabled": false
}
```

**성공 응답 (200 OK):** 업데이트된 전체 프로필 반환

---

## US-PROFILE-08: 프로필 삭제

### 스토리

**사용자로서**, 내 프로필을 삭제할 수 있다.
**그래서** 서비스 탈퇴할 수 있다.

### 상세 정보

| 항목           | 내용                         |
| -------------- | ---------------------------- |
| **엔드포인트** | `DELETE /api/v1/profiles/me` |
| **인증 필요**  | 예                           |
| **상태**       | ✅ 구현 완료                 |

### 삭제되는 데이터

1. **프로필 정보**: 설정, 스트릭, 통계
2. **학습 진행 데이터**: 모든 카드별 학습 기록
3. **즐겨찾기**: 저장된 모든 즐겨찾기
4. **선택된 덱 정보**: 덱 선택 설정

### 주의사항

- ⚠️ **되돌릴 수 없음**: 삭제된 데이터는 복구 불가
- ⚠️ **Supabase Auth 별도 삭제**: 인증 계정은 Supabase에서 별도 삭제 필요
- 💡 **확인 UI 권장**: 클라이언트에서 삭제 전 확인 다이얼로그 표시 권장

### 요청/응답 예시

**요청:**

```
DELETE /api/v1/profiles/me
Authorization: Bearer {access_token}
```

**성공 응답 (204 No Content)**

---

## US-PROFILE-09: 스트릭 정보 조회

### 스토리

**사용자로서**, 내 연속 학습 스트릭 정보를 확인할 수 있다.
**그래서** 학습 동기를 유지하고 연속 학습일을 관리할 수 있다.

### 상세 정보

| 항목           | 내용                                                                            |
| -------------- | ------------------------------------------------------------------------------- |
| **엔드포인트** | `GET /api/v1/profiles/me/streak`                                                |
| **인증 필요**  | 예                                                                              |
| **출력**       | 현재 스트릭, 최장 스트릭, 마지막 학습일, 이번 달 학습일 수, 스트릭 상태, 메시지 |
| **상태**       | ✅ 구현 완료                                                                    |

### 스트릭 상태 종류

| 상태         | 설명                              |
| ------------ | --------------------------------- |
| `active`     | 오늘 학습 완료, 스트릭 유지 중    |
| `at_risk`    | 오늘 아직 학습 안 함 (위험)       |
| `broken`     | 어제 학습 안 해서 스트릭 끊어짐   |
| `new`        | 첫 학습 또는 스트릭 0             |

### 스트릭 계산 규칙

1. **스트릭 증가**: 오늘 첫 학습 세션 완료 시
2. **스트릭 유지**: 매일 최소 1회 학습 필요
3. **스트릭 리셋**: 하루라도 학습 안 하면 0으로 리셋
4. **최장 기록 갱신**: 현재 스트릭이 최장 기록 초과 시 자동 갱신

### 요청/응답 예시

**성공 응답:**

```json
{
  "current_streak": 7,
  "longest_streak": 15,
  "last_study_date": "2025-12-10",
  "days_studied_this_month": 10,
  "streak_status": "active",
  "message": "🔥 7일 연속 학습 중!"
}
```

### 메시지 예시

| 스트릭 | 메시지 예시                        |
| ------ | ---------------------------------- |
| 0      | "오늘 첫 학습을 시작해보세요!"     |
| 1~6    | "🔥 {n}일 연속 학습 중!"           |
| 7      | "🎉 일주일 연속 학습 달성!"        |
| 30     | "🏆 한 달 연속 학습! 대단해요!"    |
| 100+   | "🌟 100일 돌파! 당신은 진정한 학습자!" |

---

## US-PROFILE-07: 복습 단어 비율 설정 (신규)

### 스토리

**사용자로서**, 학습 시 복습 단어 비율을 일반/커스텀 모드로 설정할 수 있다.
**그래서** 내 학습 스타일에 맞게 새 단어와 복습 단어 비율을 조절할 수 있다.

### 상세 정보

| 항목 | 내용 |
|------|------|
| **엔드포인트** | `PATCH /api/v1/profiles/me` (확장) |
| **인증 필요** | 예 |
| **변경 사항** | `review_ratio_mode`, `custom_review_ratio`, `min_new_ratio` 필드 추가 |
| **상태** | 🔲 미구현 |
| **GitHub** | [#47](https://github.com/ee309-team-goat/loops-api/issues/47) |

### 모드별 동작

| 모드 | 설명 | 적용 로직 |
|------|------|----------|
| `normal` | 일반 모드 (기본) | 새 단어 최소 `min_new_ratio`(25%) 보장 |
| `custom` | 커스텀 모드 | 복습 비율 `custom_review_ratio` 그대로 적용 |

### 스키마 확장

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `review_ratio_mode` | string | `"normal"` | 복습 비율 모드 (normal/custom) |
| `custom_review_ratio` | float | `0.75` | 커스텀 모드 복습 비율 (0.0~1.0) |
| `min_new_ratio` | float | `0.25` | 일반 모드 최소 새 단어 비율 |

### 요청/응답 예시

**요청:**

```
PATCH /api/v1/profiles/me
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "review_ratio_mode": "custom",
  "custom_review_ratio": 0.6
}
```

**성공 응답 (200 OK):**

```json
{
  "id": "...",
  "review_ratio_mode": "custom",
  "custom_review_ratio": 0.6,
  "min_new_ratio": 0.25
}
```

### 예시 계산

**일반 모드 (목표: 20개, min_new_ratio: 0.25):**
- 복습 카드 15개 가능, 새 카드 50개 가능
- 결과: 새 단어 5개(25%), 복습 15개(75%)

**커스텀 모드 (목표: 20개, custom_review_ratio: 0.6):**
- 결과: 새 단어 8개(40%), 복습 12개(60%)

---

## US-PROFILE-08: 복습 범위 설정 (신규)

### 스토리

**사용자로서**, 복습 범위를 "선택한 단어장만" 또는 "학습한 모든 단어" 중에서 선택할 수 있다.
**그래서** 특정 단어장에 집중하거나 전체 어휘를 복습할 수 있다.

### 상세 정보

| 항목 | 내용 |
|------|------|
| **엔드포인트** | `PATCH /api/v1/profiles/me` (확장) |
| **인증 필요** | 예 |
| **변경 사항** | `review_scope` 필드 추가 |
| **상태** | 🔲 미구현 |
| **GitHub** | [#49](https://github.com/ee309-team-goat/loops-api/issues/49) |

### 복습 범위 옵션

| 값 | 설명 | 동작 |
|----|------|------|
| `selected_decks_only` | 선택한 단어장만 (기본, 권장) | 선택된 덱의 카드만 복습 |
| `all_learned` | 학습한 모든 단어 | 덱 상관없이 학습한 모든 카드 복습 |

### 스키마 확장

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `review_scope` | string | `"selected_decks_only"` | 복습 범위 설정 |

### 요청/응답 예시

**요청:**

```
PATCH /api/v1/profiles/me
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "review_scope": "all_learned"
}
```

**성공 응답 (200 OK):**

```json
{
  "id": "...",
  "review_scope": "all_learned"
}
```

### UI 활용 예시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ 복습 범위 설정
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
(●) 선택한 단어장만 [권장]
    선택한 단어장의 어휘만 복습합니다.

( ) 학습한 모든 단어
    지금까지 학습한 모든 어휘를 복습합니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## US-PROFILE-09: 하이라이트 색상 설정 (신규)

### 스토리

**사용자로서**, 문장 내 핵심 단어 하이라이트 색상을 변경할 수 있다.
**그래서** 내 선호에 맞는 색상으로 학습할 수 있다.

### 상세 정보

| 항목 | 내용 |
|------|------|
| **엔드포인트** | `PATCH /api/v1/profiles/me` (확장) |
| **인증 필요** | 예 |
| **변경 사항** | `highlight_color` 필드 추가 |
| **상태** | 🔲 미구현 |
| **GitHub** | [#55](https://github.com/ee309-team-goat/loops-api/issues/55) |

### 권장 색상 프리셋

| 이름 | HEX | 용도 |
|------|-----|------|
| Green | `#4CAF50` | 기본값, 자연스러운 강조 |
| Blue | `#2196F3` | 시원한 느낌 |
| Orange | `#FF9800` | 따뜻한 강조 |
| Purple | `#9C27B0` | 고급스러운 느낌 |
| Red | `#F44336` | 강한 강조 |

### 스키마 확장

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `highlight_color` | string | `"#4CAF50"` | Clue 하이라이트 색상 (HEX 코드) |

### 요청/응답 예시

**요청:**

```
PATCH /api/v1/profiles/me
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "highlight_color": "#2196F3"
}
```

**성공 응답 (200 OK):**

```json
{
  "id": "...",
  "highlight_color": "#2196F3"
}
```

### UI 활용 예시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ 하이라이트 색상
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
현재: 🟢 Green (#4CAF50)

[🟢] [🔵] [🟠] [🟣] [🔴]

미리보기:
"The company signed a <contract> with..."
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 관련 컴포넌트

### 서비스

- `src/app/services/profile_service.py`: 프로필 CRUD 및 통계

### 모델

- `src/app/models/tables/profile.py`: Profile 테이블 정의
- `src/app/models/schemas/profile.py`: 프로필 관련 스키마

### API

- `src/app/api/profiles.py`: 프로필 라우트 핸들러

---

## 관련 문서

- [인증 유저 스토리](./01-authentication.md)
- [통계 유저 스토리](./07-statistics.md)
- [학습 세션 유저 스토리](./08-study-session.md)
