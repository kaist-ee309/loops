# Loops API (Backend)

FastAPI backend for an English-learning platform powered by **FSRS** (spaced repetition), with Supabase auth/storage and optional AI features.

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Table of contents

- [What this is](#what-this-is)
- [Tech stack](#tech-stack)
- [Quickstart](#quickstart)
- [Configuration](#configuration)
- [Common commands](#common-commands)
- [Tests & quality](#tests--quality)
- [API docs](#api-docs)
- [Deployment](#deployment)
- [Repository docs](#repository-docs)

---

## What this is

Loops API provides:

- **Spaced repetition (FSRS)**: schedules reviews based on scientifically validated models
- **Decks + vocabulary cards**: curated decks, per-user selection, and progress tracking
- **Study sessions**: card selection, grading (Again/Hard/Good/Easy), and next review computation
- **Stats**: accuracy, streak, history, and daily progress
- **Optional AI**:
  - **Tutor**: OpenAI-powered Q&A / explanations
  - **Image generation**: Gemini-generated card images (and storage via Supabase)

---

## Tech stack

- **Runtime**: Python 3.12+
- **Framework**: FastAPI + Uvicorn
- **DB**: PostgreSQL (async via `asyncpg`), ORM via SQLModel + Alembic migrations
- **Auth & storage**: Supabase
- **Learning algorithm**: `fsrs` (py-fsrs)
- **Dev tooling**: `uv` (dependency manager), `just` (task runner), `ruff` + `mypy` + `pytest`

---

## Quickstart

### Prerequisites

- Install **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- (Recommended) Install **just**: `brew install just`
- (Optional) Install Docker for local Postgres: `docker` + `docker-compose`

### 1) Install deps and create `.env`

```bash
cd backend
just setup
```

### 2) Start PostgreSQL (recommended for local dev)

```bash
cd backend
just docker-up
```

### 3) Run migrations

```bash
cd backend
just migrate
```

### 4) Start the API

#### Local dev server (hot reload)

```bash
cd backend
just dev
```

- Dev server default: [Swagger UI](http://localhost:8000/docs), [ReDoc](http://localhost:8000/redoc), [Health](http://localhost:8000/health)

#### Docker Compose API (optional)

`docker-compose.yaml` also defines an `api` service exposed on **8080**:

- [Swagger UI](http://localhost:8080/docs)
- [Health](http://localhost:8080/health)

---

## Configuration

Edit `backend/.env` (created by `just setup`). These are the high-signal ones:

```env
# App
APP_NAME=Loops API
DEBUG=True
API_V1_PREFIX=/api/v1
ALLOWED_ORIGINS=*

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/loops

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
SUPABASE_SECRET_KEY=sb_secret_...
SUPABASE_STORAGE_BUCKET=card-images

# Optional: AI Tutor (OpenAI)
OPENAI_API_KEY=...
OPENAI_MODEL=gpt-4o-mini

# Optional: Image generation (Gemini)
GEMINI_API_KEY=...
```

---

## Common commands

This repo uses `just` as a command runner:

```bash
cd backend
just --list
```

Most used:

```bash
cd backend
just dev
just migrate
just revision "your message"
just rollback
just docker-up
just docker-down
just docker-migrate
```

---

## Tests & quality

```bash
cd backend

# Tests
uv run pytest

# Lint + format
uv run ruff check src/
uv run ruff format src/

# Typecheck
uv run mypy src/
```

---

## API docs

All API routes are mounted under `API_V1_PREFIX` (default: `/api/v1`).

Interactive docs:

- [Swagger UI (dev server)](http://localhost:8000/docs)
- [Swagger UI (docker-compose api)](http://localhost:8080/docs)

---

## Deployment

See [Deployment guide](./docs/DEPLOYMENT.md).

This backend is designed to run on **Cloud Run** (see `Dockerfile`; it uses `PORT` and defaults to 8080).

---

## Repository docs

Start here: [docs/README.md](./docs/README.md)

- [Commands](./docs/COMMANDS.md)
- [Database](./docs/DATABASE.md)
- [Testing](./docs/TESTING.md)
- [Troubleshooting](./docs/TROUBLESHOOTING.md)
- [Card selection algorithm](./docs/CARD_SELECTION_ALGORITHM.md)
- [AI collaboration notes](./CLAUDE.md)
