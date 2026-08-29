# Implementation requirements

## Application architecture requirements

- The application is a Single Page Application (SPA) with a backend API.
- The HTTP API contract in `spec/api.tsp` is the source of truth. The frontend and backend implement against that contract, not against each other. `spec/api.md` stays in sync with the TypeSpec.
- The backend and frontend should be packed together as a single Docker image for deployment.
- Zero deployment required for the project it should be possbile to build it with the single Dockerfile from soruces from scratch
- Don't mix roles in code: owner logic and guest logic should be splitted to different components/modules.
- There is no name-entry screen, no per-tab remembered name, and no `X-User-Name` header. The shell only routes. Guest pages are public. Owner pages use the predefined owner profile with no sign-in.
- The guest types a name only on the booking confirmation form. That name is sent in the create-booking body and is not stored in `sessionStorage`.

## Project layout

```
Dockerfile              multi-stage: build the SPA with Node, run it from Flask
backend/
  pyproject.toml        uv project, dependencies and tool config
  src/                  application package, imported as `src.*`
    app.py              create_app() factory and route registration
    seed.yml            default seed data copied into the image
  tests/
    unit/               calculation logic only
    integration/        Flask test client against a per-test SEED_FILE
    fixtures/           one seed yaml per integration test
frontend/
  package.json
  vite.config.ts        dev server, /api proxy, Tailwind plugin
  src/
    shell/              routing only; no name entry
    owner/              owner module: create event types, upcoming bookings
    guest/              guest module: event-type catalog, slots, book with name
  tests/e2e/            Playwright specs
  tests/fixtures/       one seed yaml per e2e test
spec/
  api.tsp               TypeSpec API contract (source of truth)
  api.md                prose companion to the TypeSpec
```

Owner and guest code never import each other. Anything they share lives in the shell or in a neutral module such as the API client.

## Runtime and configuration

- The backend runs as a single process. In-memory storage cannot be shared across processes, so a multi-worker server would silently split state; this is a hard constraint, not a preference.
- Dev and Docker both use the Flask built-in server with threading enabled. The storage layer guards every mutation with one process-wide `threading.RLock`, which is what makes the booking check-and-reserve atomic.
- Ports: Flask on `5000`, Vite dev server on `5173`, and the Docker image exposes `5000`. Vite proxies `/api` to `http://localhost:5000`. The process listens on `PORT` when that variable is set (default `5000`).
- Environment variables, all optional with the defaults shown:

| Variable | Default | Purpose |
| --- | --- | --- |
| `SEED_FILE` | `src/seed.yml` | Seed data loaded at startup, resolved relative to `backend/` |
| `PORT` | `5000` | Port Flask listens on |
| `LOG_LEVEL` | `INFO` | Minimum level for both log sinks |
| `LOG_FILE` | `logs/app.jsonl` | JSON Lines log file; tests point this at their own run |
| `STATIC_DIR` | unset | Built SPA to serve; set only in the Docker image |

- In the packaged build Flask serves the built SPA: `/api/*` is handled by the API and an unknown `/api/*` path returns a JSON `404 not_found`, static assets are served from `STATIC_DIR`, and every other path returns `index.html` so deep links such as `/owner` and `/book/thirty-minute-call` survive a refresh.
- Startup fails loudly on an unreadable or invalid seed file rather than booting with partial data.

## Dev envionment requirements
- It should be possible to run SPA and backend in developer machine without Docker
- In dev the browser talks to the Vite dev server, which proxies `/api` to Flask. Flask serving the built frontend applies to the Docker/production build only. Frontend tests run against the Vite dev server URL.
- Consider all required tools already present on developer machine, like uv, node and so on.
- SPA and backend should be easy to change. 
- Use hot-reload for SPA
- Dev environment is WSL2 Ubuntu 26, or native Ubuntu 26. 

## Backend

### API Framework
- For backend use Python with Flask framework.
- Flask also should serve the frontend static files in the packaged build.
- Make sure `loguru` logging covered the code flow.
- Business rules for slot generation, the 14-day window, occupancy, and guest-name-on-booking live on the backend, not only in the UI.

### Slot generation
- The backend generates available slots. There is no API to publish, edit, or remove availability.
- For a selected event type, generate consecutive slots of `durationMinutes` from `00:00` UTC to the last slot that still ends on that UTC date, for each UTC calendar day from today through today+13.
- Omit any slot whose start has already passed.
- A booking occupies its clock interval for every event type. Creating a booking that overlaps an existing booking is `409 conflict`.

### Storage
- For storage use in-memory storage (e.g., Python dictionaries) to hold event types and bookings. Slots are not stored; they are generated on each request. No persistent database is required.
- Create separate layer for storage.
- On application start it should be possible to populate in-memory storage with some yaml file data.
- In-memory storage is populated on start from `backend/src/seed.yml` by default. The `SEED_FILE` environment variable overrides which yaml file is loaded, and that is the only way tests point the app at their own fixture.
- Seed data declares the predefined owner, event types, and bookings. Slots are not stored in the seed; the backend generates them.
- Seed booking times are declared relative to load time — a day offset plus UTC times of day, for example `day: +1`, `start: "10:00"` — and are expanded to absolute UTC instants when the file is loaded. Absolute timestamps are not used, so a seeded image never boots with bookings outside the rolling 14-day window.
- The Dockerfile copies `seed.yml` into the image so there is data on app start.

### Seed file schema

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
```

- `eventTypes` are the types the owner has created. The default seed includes `15m call` and `30m call`.
- There is no `availability` list and no `users` list. Free slots are computed on each request from the event type duration, the 14-day window, and existing bookings.
- For a selected event type, each UTC day from today through today+13 is filled with consecutive slots of `durationMinutes` starting at `00:00` UTC. A slot must start and end on the same UTC date. Slots whose start has passed are not returned.
- `bookings[].start` must land on a generated slot for `eventTypeId`. A booking occupies that clock interval for every event type.
- `bookings[].guestName` is the name collected at booking time, not a registered user.
- `bookings[].id` is optional and generated when omitted; pinning it keeps test assertions readable.
- Loading validates every expanded booking against the same rules the API enforces, including the 14-day window. Any violation aborts startup with a log line naming the offending entry.
- `day` is a plain YAML integer, so negative offsets are accepted. Past entries are the fixture for testing that expired bookings disappear from responses; they are stored but invisible, and the horizon check does not reject them.

### Logging
- Output data might needed for AI agent to debug and track progress.
- Use logging to track API requests and errors for trace and debugging purposes. 
- Log output should be easy to analyze by agent
- The format is JSON Lines: one flat JSON object per line, written to stdout and to `LOG_FILE`. Flat rather than loguru's default nested envelope, so a single `jq` selector reaches any field and `grep` on a line yields a complete record. Configure loguru with a custom serializer plus `logger.patch`, not `serialize=True`.
- Every record carries `ts` (UTC ISO 8601), `level`, `event`, and `request_id`. `event` is a dotted name from a closed set, which is what makes the log queryable: `request.end`, `event_type.created`, `event_type.deleted`, `booking.created`, `booking.cancelled`, `seed.loaded`, and `error`.
- `request_id` is generated per request and attached with `logger.contextualize`, so every line emitted while handling a request can be correlated without threading a logger through call sites.
- `request.end` is emitted once per request with `method`, `path`, `status`, and `duration_ms`. Domain events add their own fields, such as `event_type_id`, `slot_start`, `booking_id`, and `guest_name`.
- Every error response also emits an `error` record with `error_code` and `message`, so a failing test can be explained from the log alone.
- Log the reason a request failed, not just its status. `409` on a booking should say whether the slot was taken or already past.

Example line, pretty-printed here but written on one line:

```json
{
  "ts": "2026-08-01T09:12:04.517Z",
  "level": "INFO",
  "event": "booking.created",
  "request_id": "3f9a1c",
  "event_type_id": "thirty-minute-call",
  "slot_start": "2026-08-01T10:00:00Z",
  "booking_id": "9f1c7a3e4b8d4f2a9c6e1b0d5a7f3c82",
  "guest_name": "Sam"
}
```

### Testing
- Tests should produce logs, which can be analyzed by the Agent.
- Create integration tests and e2e tests as main usecases.
- Create yaml files to populate in-memory storage for each e2e/intregration test. Each test starts the app with `SEED_FILE` pointing at its own fixture; there is no test-only API for resetting state.
- Create unit tests to cover calculation logic, but not dataflow. Dataflow should be covered by e2e/integration tests.
- Unit tests cover slot generation from event-type duration, the 14-day window, occupancy overlap, and seed expansion of relative days. They import functions directly and never start the app.
- Integration tests use the Flask test client from the app factory, with each test constructing an app whose `SEED_FILE` points at its own fixture. Nothing is shared between tests, so no reset endpoint is needed.
- E2E tests run Playwright against the Vite dev server, which proxies to a Flask process started by Playwright's `webServer` config with that spec's `SEED_FILE`. The suite waits on `GET /api/health` before the first test.
- Each test run sets `LOG_FILE` to a path under `logs/`, named after the test, so a failure can be diagnosed from a single JSON Lines file.
- Fixtures use relative day offsets like the default seed, so tests never go stale and never depend on the wall clock beyond "today".

## Frontend

### Frontend Framework
- For the frontend use Vue 3 with Composition API.
- Make the SPA firendly for running in VS Code/Cursor in-build browser for UI-testing.
- Owner pages and guest pages are two different modules. There is no start-page name form.
- Routing uses `vue-router` with public guest routes and owner admin routes, for example `/` (event-type catalog), `/book/:eventTypeId` (generated slots and confirm with guest name), and `/owner` (create event types and upcoming bookings). No state management library is needed.
- Do not persist a guest name in `sessionStorage` or any other tab-scoped store. The name field exists only on the booking confirmation form and is sent in `POST /api/bookings`.
- The API client is one module that maps error bodies to their error codes (`validation_error`, `not_found`, `conflict`, `slot_occupied`, `slot_outside_window`, `slot_mismatch`, `future_bookings_exist`) so components handle those codes explicitly instead of inspecting status codes. It does not attach an identity header.
- Use granular error codes to show appropriate user messages:
  - `slot_occupied` — refetch slots and tell the guest the slot was just taken
  - `slot_outside_window` — tell the guest the time is no longer available
  - `slot_mismatch` — tell the guest to choose from the available slots
  - `future_bookings_exist` — tell the owner to cancel bookings before deleting the event type
- Use playwright for frontend tests.

### CSS Framework
- For CSS styling use Tailwind CSS framework.
- Tailwind v4 with the `@tailwindcss/vite` plugin and CSS-first configuration: `@import "tailwindcss"` in the entry stylesheet, no `tailwind.config.js` and no PostCSS setup.
