# Implementation requirements

## Application architecture requirements

- The application is a Single Page Application (SPA) with a backend API.
- The backend and frontend should be packed together as a single Docker image for deployment.
- Zero deployment required for the project it should be possbile to build it with the single Dockerfile from soruces from scratch
- Don't mix roles in code: owner logic and visitor logic should be splitted to different components/modules.
- The name entry screen belongs to the shared application shell, not to the owner or visitor modules. The shell resolves the entered name and mounts the owner or visitor module for a calendar by comparing the entered name with the calendar name in the URL. There is no backend role or session endpoint.
- Creating a calendar is owner logic and lives in the owner module. On the root page the shell mounts the owner module once a name is entered, and that module renders the create-calendar form or a link to the existing calendar.

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
    shell/              name entry, routing, the X-User-Name header
    owner/              owner module, including the create-calendar form
    visitor/            visitor module
  tests/e2e/            Playwright specs
  tests/fixtures/       one seed yaml per e2e test
```

Owner and visitor code never import each other. Anything they share lives in the shell or in a neutral module such as the API client.

## Runtime and configuration

- The backend runs as a single process. In-memory storage cannot be shared across processes, so a multi-worker server would silently split state; this is a hard constraint, not a preference.
- Dev and Docker both use the Flask built-in server with threading enabled. The storage layer guards every mutation with one process-wide `threading.RLock`, which is what makes the booking check-and-reserve atomic.
- Ports: Flask on `5000`, Vite dev server on `5173`, and the Docker image exposes `5000`. Vite proxies `/api` to `http://localhost:5000`.
- Environment variables, all optional with the defaults shown:

| Variable | Default | Purpose |
| --- | --- | --- |
| `SEED_FILE` | `src/seed.yml` | Seed data loaded at startup, resolved relative to `backend/` |
| `PORT` | `5000` | Port Flask listens on |
| `LOG_LEVEL` | `INFO` | Minimum level for both log sinks |
| `LOG_FILE` | `logs/app.jsonl` | JSON Lines log file; tests point this at their own run |
| `STATIC_DIR` | unset | Built SPA to serve; set only in the Docker image |

- In the packaged build Flask serves the built SPA: `/api/*` is handled by the API and an unknown `/api/*` path returns a JSON `404 not_found`, static assets are served from `STATIC_DIR`, and every other path returns `index.html` so deep links such as `/cal/alex` survive a refresh.
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

### Storage
- For storage use in-memory storage (e.g., Python dictionaries) to hold user, calendar and booking data. No persistent database is required.
- Create separate layer for storage.
- On application start it should be possible to populate in-memory storage with some yaml file data.
- In-memory storage is populated on start from `backend/src/seed.yml` by default. The `SEED_FILE` environment variable overrides which yaml file is loaded, and that is the only way tests point the app at their own fixture.
- Seed data declares users, calendars, availability and bookings by normalized user name, so a seeded calendar can be managed by entering its owner's name.
- Seeded users use reserved demo names (`demo-owner`, `demo-visitor`) so the names used in the use cases stay free on a freshly started app.
- Seed times are declared relative to load time — a day offset plus UTC times of day, for example `day: +1`, `start: "10:00"` — and are expanded to absolute UTC slots when the file is loaded. Absolute timestamps are not used, so a seeded image never boots with data outside the rolling four-week horizon.
- The Dockerfile copies `seed.yml` into the image so there is data on app start.

### Seed file schema

```yaml
users:
  - demo-owner
  - demo-visitor

calendars:
  - ownerId: demo-owner
    availability:
      - day: +1
        start: "10:00"
        end: "12:00"
      - day: +2
        start: "14:00"
        end: "15:00"
    bookings:
      - id: seed-booking-1
        day: +1
        start: "10:30"
        visitorName: demo-visitor
```

- `users` is a list of names that must already be normalized. Declaring a user without a calendar is allowed.
- `calendars[].ownerId` names the owner and therefore the calendar. The owner must appear in `users`, and only one calendar per owner is permitted.
- `availability[]` is a range that expands to 30-minute slots exactly as `POST /api/calendars/{ownerId}/availability` does. `day` is a whole-day offset from the UTC date at load time, so `+0` is today and `+1` is tomorrow. `start` and `end` are `HH:MM` on 30-minute boundaries, and `end` must be after `start`.
- `bookings[].start` must name a slot produced by that calendar's availability; a booking that does not land on a published slot is an error rather than an implicitly created slot. The booked slot leaves `availableSlots`.
- `bookings[].visitorName` must appear in `users`. `bookings[].id` is optional and generated when omitted; pinning it keeps test assertions readable.
- Loading validates every expanded slot against the same rules the API enforces, including the four-week horizon and the name format. Any violation aborts startup with a log line naming the offending entry.
- `day` is a plain YAML integer, so negative offsets are accepted. Past entries are the fixture for testing that expired slots and bookings disappear from responses; they are stored but invisible, and the horizon check does not reject them.

### Logging
- Output data might needed for AI agent to debug and track progress.
- Use logging to track API requests and errors for trace and debugging purposes. 
- Log output should be easy to analyze by agent
- The format is JSON Lines: one flat JSON object per line, written to stdout and to `LOG_FILE`. Flat rather than loguru's default nested envelope, so a single `jq` selector reaches any field and `grep` on a line yields a complete record. Configure loguru with a custom serializer plus `logger.patch`, not `serialize=True`.
- Every record carries `ts` (UTC ISO 8601), `level`, `event`, and `request_id`. `event` is a dotted name from a closed set, which is what makes the log queryable: `request.end`, `user.registered`, `calendar.created`, `availability.added`, `slot.removed`, `booking.created`, `booking.cancelled`, `seed.loaded`, and `error`.
- `request_id` is generated per request and attached with `logger.contextualize`, so every line emitted while handling a request can be correlated without threading a logger through call sites.
- `request.end` is emitted once per request with `method`, `path`, `user`, `status`, and `duration_ms`. Domain events add their own fields, such as `owner_id`, `slot_start`, `booking_id`, and `visitor_name`.
- Every error response also emits an `error` record with `error_code` and `message`, so a failing test can be explained from the log alone.
- Log the reason a request failed, not just its status. `409` on a booking should say whether the slot was taken, removed, or already past.

Example line, pretty-printed here but written on one line:

```json
{
  "ts": "2026-08-01T09:12:04.517Z",
  "level": "INFO",
  "event": "booking.created",
  "request_id": "3f9a1c",
  "user": "sam",
  "owner_id": "alex",
  "slot_start": "2026-08-01T10:00:00Z",
  "booking_id": "9f1c7a3e4b8d4f2a9c6e1b0d5a7f3c82"
}
```

### Testing
- Tests should produce logs, which can be analyzed by the Agent.
- Create integration tests and e2e tests as main usecases.
- Create yaml files to populate in-memory storage for each e2e/intregration test. Each test starts the app with `SEED_FILE` pointing at its own fixture; there is no test-only API for resetting state.
- Create unit tests to cover calculation logic, but not dataflow. Dataflow should be covered by e2e/integration tests.
- Unit tests cover slot expansion, boundary and horizon validation, name normalization, and seed expansion of relative days. They import functions directly and never start the app.
- Integration tests use the Flask test client from the app factory, with each test constructing an app whose `SEED_FILE` points at its own fixture. Nothing is shared between tests, so no reset endpoint is needed.
- E2E tests run Playwright against the Vite dev server, which proxies to a Flask process started by Playwright's `webServer` config with that spec's `SEED_FILE`. The suite waits on `GET /api/health` before the first test.
- Each test run sets `LOG_FILE` to a path under `logs/`, named after the test, so a failure can be diagnosed from a single JSON Lines file.
- Fixtures use relative day offsets like the default seed, so tests never go stale and never depend on the wall clock beyond "today".

## Frontend

### Frontend Framework
- For the frontend use Vue 3 with Composition API.
- Remembering the entered name is handled entirely by the Vite frontend using tab-scoped `sessionStorage`. There is no backend flag or environment variable for it.
- Make the SPA firendly for running in VS Code/Cursor in-build browser for UI-testing.
- Owner's calender and Visitor's calendars are two different components.
- When `/cal/{name}` has no calendar yet: if `{name}` is the entered name the owner module shows the create-calendar form, otherwise the visitor module shows a "calendar not found" page with a link back to the start page.
- Use playwright for frontend tests.
- Routing uses `vue-router` with two routes, `/` and `/cal/:ownerId`. No state management library is needed; the entered name and the calendar data fit in composables.
- The API client is one module that attaches the `X-User-Name` header and maps error bodies to the four error codes, so components handle `name_mismatch`, `not_found`, and `conflict` explicitly instead of inspecting status codes.
- Since there are no notifications, a `409 conflict` on booking means the view is stale: refetch the calendar and tell the visitor the slot was just taken.

### CSS Framework
- For CSS styling use Tailwind CSS framework.
- Tailwind v4 with the `@tailwindcss/vite` plugin and CSS-first configuration: `@import "tailwindcss"` in the entry stylesheet, no `tailwind.config.js` and no PostCSS setup.
