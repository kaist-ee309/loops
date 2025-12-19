# 데이터베이스 가이드 (Database Guide)

Loops API의 데이터베이스 구조, 마이그레이션, 그리고 최적화 방법을 설명합니다.

## 📋 목차

- [데이터베이스 스키마](#-데이터베이스-스키마)
- [마이그레이션 관리](#-마이그레이션-관리)
- [모델 작성 가이드](#-모델-작성-가이드)
- [쿼리 최적화](#-쿼리-최적화)
- [백업 & 복구](#-백업--복구)

---

## 🗄 데이터베이스 스키마

### 테이블 개요

현재 8개의 주요 테이블:

1. **users** - 사용자 정보 및 학습 통계
2. **vocabulary_cards** - 한국어 단어 카드
3. **user_card_progress** - FSRS 기반 학습 진도
4. **decks** - 덱(단어장) 관리
5. **user_decks** - 사용자-덱 관계
6. **study_sessions** - 학습 세션 기록
7. **ai_interactions** - AI 상호작용 로그
8. **sync_queue** - 오프라인 동기화 큐

### ER 다이어그램

```
users (1) ----< (N) user_card_progress
  |                      |
  |                      v
  |              vocabulary_cards (N) >---- (1) decks
  |
  +----< user_decks >---- decks
  |
  +----< study_sessions
  |
  +----< ai_interactions
  |
  +----< sync_queue
```

### 1. users (사용자)

```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    subscription_type VARCHAR(20) DEFAULT 'free',
    total_cards_learned INTEGER DEFAULT 0,
    total_study_time_minutes INTEGER DEFAULT 0,
    current_streak INTEGER DEFAULT 0,
    longest_streak INTEGER DEFAULT 0,
    last_study_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_users_email ON users(email);
CREATE INDEX ix_users_username ON users(username);
```

**주요 필드:**

- `subscription_type`: free, premium, enterprise
- `current_streak`: 연속 학습 일수
- `last_study_date`: 마지막 학습 날짜 (streak 계산용)

### 2. vocabulary_cards (단어 카드)

```sql
CREATE TABLE vocabulary_cards (
    id SERIAL PRIMARY KEY,
    korean_word VARCHAR(100) NOT NULL,
    pronunciation VARCHAR(100),
    meaning TEXT NOT NULL,
    definition_en TEXT,
    difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 10),
    cefr_level VARCHAR(2),
    example_sentences JSONB,
    synonyms JSONB,
    antonyms JSONB,
    related_words JSONB,
    collocations JSONB,
    usage_notes TEXT,
    etymology TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    deck_id INTEGER REFERENCES decks(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_cards_korean_word ON vocabulary_cards(korean_word);
CREATE INDEX ix_cards_difficulty ON vocabulary_cards(difficulty_level);
CREATE INDEX ix_cards_deck_id ON vocabulary_cards(deck_id);
```

**JSONB 필드:**

- `example_sentences`: 예문 배열
- `synonyms`, `antonyms`, `related_words`: 관련 단어 배열
- `collocations`: 연어(collocation) 배열

### 3. user_card_progress (학습 진도 - FSRS)

```sql
CREATE TABLE user_card_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    card_id INTEGER NOT NULL REFERENCES vocabulary_cards(id) ON DELETE CASCADE,

    -- FSRS 핵심 필드
    stability FLOAT DEFAULT 0.0,
    difficulty FLOAT DEFAULT 5.0,
    interval INTEGER DEFAULT 0,
    scheduled_days INTEGER DEFAULT 0,
    lapses INTEGER DEFAULT 0,
    reps_since_lapse INTEGER DEFAULT 0,
    elapsed_days INTEGER DEFAULT 0,
    card_state VARCHAR(20) DEFAULT 'new',

    -- 통계 필드
    total_reviews INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    wrong_count INTEGER DEFAULT 0,
    accuracy_rate FLOAT DEFAULT 0.0,
    repetitions INTEGER DEFAULT 0,
    average_response_time INTEGER,

    -- 타이밍 필드
    next_review_date TIMESTAMP,
    last_review_date TIMESTAMP,
    first_studied_at TIMESTAMP,
    mastered_at TIMESTAMP,

    -- 기록
    quality_history JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, card_id)
);

CREATE INDEX ix_progress_user_card ON user_card_progress(user_id, card_id);
CREATE INDEX ix_progress_next_review ON user_card_progress(next_review_date);
CREATE INDEX ix_progress_card_state ON user_card_progress(card_state);
```

**FSRS 필드 설명:**

- `stability`: 기억 안정성 (FSRS 계산값)
- `difficulty`: 난이도 1-10
- `card_state`: NEW, LEARNING, REVIEW, RELEARNING
- `quality_history`: 복습 기록 (날짜, rating, interval 등)

### 4. decks (덱)

```sql
CREATE TABLE decks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    creator_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    is_public BOOLEAN DEFAULT FALSE,
    card_count INTEGER DEFAULT 0,
    learning_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_decks_creator ON decks(creator_id);
CREATE INDEX ix_decks_public ON decks(is_public);
```

### 5. user_decks (사용자-덱 관계)

```sql
CREATE TABLE user_decks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    deck_id INTEGER NOT NULL REFERENCES decks(id) ON DELETE CASCADE,
    is_active BOOLEAN DEFAULT TRUE,
    cards_new INTEGER DEFAULT 0,
    cards_learning INTEGER DEFAULT 0,
    cards_review INTEGER DEFAULT 0,
    progress_percentage FLOAT DEFAULT 0.0,
    last_studied_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(user_id, deck_id)
);

CREATE INDEX ix_user_decks_user ON user_decks(user_id);
CREATE INDEX ix_user_decks_deck ON user_decks(deck_id);
```

### 6. study_sessions (학습 세션)

```sql
CREATE TABLE study_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    deck_id INTEGER REFERENCES decks(id) ON DELETE SET NULL,
    duration_minutes INTEGER NOT NULL,
    cards_studied INTEGER NOT NULL,
    accuracy_rate FLOAT,
    device_type VARCHAR(50),
    session_date TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_sessions_user ON study_sessions(user_id);
CREATE INDEX ix_sessions_date ON study_sessions(session_date);
```

### 7. ai_interactions (AI 상호작용)

```sql
CREATE TABLE ai_interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    interaction_type VARCHAR(50),
    model_used VARCHAR(100),
    user_input TEXT,
    ai_response TEXT,
    tokens_used INTEGER,
    response_time_ms INTEGER,
    feedback_rating INTEGER CHECK (feedback_rating BETWEEN 1 AND 5),
    interaction_timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_ai_user ON ai_interactions(user_id);
```

### 8. sync_queue (동기화 큐)

```sql
CREATE TABLE sync_queue (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER NOT NULL,
    operation VARCHAR(20) NOT NULL,
    payload JSONB,
    is_synced BOOLEAN DEFAULT FALSE,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    priority INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    synced_at TIMESTAMP,
    last_retry_at TIMESTAMP
);

CREATE INDEX ix_sync_user ON sync_queue(user_id);
CREATE INDEX ix_sync_synced ON sync_queue(is_synced);
CREATE INDEX ix_sync_entity ON sync_queue(entity_type, entity_id);
```

---

## 🔄 마이그레이션 관리

### 마이그레이션 생성

```bash
# 모델 변경 후 자동으로 마이그레이션 생성
just revision "Add new field to users"

# 또는 수동으로
uv run alembic revision --autogenerate -m "Add new field"

# 빈 마이그레이션 (수동 작성용)
uv run alembic revision -m "Custom migration"
```

### 마이그레이션 파일 위치

```
src/alembic/versions/
├── 20250120_1234_initial_migration.py
├── 20250120_1235_add_users_table.py
└── 20250120_1236_add_cards_table.py
```

### 마이그레이션 파일 구조

```python
"""Add user profile fields

Revision ID: abc123def456
Revises: previous_revision
Create Date: 2025-01-20 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123def456'
down_revision = 'previous_revision'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """업그레이드 (마이그레이션 적용)"""
    op.add_column('users',
        sa.Column('bio', sa.Text(), nullable=True)
    )
    op.create_index('ix_users_bio', 'users', ['bio'])

def downgrade() -> None:
    """다운그레이드 (마이그레이션 롤백)"""
    op.drop_index('ix_users_bio', table_name='users')
    op.drop_column('users', 'bio')
```

### 일반적인 마이그레이션 작업

```python
# 컬럼 추가
op.add_column('table_name',
    sa.Column('column_name', sa.String(50), nullable=True)
)

# 컬럼 삭제
op.drop_column('table_name', 'column_name')

# 컬럼 타입 변경
op.alter_column('table_name', 'column_name',
    existing_type=sa.String(50),
    type_=sa.String(100)
)

# 인덱스 생성
op.create_index('ix_table_column', 'table_name', ['column_name'])

# 인덱스 삭제
op.drop_index('ix_table_column', table_name='table_name')

# 외래 키 추가
op.create_foreign_key(
    'fk_user_id', 'table_name', 'users',
    ['user_id'], ['id'], ondelete='CASCADE'
)

# 테이블 생성
op.create_table(
    'new_table',
    sa.Column('id', sa.Integer(), primary_key=True),
    sa.Column('name', sa.String(100), nullable=False)
)
```

### 데이터 마이그레이션

```python
from sqlalchemy.sql import table, column

def upgrade():
    # 임시 테이블 정의
    users = table('users',
        column('id', sa.Integer),
        column('old_field', sa.String),
        column('new_field', sa.String)
    )

    # 데이터 업데이트
    op.execute(
        users.update().values(
            new_field=users.c.old_field
        )
    )

    # 구 컬럼 삭제
    op.drop_column('users', 'old_field')
```

---

## 📝 모델 작성 가이드

### 기본 모델 패턴

```python
from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional
from datetime import datetime

# 1. Base 스키마
class YourModelBase(SQLModel):
    name: str = Field(max_length=255)
    description: Optional[str] = None

# 2. 테이블 모델
class YourModel(YourModelBase, table=True):
    __tablename__ = "your_models"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")

    # JSONB 필드
    metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))

    # 타임스탬프
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# 3. Create 스키마 (POST용)
class YourModelCreate(YourModelBase):
    user_id: int

# 4. Read 스키마 (응답용)
class YourModelRead(YourModelBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

# 5. Update 스키마 (PATCH용)
class YourModelUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
```

### Enum 타입 사용

```python
import enum
from sqlmodel import Column, Enum as SQLEnum

class SubscriptionType(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"
    ENTERPRISE = "enterprise"

class User(SQLModel, table=True):
    subscription_type: SubscriptionType = Field(
        default=SubscriptionType.FREE,
        sa_column=Column(SQLEnum(SubscriptionType), nullable=False)
    )
```

### 인덱스 추가

```python
from sqlmodel import Field, Column, String

class Card(SQLModel, table=True):
    korean_word: str = Field(
        sa_column=Column(String(100), index=True)  # 인덱스 추가
    )
```

---

## ⚡ 쿼리 최적화

### N+1 문제 해결

```python
from sqlmodel import select
from sqlalchemy.orm import selectinload

# ❌ 나쁜 예: N+1 쿼리
users = await session.execute(select(User))
for user in users:
    # 각 사용자마다 추가 쿼리 발생
    cards = await session.execute(
        select(UserCardProgress).where(UserCardProgress.user_id == user.id)
    )

# ✅ 좋은 예: eager loading
statement = select(User).options(
    selectinload(User.card_progress)
)
users = await session.execute(statement)
```

### 페이지네이션

```python
async def get_cards(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[VocabularyCard]:
    statement = (
        select(VocabularyCard)
        .offset(skip)
        .limit(limit)
        .order_by(VocabularyCard.created_at.desc())
    )
    result = await session.execute(statement)
    return list(result.scalars().all())
```

### 필요한 컬럼만 조회

```python
from sqlalchemy import select

# ❌ 모든 컬럼 조회
cards = await session.execute(select(VocabularyCard))

# ✅ 필요한 컬럼만
statement = select(
    VocabularyCard.id,
    VocabularyCard.korean_word,
    VocabularyCard.meaning
)
cards = await session.execute(statement)
```

### 집계 쿼리

```python
from sqlalchemy import func

# 총 개수
statement = select(func.count(VocabularyCard.id))
count = await session.execute(statement)
total = count.scalar()

# 평균
statement = select(func.avg(UserCardProgress.accuracy_rate))
avg = await session.execute(statement)
average_accuracy = avg.scalar()
```

---

## 💾 백업 & 복구

### 수동 백업

```bash
# 전체 데이터베이스 백업
pg_dump -U postgres -d loops > backup_$(date +%Y%m%d_%H%M%S).sql

# 특정 테이블만
pg_dump -U postgres -d loops -t users > users_backup.sql

# 압축 백업
pg_dump -U postgres -d loops | gzip > backup.sql.gz
```

### 복구

```bash
# SQL 파일에서 복구
psql -U postgres -d loops < backup_20250120_120000.sql

# 압축 파일에서 복구
gunzip -c backup.sql.gz | psql -U postgres -d loops
```

### 자동 백업 스크립트

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
DB_NAME="loops"

# 백업 생성
pg_dump -U postgres -d $DB_NAME | gzip > $BACKUP_DIR/backup_$TIMESTAMP.sql.gz

# 7일 이상 된 백업 삭제
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$TIMESTAMP.sql.gz"
```

### Cron으로 자동화

```bash
# crontab -e
# 매일 새벽 2시에 백업
0 2 * * * /path/to/backup.sh
```

---

## 📚 관련 문서

- [README.md](../README.md) - 프로젝트 개요
- [COMMANDS.md](./COMMANDS.md) - 명령어 레퍼런스
- [API.md](./API.md) - API 문서
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 문제 해결 가이드
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 배포 가이드
