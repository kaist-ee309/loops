# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Loops API is a FastAPI backend for a Korean vocabulary learning application using FSRS (Free Spaced Repetition Scheduler) algorithm. It features AI-powered tutoring via LangGraph/OpenAI, image generation via Gemini, Supabase authentication & storage, and async PostgreSQL operations with SQLModel.

**Tech Stack:**
- **Framework**: FastAPI 0.121+
- **ORM**: SQLModel (SQLAlchemy + Pydantic)
- **Database**: PostgreSQL (async via asyncpg)
- **Auth & Storage**: Supabase
- **Learning Algorithm**: py-fsrs 6.3
- **AI/LLM**: LangChain + LangGraph + OpenAI
- **Image Generation**: Google Gemini
- **Package Manager**: uv

## Common Commands

This project uses [just](https://just.systems) as a command runner. Install with `brew install just` (macOS).

```bash
# Development
just dev                    # Start dev server (port 8000)
just setup                  # Initial setup (install deps, create .env)
just install                # Install dependencies (uv sync)

# Database Migrations
just migrate                # Apply migrations
just revision "message"     # Create new migration (requires confirmation)
just rollback               # Rollback last migration
just current                # Show current revision
just history                # View migration history
just check-migrations       # Check for pending migrations

# Database
just db-seed                # Seed with sample data
just db-test                # Test database connection
just reset                  # Reset database (⚠️ destructive)

# Docker
just docker-up              # Start containers
just docker-down            # Stop containers
just docker-logs            # View logs
just docker-migrate         # Apply migrations in Docker

# Utilities
just info                   # Show environment info
just health                 # Check API health (requires running server)
just clean                  # Clean Python cache
```

**Raw commands** (without just):

```bash
uv run python src/main.py                           # Start server
uv run alembic upgrade head                         # Apply migrations
uv run alembic revision --autogenerate -m "msg"     # Create migration
```

## Architecture

### Directory Structure

```text
src/
├── app/
│   ├── main.py              # FastAPI app, middleware, exception handlers
│   ├── config.py            # Settings (pydantic-settings)
│   ├── database.py          # Async session factory, engine
│   ├── api/                  # Route handlers (domain-based)
│   │   ├── routes.py         # Router aggregator
│   │   ├── auth.py           # Authentication (Supabase)
│   │   ├── profiles.py       # User profiles
│   │   ├── cards.py          # Vocabulary cards
│   │   ├── decks.py          # Deck management
│   │   ├── study.py          # Study sessions
│   │   ├── tutor.py          # AI Word Tutor chat
│   │   └── stats.py          # Statistics
│   ├── constants/
│   │   └── categories.py     # Vocabulary categories
│   ├── core/
│   │   ├── security.py       # Supabase client, token verification
│   │   ├── dependencies.py   # FastAPI dependencies (CurrentActiveProfile)
│   │   ├── exceptions.py     # Custom exception classes
│   │   └── logging.py        # Structured logging (loguru)
│   ├── models/
│   │   ├── base.py           # TimestampMixin
│   │   ├── enums.py          # CardState, SessionStatus, QuizType, ChatRole
│   │   ├── tables/           # SQLModel table definitions
│   │   └── schemas/          # Pydantic DTOs
│   └── services/             # Business logic
│       ├── profile_service.py
│       ├── vocabulary_card_service.py
│       ├── user_card_progress_service.py
│       ├── deck_service.py
│       ├── study_session_service.py
│       ├── stats_service.py           # Statistics aggregation
│       ├── wrong_answer_service.py
│       ├── word_tutor_service.py      # AI tutor orchestration
│       ├── word_tutor_graph.py        # LangGraph workflows
│       ├── gemini_image_service.py    # Gemini image generation
│       ├── supabase_storage_service.py # Supabase Storage uploads
│       ├── tts_service.py             # Text-to-Speech (Google TTS)
│       └── pronunciation_service.py   # Pronunciation audio handling
├── alembic/                  # Database migrations
└── scripts/                  # Utility scripts
    ├── seed_data.py          # Database seeding
    ├── collect_data.py       # Vocabulary collection
    ├── collect_phrases.py    # Phrases/idioms collection
    ├── collect_toefl_data.py # TOEFL word list collection
    ├── map_frequency.py      # Frequency rank mapping
    ├── generate_cloze.py     # Cloze sentence generation
    ├── generate_card_images.py # Card image generation (Gemini)
    ├── enrich_with_gpt.py    # GPT enrichment
    ├── update_cards_via_api.py # Bulk update via API
    ├── seed_via_rest.py      # Seed via REST API
    └── verify_data.py        # Data validation
```

### Database Models

Models in `src/app/models/tables/`:

| Model | Description |
|-------|-------------|
| `Profile` | User profile (UUID from Supabase), streaks, settings, daily_goal |
| `VocabularyCard` | English word with korean_meaning, IPA, examples, cloze_sentences, frequency_rank, cefr_level, image_url, related_words |
| `UserCardProgress` | FSRS state (stability, difficulty, lapses, card_state, next_review_date) |
| `Deck` | Word collections (public/private, official flag) |
| `StudySession` | Learning session (card_ids, correct/wrong counts, status) |
| `WordTutorThread` | AI tutor conversation thread per (user, session, card) |
| `WordTutorMessage` | Individual messages in tutor chat (role, content, suggested_questions) |
| `WrongAnswer` | Tracks incorrect answers for review (user_answer, correct_answer, quiz_type, reviewed) |
| `Favorite` | User's bookmarked cards |
| `UserSelectedDeck` | User's selected decks for study |

### Enums

```python
# src/app/models/enums.py
CardState: NEW, LEARNING, REVIEW, RELEARNING
SessionStatus: ACTIVE, COMPLETED, ABANDONED
QuizType: WORD_TO_MEANING, MEANING_TO_WORD, CLOZE, LISTENING, IMAGE_TO_WORD
ChatRole: SYSTEM, USER, ASSISTANT
```

### Schemas (`src/app/models/schemas/`)

| Domain | Schemas |
|--------|---------|
| Profile | `ProfileRead`, `ProfileUpdate`, `ProfileConfigRead/Update`, `TodayProgressRead`, `StreakRead` |
| Card | `VocabularyCardCreate/Read/Update`, `UserCardProgressCreate/Read` |
| Deck | `DeckCreate/Read/Update`, `DeckWithProgressRead`, `SelectDecksRequest/Response` |
| Study | `SessionStartRequest/Response`, `CardRequest/Response`, `AnswerRequest/Response`, `SessionCompleteResponse` |
| Stats | `TotalLearnedRead`, `StatsHistoryRead`, `StatsAccuracyRead`, `TodayStatsRead` |
| Tutor | `TutorMessageRequest`, `TutorStartResponse`, `TutorMessageResponse`, `TutorHistoryResponse` |
| WrongAnswer | `WrongAnswerCreate`, `WrongAnswerRead` |

**Pattern for new models**:

```python
# src/app/models/tables/entity.py
class EntityBase(SQLModel):
    name: str

class Entity(EntityBase, TimestampMixin, table=True):
    __tablename__ = "entities"
    id: int = Field(default=None, primary_key=True)

# src/app/models/schemas/entity.py
class EntityCreate(EntityBase): pass
class EntityRead(EntityBase):
    id: int
    created_at: datetime
```

**Critical**: Import new models in both `src/app/models/tables/__init__.py` AND `src/app/models/__init__.py` for Alembic detection.

### API Routes

All routes mounted at `/api/v1` (configurable via `API_V1_PREFIX`):

| Prefix | File | Description |
|--------|------|-------------|
| `/auth` | `auth.py` | Register, login, refresh, logout |
| `/profiles` | `profiles.py` | me, today-progress, streak, config, level |
| `/cards` | `cards.py` | Vocabulary cards CRUD |
| `/decks` | `decks.py` | Deck management, select, selected |
| `/study` | `study.py` | session/start, session/card, session/answer, session/complete |
| `/study/.../tutor` | `tutor.py` | tutor/start, tutor/message, tutor/history |
| `/stats` | `stats.py` | total-learned, accuracy, history, today |

### Authentication

Uses **Supabase Auth** (not local JWT):

- `Profile.id` is the Supabase `auth.users.id` UUID
- Token verification via `get_supabase_client()` in `src/app/core/security.py`
- Protected routes use `CurrentActiveProfile` dependency from `src/app/core/dependencies.py`

```python
from app.core.dependencies import CurrentActiveProfile

@router.get("/protected")
async def protected_route(profile: CurrentActiveProfile):
    return {"user_id": profile.id}
```

### Service Layer

Business logic in `src/app/services/`:

| Service | Responsibility |
|---------|---------------|
| `ProfileService` | Profile CRUD, streak updates, daily goals |
| `VocabularyCardService` | Card CRUD with filtering |
| `UserCardProgressService` | FSRS integration, review scheduling |
| `DeckService` | Deck listing with progress calculation |
| `StudySessionService` | Session flow, card selection, answer processing |
| `StatsService` | Statistics aggregation (accuracy, history, today) |
| `WrongAnswerService` | Wrong answer tracking and review |
| `WordTutorService` | AI tutor orchestration |
| `GeminiImageService` | Image generation via Gemini API |
| `SupabaseStorageService` | File uploads to Supabase Storage |
| `TtsService` | Text-to-Speech audio generation (Google TTS) |
| `PronunciationService` | Pronunciation audio URL handling |

### FSRS Integration

Uses `py-fsrs` library for spaced repetition:

- `UserCardProgress` stores FSRS state (stability, difficulty, scheduled_days, lapses, card_state)
- `CardState` enum: NEW, LEARNING, REVIEW, RELEARNING
- Rating: 1=Again, 2=Hard, 3=Good, 4=Easy
- See `src/app/services/user_card_progress_service.py` for integration

### AI Tutor (LangGraph)

The Word Tutor feature uses LangGraph for AI-powered vocabulary assistance:

**Location**: `src/app/services/word_tutor_service.py`, `word_tutor_graph.py`

**Endpoints** (`/study/session/{session_id}/cards/{card_id}/tutor/...`):
- `POST .../start` - Creates thread, generates 3-7 starter questions via GPT
- `POST .../message` - User sends question, LLM responds with answer + follow-up suggestions
- `GET .../history` - Retrieves conversation history

### Image Generation (Gemini)

Uses Google Gemini for vocabulary card images:

**Location**: `src/app/services/gemini_image_service.py`

```python
from app.services.gemini_image_service import GeminiImageService, GeneratedImage

image: GeneratedImage = GeminiImageService.generate_image("a cute cat")
# image.bytes, image.mime_type
```

### Supabase Storage

File uploads to Supabase Storage buckets:

**Location**: `src/app/services/supabase_storage_service.py`

```python
from app.services.supabase_storage_service import SupabaseStorageService

url = SupabaseStorageService.upload_bytes(
    bucket="card-images",
    path="cards/123.png",
    data=image_bytes,
    mime_type="image/png"
)
```

## Development Patterns

### Adding a New Entity

1. Create table model in `src/app/models/tables/`
2. Create schemas in `src/app/models/schemas/`
3. Export in `src/app/models/tables/__init__.py`
4. Export in `src/app/models/schemas/__init__.py`
5. Export in `src/app/models/__init__.py`
6. Create service in `src/app/services/`
7. Create router in `src/app/api/` and register in `routes.py`
8. Generate migration: `just revision "add entity"`
9. Apply migration: `just migrate`

### Error Handling

Custom exceptions in `src/app/core/exceptions.py`:

- `NotFoundError` (404)
- `ValidationError` (400)
- `AuthenticationError` (401)
- `AuthorizationError` (403)
- `ConflictError` (409)
- `DatabaseError` (500)

```python
from app.core.exceptions import NotFoundError

if not entity:
    raise NotFoundError(f"Entity {id} not found", resource="entity")
```

### Database Queries

```python
from sqlmodel import select

# Single result
result = await session.execute(select(Entity).where(Entity.id == id))
entity = result.scalar_one_or_none()

# Multiple results
result = await session.execute(select(Entity).offset(skip).limit(limit))
entities = list(result.scalars().all())
```

## Environment Configuration

Required in `.env` (see `.env.example`):

```env
# Application
APP_NAME=Loops API
DEBUG=True
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=*

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/loops
DATABASE_ECHO=False

# Supabase Auth
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxx
SUPABASE_SECRET_KEY=sb_secret_xxx  # Required for Storage + admin ops

# Supabase Storage
SUPABASE_STORAGE_BUCKET=card-images

# OpenAI (AI Tutor)
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Gemini (Image Generation)
GEMINI_API_KEY=your-gemini-api-key
GEMINI_IMAGE_MODEL=gemini-3-pro-image-preview
```

## Troubleshooting

**Migration not detecting changes**: Ensure model is imported in `src/app/models/__init__.py`

**Database connection error**: Run `just docker-up` or ensure PostgreSQL is running. For Supabase, use pooler URL (`aws-0-ap-southeast-1.pooler.supabase.com`)

**Column does not exist error**: Migration not applied to DB. Run `just migrate` or apply SQL manually in Supabase SQL Editor

**Multiple migration heads**: Run `uv run alembic merge -m "merge heads" <head1> <head2> ...` to consolidate

**Auth token invalid**: Check `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in `.env`

**AI Tutor not responding**: Verify `OPENAI_API_KEY` is set and valid

**Image generation failing**: Check `GEMINI_API_KEY` in `.env`

**Storage upload failing**: Ensure `SUPABASE_SECRET_KEY` is set (required for write operations)

## Testing

See [docs/TESTING.md](docs/TESTING.md) for detailed testing guide.

### Quick Start

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src/app --cov-report=term-missing

# Run specific test file
uv run pytest tests/unit/api/test_auth_api.py -v
```

### Test Structure

```text
tests/
├── conftest.py              # Shared fixtures
├── factories.py             # Model factories
├── unit/
│   ├── api/                 # API endpoint tests
│   └── services/            # Service layer tests
```

### Coverage Requirements

- **Minimum**: 80%
- **Current**: 85%+

### Key Patterns

```python
# API test with mocking
def test_endpoint(api_client, mocker):
    mocker.patch("app.api.module.Service.method", new_callable=AsyncMock, return_value=mock_response)
    response = api_client.get("/api/v1/endpoint")
    assert response.status_code == 200

# Authentication test
def test_requires_auth(unauthenticated_client):
    response = unauthenticated_client.get("/api/v1/endpoint")
    assert response.status_code == 403
```

## Quick Reference

```bash
# Full development cycle
just setup                  # First time setup
just docker-up              # Start database
just migrate                # Apply migrations
just db-seed                # (Optional) Add sample data
just dev                    # Start server

# After model changes
just revision "description" # Create migration
just migrate                # Apply migration
just current                # Verify

# Testing
uv run pytest               # Run tests
uv run pytest --cov         # With coverage
```
