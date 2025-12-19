# Loops (Frontend)

Next.js (App Router) web client for Loops.

---

## Requirements

- Node.js (recommend: 20+)
- pnpm

---

## Setup

```bash
cd frontend
pnpm install
```

---

## Run (development)

```bash
cd frontend
pnpm dev
```

Default Next dev server: `http://localhost:3000`

---

## Backend API base URL

The frontend talks to the backend via `getApiBaseUrl()`:

- **Default**: `/_loops_api`
  - In `next.config.mjs`, this path is rewritten to the deployed Cloud Run backend.
- **Local backend**: set `NEXT_PUBLIC_LOOPS_API_BASE_URL` to your local API origin.

Create `frontend/.env.local`:

```env
# If you run the backend with `cd backend && just dev`
NEXT_PUBLIC_LOOPS_API_BASE_URL=http://localhost:8000

# If you run the backend via `cd backend && docker-compose up` (api exposed on 8080)
# NEXT_PUBLIC_LOOPS_API_BASE_URL=http://localhost:8080
```

Notes:

- The frontend uses `/api/v1/*` paths (the backend default `API_V1_PREFIX`).
- When you set the base URL to `http://localhost:8000`, requests become cross-origin from the browser; the backend must allow CORS for your frontend origin.

---

## Scripts

```bash
cd frontend
pnpm dev
pnpm build
pnpm start
pnpm lint
```


