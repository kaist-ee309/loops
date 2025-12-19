# 문제 해결 가이드 (Troubleshooting Guide)

Loops API 개발 중 발생할 수 있는 일반적인 문제와 해결 방법을 설명합니다.

## 📋 목차

- [데이터베이스 문제](#-데이터베이스-문제)
- [마이그레이션 문제](#-마이그레이션-문제)
- [인증 & JWT 문제](#-인증--jwt-문제)
- [Docker 문제](#-docker-문제)
- [패키지 & 의존성 문제](#-패키지--의존성-문제)
- [FSRS 관련 문제](#-fsrs-관련-문제)
- [포트 & 네트워크 문제](#-포트--네트워크-문제)
- [성능 & 메모리 문제](#-성능--메모리-문제)

---

## 🗄 데이터베이스 문제

### 데이터베이스 연결 실패

**증상:**

```
OSError: Connect call failed
sqlalchemy.exc.OperationalError: could not connect to server
```

**해결 방법:**

```bash
# 1. PostgreSQL이 실행 중인지 확인
just docker-up          # Docker 사용 시

# 또는 로컬 PostgreSQL
pg_ctl status
pg_ctl start            # 실행 안되어 있으면

# 2. 연결 테스트
just db-test

# 3. .env 파일 확인
cat .env | grep DATABASE_URL

# 4. DATABASE_URL 형식 확인
# 올바른 형식:
DATABASE_URL=postgresql+asyncpg://user:password@host:port/database

# Docker 사용 시:
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/loops

# 로컬 PostgreSQL:
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/loops

# Supabase:
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### 데이터베이스가 없음

**증상:**

```
sqlalchemy.exc.OperationalError: database "loops" does not exist
```

**해결 방법:**

```bash
# PostgreSQL에 연결하여 데이터베이스 생성
createdb loops

# 또는 psql로
psql -U postgres
CREATE DATABASE loops;
\q

# Docker 사용 시 (docker-compose.yaml에 정의되어 있으면 자동 생성)
just docker-down
just docker-up
```

### 권한 문제

**증상:**

```
psycopg2.OperationalError: FATAL: password authentication failed
```

**해결 방법:**

```bash
# 1. .env 파일의 비밀번호 확인
cat .env | grep DATABASE_URL

# 2. PostgreSQL 비밀번호 재설정 (필요시)
psql -U postgres
ALTER USER postgres PASSWORD 'new_password';

# 3. .env 파일 업데이트
DATABASE_URL=postgresql+asyncpg://postgres:new_password@localhost:5432/loops
```

---

## 🔄 마이그레이션 문제

### 마이그레이션 자동 감지 안됨

**증상:**

```
INFO  [alembic.autogenerate.compare] Detected NULL
```

**해결 방법:**

```bash
# 1. 모델이 __init__.py에 임포트되었는지 확인
cat src/app/models/__init__.py

# 2. 모델이 없으면 추가
# src/app/models/__init__.py
from app.models.your_model import YourModel, YourModelCreate, YourModelRead

__all__ = [
    ...,
    "YourModel",
    "YourModelCreate",
    "YourModelRead",
]

# 3. Python 캐시 정리
just clean

# 4. 마이그레이션 재생성
just revision "Add your_model"
```

### 마이그레이션 충돌

**증상:**

```
ERROR [alembic.util.messaging] Multiple head revisions are present
```

**해결 방법:**

```bash
# 1. 현재 상태 확인
just heads
just history

# 2. 여러 head 병합
just merge "Merge multiple heads"

# 3. 병합된 마이그레이션 적용
just migrate
```

### 마이그레이션 롤백 실패

**증상:**

```
ERROR [alembic.runtime.migration] Can't locate revision identified by...
```

**해결 방법:**

```bash
# 1. 현재 리비전 확인
just current

# 2. 히스토리 확인
just history

# 3. 특정 리비전으로 다운그레이드
just downgrade-to <revision_id>

# 4. 최후의 수단: DB 초기화 (⚠️ 데이터 삭제됨)
just reset
just db-seed
```

### 마이그레이션 적용 오류

**증상:**

```
sqlalchemy.exc.ProgrammingError: relation "table_name" already exists
```

**해결 방법:**

```bash
# 1. 데이터베이스와 마이그레이션 상태가 불일치
# 현재 DB 상태를 특정 리비전으로 표시
just stamp <current_revision_id>

# 2. 또는 깨끗하게 다시 시작
just reset
just migrate
```

---

## 🔐 인증 & JWT 문제

### JWT 토큰 invalid 오류

**증상:**

```
HTTPException: Could not validate credentials
401 Unauthorized
```

**해결 방법:**

```bash
# 1. .env 파일의 SECRET_KEY 확인
cat .env | grep SECRET_KEY

# 2. SECRET_KEY가 비어있거나 기본값이면 새로 생성
openssl rand -hex 32

# 3. .env 파일에 추가
SECRET_KEY=생성된_키_여기에_붙여넣기

# 4. 서버 재시작
just dev

# 5. 새로 로그인하여 토큰 재발급
```

### 토큰 만료

**증상:**

```
Token has expired
```

**해결 방법:**

```bash
# 1. 로그인하여 새 토큰 발급
curl -X POST http://localhost:8080/api/v1/auth/login \
  -d "username=testuser&password=password123"

# 2. 토큰 만료 시간 조정 (필요시)
# .env 파일에 추가
ACCESS_TOKEN_EXPIRE_MINUTES=60  # 기본값: 30분
```

### 비밀번호 해싱 오류

**증상:**

```
ValueError: Invalid salt
```

**해결 방법:**

```bash
# 1. passlib 재설치
uv add --reinstall passlib[bcrypt]

# 2. 서버 재시작
just dev

# 3. 필요시 사용자 비밀번호 재설정
# (DB에서 직접 수정하지 말고 API 통해 변경)
```

---

## 🐳 Docker 문제

### Docker 컨테이너 시작 실패

**증상:**

```
ERROR: Cannot start service...
```

**해결 방법:**

```bash
# 1. 실행 중인 컨테이너 확인 및 중지
docker ps -a
just docker-down

# 2. 볼륨까지 삭제하고 재시작
docker-compose down -v
just docker-up

# 3. 빌드 캐시 없이 재빌드
docker-compose build --no-cache
docker-compose up
```

### Docker 네트워크 오류

**증상:**

```
ERROR: Network loops-api_default declared as external, but could not be found
```

**해결 방법:**

```bash
# 1. Docker 네트워크 정리
docker network prune

# 2. 컨테이너 재시작
just docker-down
just docker-up
```

### Docker 볼륨 문제

**증상:**

```
데이터가 사라짐 또는 이전 데이터가 남아있음
```

**해결 방법:**

```bash
# 1. 볼륨 목록 확인
docker volume ls

# 2. 특정 볼륨 삭제
docker volume rm loops-api_postgres_data

# 3. 사용하지 않는 볼륨 전체 정리
docker volume prune

# 4. 컨테이너 재시작
just docker-up
just docker-migrate
```

### Docker 로그 확인

```bash
# 실시간 로그 확인
just docker-logs

# 특정 서비스 로그만
docker-compose logs -f api
docker-compose logs -f db

# 최근 100줄만
docker-compose logs --tail=100
```

---

## 📦 패키지 & 의존성 문제

### ImportError: cannot import name

**증상:**

```
ImportError: cannot import name 'FSRS' from 'fsrs'
```

**해결 방법:**

```bash
# 1. 패키지 목록 확인
uv pip list | grep fsrs

# 2. 올바른 import 확인 (FSRS 6.3.0의 경우)
# from fsrs import FSRS, Card, Rating  # ❌ 잘못됨
from fsrs import Scheduler, Card, Rating  # ✅ 올바름

# 3. 캐시 정리
just clean

# 4. 패키지 재설치
uv add --reinstall fsrs
```

### UV 동기화 오류

**증상:**

```
error: Failed to download distributions
```

**해결 방법:**

```bash
# 1. UV 캐시 정리
uv cache clean

# 2. 가상환경 삭제 후 재생성
rm -rf .venv
uv sync

# 3. 특정 패키지만 재설치
uv remove <패키지>
uv add <패키지>
```

### Python 버전 불일치

**증상:**

```
ERROR: Python 3.12 is required
```

**해결 방법:**

```bash
# 1. 현재 Python 버전 확인
python --version

# 2. Python 3.12+ 설치 (macOS)
brew install python@3.12

# 3. UV가 올바른 Python 사용하도록 설정
uv venv --python python3.12

# 4. 의존성 재설치
uv sync
```

---

## 🧮 FSRS 관련 문제

### FSRS 계산 오류

**증상:**

```
TypeError: unsupported operand type(s)
```

**해결 방법:**

```bash
# 1. fsrs 패키지 버전 확인
uv pip list | grep fsrs

# 2. 최신 버전으로 업데이트
uv add --upgrade fsrs

# 3. 코드에서 올바른 타입 사용 확인
# stability, difficulty는 float
# interval, scheduled_days는 int
```

### Rating 값 오류

**증상:**

```
ValueError: Rating must be 1 (Again), 2 (Hard), 3 (Good), or 4 (Easy)
```

**해결 방법:**

```python
# API 요청 시 rating은 1-4 사이 정수만 허용
{
  "card_id": 1,
  "rating": 3  # 1, 2, 3, 4 중 하나
}
```

---

## 🌐 포트 & 네트워크 문제

### 포트 이미 사용 중

**증상:**

```
OSError: [Errno 48] Address already in use
```

**해결 방법:**

```bash
# 1. 8080번 포트 사용 프로세스 확인
lsof -i :8080

# 2. 프로세스 종료
kill -9 <PID>

# 3. 또는 다른 포트 사용
# src/main.py 또는 .env에서 포트 변경
uvicorn.run("app.main:app", host="0.0.0.0", port=8001)
```

### CORS 오류

**증상:**

```
Access to fetch at '...' has been blocked by CORS policy
```

**해결 방법:**

```bash
# .env 파일에서 ALLOWED_ORIGINS 확인
ALLOWED_ORIGINS=*  # 개발 환경

# 프로덕션에서는 특정 도메인만 허용
ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## ⚡ 성능 & 메모리 문제

### 메모리 부족

**증상:**

```
MemoryError
Out of memory
```

**해결 방법:**

```bash
# 1. 불필요한 컨테이너 정리
docker system prune -a

# 2. 쿼리에 limit 추가
# 잘못된 예
cards = await session.execute(select(VocabularyCard))

# 올바른 예
cards = await session.execute(
    select(VocabularyCard).limit(100)
)

# 3. Docker 메모리 제한 조정
# docker-compose.yaml에 추가
services:
  api:
    mem_limit: 1g
```

### 느린 쿼리

**증상:**

```
응답 시간이 느림
```

**해결 방법:**

```bash
# 1. DATABASE_ECHO=True로 설정하여 SQL 쿼리 확인
# .env
DATABASE_ECHO=True

# 2. 필요한 필드에 인덱스 추가
# 마이그레이션에서:
op.create_index('ix_cards_korean_word', 'vocabulary_cards', ['korean_word'])

# 3. 불필요한 관계 로딩 제거
# eager loading 대신 필요할 때만 로딩
```

---

## 🔍 디버깅 팁

### 로그 레벨 조정

```python
# src/main.py에 추가
import logging

logging.basicConfig(level=logging.DEBUG)
```

### 환경 정보 확인

```bash
# 전체 환경 정보
just info

# Python 버전
python --version

# UV 버전
uv --version

# Docker 버전
docker --version
docker-compose --version

# 설치된 패키지
uv pip list
```

### 데이터베이스 직접 확인

```bash
# PostgreSQL 접속
psql -U postgres -d loops

# 테이블 목록
\dt

# 특정 테이블 스키마
\d vocabulary_cards

# 간단한 쿼리
SELECT * FROM users LIMIT 10;

# 종료
\q
```

---

## 📞 추가 도움

여전히 문제가 해결되지 않으면:

1. **로그 확인**: `just docker-logs` 또는 콘솔 출력 확인
2. **환경 정보**: `just info` 결과 확인
3. **데이터베이스 상태**: `just current`, `just check-migrations` 확인
4. **GitHub Issues**: 프로젝트 저장소에 이슈 등록
5. **문서 재확인**: [README.md](../README.md), [CLAUDE.md](../CLAUDE.md)

---

## 📚 관련 문서

- [README.md](../README.md) - 프로젝트 개요
- [COMMANDS.md](./COMMANDS.md) - 명령어 레퍼런스
- [API.md](./API.md) - API 문서
- [DATABASE.md](./DATABASE.md) - 데이터베이스 정보
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 배포 가이드
