# Loops

Full-stack English-learning app built around **FSRS spaced repetition**.

- **Original source repositories**:

  - Backend: [ee309-team-goat/loops-api](https://github.com/ee309-team-goat/loops-api)
  - Frontend: [ee309-team-goat/loops-front](https://github.com/ee309-team-goat/loops-front)

- **Backend**: FastAPI + PostgreSQL + Supabase auth/storage (+ optional AI)
- **Frontend**: Next.js (App Router) web client

---

## Repo layout

```text
.
├── backend/   # FastAPI API server + DB + migrations
└── frontend/  # Next.js web app
```

---

## Quickstart (local)

## Deployed backend

- API: `https://loops-api-273611200488.asia-northeast3.run.app`
- Docs: `https://loops-api-273611200488.asia-northeast3.run.app/docs`

### 1) Backend

```bash
cd backend
just setup
just migrate
just dev
```

- **Postgres note**: you don’t have to run local Postgres. If you already have a Supabase Postgres instance, set `DATABASE_URL` in `backend/.env` to your Supabase connection string and you can skip `just docker-up`.

- Dev server docs: [Swagger UI](http://localhost:8000/docs)

If you prefer to run the API via Docker Compose (exposed on 8080):

```bash
cd backend
docker-compose up --build
```

### 2) Frontend

```bash
cd frontend
pnpm install
```

Point the frontend at your local backend by creating `frontend/.env.local`:

```env
NEXT_PUBLIC_LOOPS_API_BASE_URL=http://localhost:8000
```

Then start the app:

```bash
cd frontend
pnpm dev
```

App: `http://localhost:3000`

---

## Readmes

- Backend: [`backend/README.md`](./backend/README.md)
- Frontend: [`frontend/README.md`](./frontend/README.md)

For detailed setup/configuration/commands, **refer to the README inside each folder**.
