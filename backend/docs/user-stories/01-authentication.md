# 인증 (Authentication) 유저 스토리

> Supabase Auth를 통한 사용자 인증 관리
>
> 최종 업데이트: 2025-12-10

---

## 개요

인증 도메인은 사용자의 회원가입, 로그인, 토큰 관리, 로그아웃 기능을 담당합니다.
Supabase Auth를 백엔드로 사용하여 안전한 JWT 기반 인증을 제공합니다.

### 주요 특징

- **Supabase Auth 통합**: 자체 인증 시스템 대신 Supabase의 검증된 인증 서비스 활용
- **JWT 토큰 기반**: Access Token과 Refresh Token을 통한 stateless 인증
- **프로필 자동 생성**: 회원가입 시 Supabase 계정과 연동된 로컬 프로필 자동 생성

### 인증 흐름

```
[클라이언트] → POST /auth/register → [Supabase Auth 계정 생성] → [로컬 Profile 생성] → [토큰 반환]
[클라이언트] → POST /auth/login → [Supabase Auth 검증] → [토큰 반환]
[클라이언트] → Authorization: Bearer {token} → [API 요청]
```

---

## US-AUTH-01: 회원가입

### 스토리

**사용자로서**, 이메일과 비밀번호로 회원가입을 할 수 있다.
**그래서** 앱의 모든 기능을 사용할 수 있다.

### 상세 정보

| 항목           | 내용                                    |
| -------------- | --------------------------------------- |
| **엔드포인트** | `POST /api/v1/auth/register`            |
| **인증 필요**  | 아니오                                  |
| **입력**       | 이메일, 비밀번호 (8자 이상)             |
| **출력**       | 액세스 토큰, 리프레시 토큰, 프로필 정보 |
| **상태**       | ✅ 구현 완료                            |

### 비즈니스 규칙

1. **이메일 유효성**: RFC 5322 표준에 맞는 이메일 형식만 허용
2. **비밀번호 정책**: 최소 8자 이상 (추후 복잡성 요구사항 추가 가능)
3. **중복 체크**: 이미 등록된 이메일로는 가입 불가
4. **원자적 처리**: Supabase 계정 생성과 로컬 프로필 생성이 함께 완료되어야 함

### 인수 조건 (Acceptance Criteria)

- [x] 이메일 형식 유효성 검사
- [x] 비밀번호 최소 8자 이상
- [x] 중복 이메일 체크
- [x] Supabase Auth와 로컬 DB에 프로필 동시 생성
- [x] 가입 즉시 로그인 상태 (토큰 발급)

### 요청/응답 예시

**요청:**

```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**성공 응답 (201 Created):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "profile": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "daily_goal": 20,
    "current_streak": 0,
    "longest_streak": 0,
    "created_at": "2025-12-10T10:00:00Z"
  }
}
```

**에러 응답:**

- `400 Bad Request`: 이메일 중복 또는 유효하지 않은 데이터
- `422 Unprocessable Entity`: 필수 필드 누락 또는 형식 오류

### 관련 컴포넌트

- `src/app/api/auth.py`: 라우트 핸들러
- `src/app/services/profile_service.py`: 프로필 생성 로직
- `src/app/core/security.py`: Supabase 클라이언트

---

## US-AUTH-02: 로그인

### 스토리

**사용자로서**, 이메일과 비밀번호로 로그인할 수 있다.
**그래서** 내 학습 데이터에 접근할 수 있다.

### 상세 정보

| 항목           | 내용                                    |
| -------------- | --------------------------------------- |
| **엔드포인트** | `POST /api/v1/auth/login`               |
| **인증 필요**  | 아니오                                  |
| **입력**       | 이메일, 비밀번호                        |
| **출력**       | 액세스 토큰, 리프레시 토큰, 프로필 정보 |
| **상태**       | ✅ 구현 완료                            |

### 비즈니스 규칙

1. **자격 증명 검증**: Supabase Auth를 통해 이메일/비밀번호 검증
2. **프로필 연동**: 인증 성공 시 로컬 DB에서 프로필 정보 조회
3. **토큰 발급**: Access Token (단기)과 Refresh Token (장기) 발급

### 인수 조건

- [x] 올바른 자격 증명 시 토큰 발급
- [x] 잘못된 자격 증명 시 401 반환
- [x] 프로필 정보 함께 반환

### 요청/응답 예시

**요청:**

```json
{
  "email": "user@example.com",
  "password": "securePassword123!"
}
```

**성공 응답 (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "profile": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "daily_goal": 20,
    "current_streak": 7,
    "longest_streak": 15,
    "last_study_date": "2025-12-09",
    "created_at": "2025-11-01T10:00:00Z"
  }
}
```

**에러 응답:**

- `401 Unauthorized`: 이메일 또는 비밀번호가 잘못됨
- `404 Not Found`: Supabase에는 있지만 로컬 DB에 프로필이 없는 경우

### 토큰 사용법

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## US-AUTH-03: 토큰 갱신

### 스토리

**사용자로서**, 리프레시 토큰으로 새 액세스 토큰을 발급받을 수 있다.
**그래서** 재로그인 없이 앱을 계속 사용할 수 있다.

### 상세 정보

| 항목           | 내용                             |
| -------------- | -------------------------------- |
| **엔드포인트** | `POST /api/v1/auth/refresh`      |
| **인증 필요**  | 아니오 (리프레시 토큰 필요)      |
| **입력**       | 리프레시 토큰                    |
| **출력**       | 새 액세스 토큰, 새 리프레시 토큰 |
| **상태**       | ✅ 구현 완료                     |

### 비즈니스 규칙

1. **토큰 회전**: 리프레시 토큰 사용 시 새로운 토큰 쌍 발급 (보안 강화)
2. **만료 체크**: 리프레시 토큰이 만료되면 재로그인 필요

### 사용 시나리오

```
1. 클라이언트가 API 요청 시 401 Unauthorized 수신
2. 저장된 리프레시 토큰으로 /auth/refresh 호출
3. 새 토큰 쌍 수신 및 저장
4. 원래 요청 재시도
```

### 요청/응답 예시

**요청:**

```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**성공 응답 (200 OK):**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...(new)",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...(new)",
  "token_type": "bearer",
  "profile": { ... }
}
```

**에러 응답:**

- `401 Unauthorized`: 리프레시 토큰이 유효하지 않거나 만료됨

---

## US-AUTH-04: 로그아웃

### 스토리

**사용자로서**, 로그아웃할 수 있다.
**그래서** 다른 기기에서 내 계정을 안전하게 보호할 수 있다.

### 상세 정보

| 항목           | 내용                       |
| -------------- | -------------------------- |
| **엔드포인트** | `POST /api/v1/auth/logout` |
| **인증 필요**  | 예                         |
| **출력**       | 성공 메시지                |
| **상태**       | ✅ 구현 완료               |

### 비즈니스 규칙

1. **클라이언트 책임**: 실제 토큰 무효화는 클라이언트에서 처리 (로컬 스토리지 삭제)
2. **서버 응답**: 서버는 로그아웃 의도 확인 후 성공 응답 반환

### 클라이언트 구현 가이드

```javascript
// 로그아웃 처리 예시
async function logout() {
  await api.post("/auth/logout");
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  router.push("/login");
}
```

### 요청/응답 예시

**요청:**

```
POST /api/v1/auth/logout
Authorization: Bearer {access_token}
```

**성공 응답 (200 OK):**

```json
{
  "message": "Successfully logged out"
}
```

---

## US-AUTH-05: 현재 사용자 정보 조회

### 스토리

**사용자로서**, 현재 로그인된 내 정보를 확인할 수 있다.
**그래서** 내 계정 상태를 파악할 수 있다.

### 상세 정보

| 항목           | 내용                  |
| -------------- | --------------------- |
| **엔드포인트** | `GET /api/v1/auth/me` |
| **인증 필요**  | 예                    |
| **출력**       | 프로필 정보           |
| **상태**       | ✅ 구현 완료          |

### 사용 시나리오

1. **앱 시작 시**: 저장된 토큰 유효성 확인 및 사용자 정보 로드
2. **프로필 화면**: 현재 사용자 정보 표시
3. **토큰 검증**: 토큰이 유효한지 빠르게 확인

### 요청/응답 예시

**요청:**

```
GET /api/v1/auth/me
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

**에러 응답:**

- `401 Unauthorized`: 유효한 토큰이 필요함

---

## 보안 고려사항

### 토큰 보안

| 토큰 유형       | 만료 시간 | 저장 위치 권장      |
| --------------- | --------- | ------------------- |
| Access Token    | 1시간     | 메모리 또는 세션    |
| Refresh Token   | 7일       | Secure Cookie/Keychain |

### 보안 체크리스트

- [ ] HTTPS 필수 사용
- [ ] 토큰을 URL 파라미터에 포함하지 않음
- [ ] 클라이언트에서 토큰 만료 시간 관리
- [ ] 비밀번호 입력 필드 마스킹
- [ ] 로그인 실패 횟수 제한 (Supabase 기본 제공)

---

## 테스트 예제

### Curl

```bash
# 회원가입
curl -X POST http://localhost:8080/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# 로그인 & 토큰 저장
TOKEN=$(curl -s -X POST http://localhost:8080/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' | jq -r .access_token)

# 현재 사용자 정보 조회
curl -X GET http://localhost:8080/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"

# 토큰 갱신
curl -X POST http://localhost:8080/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"your_refresh_token_here"}'

# 로그아웃
curl -X POST http://localhost:8080/api/v1/auth/logout \
  -H "Authorization: Bearer $TOKEN"
```

### Python

```python
import requests

BASE_URL = "http://localhost:8080/api/v1"

# 회원가입
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "test@example.com",
    "password": "password123"
})
print(response.json())

# 로그인
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "test@example.com",
    "password": "password123"
})
tokens = response.json()
access_token = tokens["access_token"]
headers = {"Authorization": f"Bearer {access_token}"}

# 현재 사용자 정보 조회
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
user = response.json()
print(user)

# 토큰 갱신
response = requests.post(f"{BASE_URL}/auth/refresh", json={
    "refresh_token": tokens["refresh_token"]
})
new_tokens = response.json()

# 로그아웃
response = requests.post(f"{BASE_URL}/auth/logout", headers=headers)
print(response.json())
```

---

## 관련 문서

- [프로필 유저 스토리](./02-profile.md)
- [학습 진행 유저 스토리](./05-progress.md)
