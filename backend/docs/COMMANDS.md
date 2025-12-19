# 명령어 레퍼런스 (Commands Reference)

이 문서는 Loops API 프로젝트에서 사용하는 모든 Just 명령어와 UV 명령어를 설명합니다.

## 📋 목차

- [빠른 참조](#-빠른-참조)
- [개발 워크플로우](#-개발-워크플로우)
- [마이그레이션 명령어](#-마이그레이션-명령어)
- [데이터베이스 작업](#-데이터베이스-작업)
- [Docker 명령어](#-docker-명령어)
- [의존성 관리](#-의존성-관리)
- [UV 명령어](#-uv-명령어)

---

## ⚡ 빠른 참조

```bash
# 전체 명령어 목록 보기
just --list

# 프로젝트 초기 설정
just setup                          # 의존성 설치 + .env 생성

# 개발 서버 시작
just dev                            # 개발 서버 (auto-reload)

# 마이그레이션
just revision "변경사항 설명"       # 마이그레이션 생성
just migrate                        # 마이그레이션 적용
just rollback                       # 마지막 마이그레이션 롤백

# 상태 확인
just info                           # 환경 정보 및 마이그레이션 상태
just db-test                        # DB 연결 테스트
just health                         # API 헬스 체크
```

---

## 🔨 개발 워크플로우

### 프로젝트 시작

```bash
# 프로젝트 초기 설정 (처음 1회)
just setup
# 내용: uv sync + .env 파일 생성

# 개발 서버 시작
just dev
# 내용: uv run python src/main.py
# 포트: http://localhost:8080
```

### 환경 정보 확인

```bash
# 환경 및 마이그레이션 상태 확인
just info
# 표시 내용:
# - Python 버전
# - UV 버전
# - 데이터베이스 URL
# - 현재 마이그레이션 리비전
# - 대기 중인 마이그레이션

# API 헬스 체크
just health
# 요청: curl http://localhost:8080/health
```

### 유틸리티

```bash
# Python 캐시 정리
just clean
# 삭제: __pycache__, *.pyc, .pytest_cache 등
```

---

## 🗄 마이그레이션 명령어

### 기본 명령어

```bash
# 마이그레이션 적용
just migrate
# = uv run alembic upgrade head

# 마이그레이션 생성 (자동 감지)
just revision "설명"
# = uv run alembic revision --autogenerate -m "설명"

# 마지막 마이그레이션 롤백
just rollback
# = uv run alembic downgrade -1
```

### 상태 확인

```bash
# 현재 리비전 확인
just current
# = uv run alembic current

# 최신 리비전 확인
just heads
# = uv run alembic heads

# 마이그레이션 히스토리
just history
# = uv run alembic history

# 대기 중인 마이그레이션 확인
just check-migrations
# 출력: 현재 리비전과 head 리비전 비교

# 마이그레이션 파일 목록
just migrations
# = ls -lh src/alembic/versions/

# 최신 마이그레이션 파일 내용
just migration-latest
# 최신 마이그레이션 파일을 cat으로 표시
```

### 고급 명령어

```bash
# 특정 리비전으로 다운그레이드
just downgrade-to <revision_id>
# = uv run alembic downgrade <revision_id>

# 특정 마이그레이션 상세 정보
just show <revision_id>
# = uv run alembic show <revision_id>

# 여러 브랜치 병합
just merge "merge description"
# = uv run alembic merge heads -m "merge description"

# DB를 특정 리비전으로 표시 (⚠️ 주의: 실제 마이그레이션 실행 안함)
just stamp <revision_id>
# = uv run alembic stamp <revision_id>
# ⚠️ 확인 필요: 데이터베이스를 실제로 변경하지 않고 버전만 기록

# DB 초기화 (base로 다운그레이드 후 head로 업그레이드)
just reset
# ⚠️ 확인 필요: 모든 데이터 삭제됨
```

---

## 💾 데이터베이스 작업

### 데이터 시딩

```bash
# 샘플 데이터 시딩
just db-seed
# = uv run python src/scripts/seed_data.py

# DB 초기화 후 시딩
just db-refresh
# ⚠️ 확인 필요: 모든 데이터 삭제 후 샘플 데이터 추가
# 순서: just reset -> just db-seed
```

### 연결 테스트

```bash
# DB 연결 테스트
just db-test
# Python으로 간단한 SELECT 1 쿼리 실행
```

---

## 🐳 Docker 명령어

### 컨테이너 관리

```bash
# Docker 컨테이너 시작
just docker-up
# = docker-compose up --build

# Docker 백그라운드 시작
just docker-up-d
# = docker-compose up -d --build

# Docker 컨테이너 중지
just docker-down
# = docker-compose down

# Docker 로그 보기 (실시간)
just docker-logs
# = docker-compose logs -f
```

### Docker 내부 마이그레이션

```bash
# Docker 컨테이너 내에서 마이그레이션 적용
just docker-migrate
# = docker-compose exec api uv run alembic upgrade head

# Docker 컨테이너 내에서 마이그레이션 생성
just docker-revision "설명"
# = docker-compose exec api uv run alembic revision --autogenerate -m "설명"

# Docker 컨테이너 내에서 롤백
just docker-rollback
# = docker-compose exec api uv run alembic downgrade -1

# Docker 컨테이너 내 현재 리비전
just docker-current
# = docker-compose exec api uv run alembic current

# Docker 컨테이너 내 히스토리
just docker-history
# = docker-compose exec api uv run alembic history
```

### Docker 데이터베이스 작업

```bash
# Docker DB 초기화
just docker-reset
# ⚠️ 확인 필요: Docker 컨테이너 내 DB 초기화

# Docker DB 시딩
just docker-seed
# = docker-compose exec api uv run python src/scripts/seed_data.py

# Docker DB 초기화 후 시딩
just docker-refresh
# ⚠️ 확인 필요: just docker-reset -> just docker-seed
```

---

## 📦 의존성 관리

```bash
# 의존성 설치/동기화
just install
# = uv sync

# 새 패키지 추가
just add <패키지명>
# = uv add <패키지명>

# 개발 의존성 추가 (직접 UV 사용)
uv add --dev <패키지명>

# 패키지 제거 (직접 UV 사용)
uv remove <패키지명>
```

---

## 💡 UV 명령어

### 패키지 관리

```bash
# 패키지 추가
uv add <패키지>
uv add --dev <패키지>        # 개발 의존성

# 패키지 제거
uv remove <패키지>

# 의존성 동기화
uv sync                      # pyproject.toml 기반

# 의존성 잠금
uv lock                      # uv.lock 파일 업데이트
```

### 가상환경

```bash
# 가상환경 생성
uv venv

# 설치된 패키지 목록
uv pip list

# 의존성 freeze
uv pip freeze
```

### 실행

```bash
# 가상환경에서 명령어 실행
uv run <명령어>

# Python 스크립트 실행
uv run python script.py

# Alembic 직접 실행
uv run alembic upgrade head
uv run alembic revision --autogenerate -m "message"
```

### 유틸리티

```bash
# UV 캐시 정리
uv cache clean

# UV 버전 확인
uv --version

# 특정 패키지 재설치
uv add --reinstall <패키지>
```

---

## 📝 일반적인 워크플로우

### 새로운 프로젝트 시작

```bash
# 1. 저장소 클론
git clone <repository-url>
cd loops-api

# 2. 프로젝트 설정
just setup

# 3. .env 파일 수정
# DATABASE_URL, SECRET_KEY 등 설정

# 4. 마이그레이션 적용
just migrate

# 5. 샘플 데이터 추가 (선택)
just db-seed

# 6. 개발 서버 시작
just dev
```

### 새 모델 추가

```bash
# 1. 모델 파일 생성
# src/app/models/your_model.py

# 2. 모델 등록
# src/app/models/__init__.py에 import 추가

# 3. 마이그레이션 생성
just revision "Add your_model"

# 4. 마이그레이션 파일 검토
just migration-latest

# 5. 마이그레이션 적용
just migrate

# 6. 상태 확인
just current
just check-migrations
```

### Docker로 개발

```bash
# 1. Docker 시작
just docker-up-d

# 2. 마이그레이션 적용
just docker-migrate

# 3. 샘플 데이터 추가
just docker-seed

# 4. 로그 확인
just docker-logs
```

### 문제 해결

```bash
# 1. 환경 정보 확인
just info

# 2. DB 연결 테스트
just db-test

# 3. 마이그레이션 상태 확인
just current
just check-migrations

# 4. 필요시 캐시 정리
just clean

# 5. DB 초기화 (최후의 수단)
just reset
just db-seed
```

---

## ⚠️ 주의사항

### 확인이 필요한 위험한 명령어

다음 명령어들은 데이터를 삭제하거나 예상치 못한 결과를 초래할 수 있으므로 실행 전 확인이 필요합니다:

- `just reset` - 모든 마이그레이션을 롤백 후 재적용
- `just db-refresh` - DB 초기화 후 샘플 데이터 추가
- `just stamp <revision>` - 실제 마이그레이션 없이 버전만 변경
- `just docker-reset` - Docker 내 DB 초기화
- `just docker-refresh` - Docker 내 DB 초기화 후 시딩

### 프로덕션 환경 주의사항

- `DEBUG=False`로 설정
- `DATABASE_ECHO=False`로 설정
- `SECRET_KEY`를 안전한 랜덤 키로 변경
- `ALLOWED_ORIGINS`를 실제 도메인으로 제한
- 마이그레이션 전 DB 백업
- `just reset` 명령어 절대 사용 금지

---

## 📚 관련 문서

- [README.md](../README.md) - 프로젝트 개요
- [API.md](./API.md) - API 엔드포인트 문서
- [DATABASE.md](./DATABASE.md) - 데이터베이스 상세 정보
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결 가이드
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 배포 가이드
