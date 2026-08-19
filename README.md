### Hexlet tests and linter status:
[![Actions Status](https://github.com/musukvl/ai-for-developers-project-386/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/musukvl/ai-for-developers-project-386/actions)

# Calls Calendar

A small scheduling app: an owner publishes 30-minute availability slots on their
calendar, and visitors book a slot with a name and no account. See [spec/](spec/)
for the full requirements, API contract, and UI notes.

Live app: https://ai-for-developers-project-386-wwcr.onrender.com/

- **Backend**: Python + Flask, in-memory storage, seeded from YAML on startup.
- **Frontend**: Vue 3 (Composition API) + TypeScript + Tailwind CSS v4, built with Vite.
- **Tests**: `pytest` (unit + integration) for the backend, Playwright for end-to-end.

## Project layout

```
Dockerfile              multi-stage: builds the SPA with Node, serves it from Flask
backend/                Flask API, domain logic, in-memory storage, seed loader
  src/                  application package (imported as src.*)
  tests/unit/           calculation logic only
  tests/integration/    Flask test client, one seed fixture per test
frontend/               Vue 3 + TS + Tailwind SPA
  src/shell/            name entry, routing, the X-User-Name header
  src/owner/            owner module (create calendar, publish slots, cancel bookings)
  src/visitor/          visitor module (book/cancel a slot)
  tests/e2e/            Playwright specs, one seed fixture per spec
spec/                   requirements, API contract, and UI notes
```

## Prerequisites

- [uv](https://docs.astral.sh/uv/) (Python package/dependency manager)
- Node.js 22+ and npm
- Docker (only needed for the containerized build)

## Running in development (no Docker)

The backend and frontend run as two separate processes; Vite proxies `/api`
requests to Flask.

**Backend** (from `backend/`), listening on `:5000`:

```bash
cd backend
uv sync
uv run python -m src.app
```

**Frontend** (from `frontend/`), listening on `:5173` with hot module reload:

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The app starts seeded from `backend/src/seed.yml`.

### Backend configuration

All environment variables are optional:

| Variable | Default | Purpose |
| --- | --- | --- |
| `SEED_FILE` | `src/seed.yml` | Seed data loaded at startup, resolved relative to `backend/` |
| `PORT` | `5000` | Port Flask listens on |
| `LOG_LEVEL` | `INFO` | Minimum level for both log sinks |
| `LOG_FILE` | `logs/app.jsonl` | JSON Lines log file |
| `STATIC_DIR` | unset | Built SPA to serve; set only in the Docker image |

## Tests

**Backend** unit + integration tests (from `backend/`):

```bash
cd backend
uv run pytest
```

**Frontend** end-to-end tests with Playwright (from `frontend/`). Each spec
starts its own Flask + Vite dev server pair against a dedicated seed fixture:

```bash
cd frontend
npx playwright install --with-deps chromium   # first run only
npm run test:e2e
```

## Docker

The single [Dockerfile](Dockerfile) builds the SPA with Node, then packages it
together with the Flask backend into one image that serves both the API and
the static frontend on port 5000 — no separate deployment steps.

Build and run from the repository root:

```bash
docker build -t calls-calendar .
docker run --rm -p 5000:5000 calls-calendar
```

Then open http://localhost:5000. Override any of the backend environment
variables above with `-e`, e.g. `-e LOG_LEVEL=DEBUG`.
