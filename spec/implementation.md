# Implementation Requirements

Behavioral rules are in `requirements.md`. This document covers architecture, stack, and technical constraints.

## Architecture

- Single Page Application (SPA) with a backend API.
- The HTTP API contract in `spec/api.tsp` is the source of truth. `spec/api.md` stays in sync with the TypeSpec.
- TypeSpec is compiled to OpenAPI. `spec/` contains `package.json`, `tspconfig.yaml`, and a committed `openapi.yaml`. CI fails when the generated OpenAPI drifts.
- Backend and frontend are packed together as a single Docker image.
- Owner logic and guest logic are split into separate modules; they never import each other.
- The shell only routes. Guest pages are public. Owner pages use the predefined owner profile.
- Guest name exists only on the booking confirmation form; it is sent in the request body and not stored in `sessionStorage`.

## Project Layout

```
Dockerfile              multi-stage: build SPA with Node, run from Flask
backend/
  pyproject.toml        uv project
  src/
    app.py              create_app() factory
    seed.yml            default seed data
  tests/
    unit/               calculation logic only
    integration/        Flask test client, per-test SEED_FILE
    fixtures/           one seed yaml per test
frontend/
  package.json
  vite.config.ts        dev server, /api proxy, Tailwind plugin
  src/
    shell/              routing only
    owner/              create event types, upcoming bookings
    guest/              event-type catalog, slots, booking form
  tests/e2e/            Playwright specs
  tests/fixtures/       one seed yaml per spec
spec/
  api.tsp               TypeSpec contract (source of truth)
  api.md                prose companion
  tspconfig.yaml        TypeSpec emit config
  package.json          TypeSpec dependencies
  openapi.yaml          generated OpenAPI (committed; do not edit)
```

## Runtime and Configuration

- Single-process backend; in-memory storage cannot be shared across workers.
- Development: Flask built-in server with threading. Production/Docker: Waitress (single process, threaded) so the container exits on `SIGTERM` within 10 seconds.
- Ports: Flask `5000`, Vite `5173`, Docker exposes `5000`. Vite proxies `/api` to Flask.
- Environment variables (all optional):

| Variable | Default | Purpose |
|----------|---------|---------|
| `SEED_FILE` | `src/seed.yml` | Seed data, resolved relative to `backend/` |
| `PORT` | `5000` | Flask listen port |
| `LOG_LEVEL` | `INFO` | Minimum log level |
| `LOG_FILE` | `logs/app.jsonl` | JSON Lines log file |
| `STATIC_DIR` | unset | Built SPA path; set only in Docker |

- Flask serves the built SPA: `/api/*` goes to the API, unknown `/api/*` returns JSON 404, other paths return `index.html`.
- Startup fails on invalid seed file.
- `MAX_CONTENT_LENGTH` is 64 KiB. Oversized bodies return 413, not a validation error.
- The Node build stage pins `linux/amd64` (Rolldown native binding). Document this in README.

## Backend

### Stack
- Python with Flask.
- `loguru` for structured logging.
- Business rules (slot generation, 14-day window, occupancy) live on the backend.

### Slot Generation
- `WINDOW_DAYS = 14`. Generate slots for today through today+13. Day 14+ is outside the window.
- Overlapping bookings return `409 slot_occupied`, including cross-type conflicts.

### Storage
- In-memory dictionaries for event types and bookings. Slots are generated on each request.
- Seed data loaded from `SEED_FILE` at startup.

### Seed File Schema

```yaml
owner: demo-owner

eventTypes:
  - id: fifteen-minute-call
    title: 15m call
    description: A short call.
    durationMinutes: 15
  - id: thirty-minute-call
    title: 30m call
    description: A standard call.
    durationMinutes: 30

bookings:
  - id: seed-booking-1
    eventTypeId: thirty-minute-call
    day: +1
    start: "10:30"
    guestName: Sam
  - id: seed-booking-2
    eventTypeId: fifteen-minute-call
    day: +1
    start: "14:00"
    guestName: Alex
  - id: seed-booking-3
    eventTypeId: thirty-minute-call
    day: +2
    start: "09:00"
    guestName: Jordan
  - id: seed-booking-4
    eventTypeId: fifteen-minute-call
    day: +4
    start: "16:15"
    guestName: Riley
  - id: seed-booking-5
    eventTypeId: thirty-minute-call
    day: +7
    start: "11:00"
    guestName: Casey
```

- `day` is an integer offset from today; `start` is `HH:MM` UTC.
- Negative `day` offsets are allowed for testing expired-booking visibility.
- `bookings[].id` is optional; generated when omitted.
- Loading validates bookings against the same rules the API enforces. Violations abort startup.

### Logging
- JSON Lines format: one flat object per line to stdout and `LOG_FILE`.
- Fields: `ts`, `level`, `event`, `request_id`.
- Events: `request.end`, `event_type.created`, `event_type.deleted`, `booking.created`, `booking.cancelled`, `seed.loaded`, `error`.
- Log the reason a request failed, not just its status.

Example:
```json
{"ts":"2026-08-01T09:12:04.517Z","level":"INFO","event":"booking.created","request_id":"3f9a1c","event_type_id":"thirty-minute-call","booking_id":"9f1c7a3e","guest_name":"Sam"}
```

## Frontend

### Stack
- Vue 3 with Composition API.
- `vue-router`: `/` (event-type catalog), `/book/:eventTypeId` (slots + booking form), `/owner` (admin).
- No state management library. No `sessionStorage` for guest name.
- API client maps error bodies to codes (`slot_occupied`, `slot_outside_window`, `slot_mismatch`, `future_bookings_exist`).

### CSS
- Tailwind CSS v4 with `@tailwindcss/vite` plugin. No `tailwind.config.js`.

## Testing

- Unit tests: slot generation, 14-day window (including rejection of day 14+), cross-type occupancy, seed expansion.
- Integration tests: Flask test client with per-test `SEED_FILE`. Cover booking by event type, cross-type conflict, horizon rejection of day 15 and day 27, 413 handling, and SIGTERM exit within 10 seconds.
- E2E tests: Playwright against Vite dev server proxying to Flask. Wait on `GET /api/health`. Happy-path asserts `role=alert` is not displayed after successful booking.
- Each test sets `LOG_FILE` to `logs/<test-name>.jsonl`.
- Fixtures use relative day offsets.

## CI

- GitHub Actions on push and pull request: Ruff, pytest, frontend build, Playwright e2e, TypeSpec compile with drift check.
- Do not remove `hexlet-check.yml`.
- Commits follow Conventional Commits. release-please configured on `main`.
