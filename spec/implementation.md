# Implementation requirements

## Application architecture requirements

- The application is a Single Page Application (SPA) with a backend API.
- The backend and frontend should be packed together as a single Docker image for deployment.
- Zero deployment required for the project it should be possbile to build it with the single Dockerfile from soruces from scratch
- Don't mix roles in code: owner logic and visitor logic should be splitted to different components/modules.
- The name entry screen belongs to the shared application shell, not to the owner or visitor modules. The shell resolves the entered name and mounts the owner or visitor module for a calendar by comparing the entered name with the calendar name in the URL. There is no backend role or session endpoint.
- Creating a calendar is owner logic and lives in the owner module. On the root page the shell mounts the owner module once a name is entered, and that module renders the create-calendar form or a link to the existing calendar.

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
- In-memory storage is populated on start from `src/seed.yml` by default. The `SEED_FILE` environment variable overrides which yaml file is loaded, and that is the only way tests point the app at their own fixture.
- Seed data declares users, calendars, availability and bookings by normalized user name, so a seeded calendar can be managed by entering its owner's name.
- Seeded users use reserved demo names (`demo-owner`, `demo-visitor`) so the names used in the use cases stay free on a freshly started app.
- Seed times are declared relative to load time — a day offset plus a UTC time of day, for example `day: +1`, `time: "10:00"` — and are expanded to absolute UTC slots when the file is loaded. Absolute timestamps are not used, so a seeded image never boots with data outside the rolling four-week horizon.
- The Dockerfile copies `seed.yml` into the image so there is data on app start.

### Logging
- Output data might needed for AI agent to debug and track progress.
- Use logging to track API requests and errors for trace and debugging purposes. 
- Log output should be easy to analyze by agent

### Testing
- Tests should produce logs, which can be analyzed by the Agent.
- Create integration tests and e2e tests as main usecases.
- Create yaml files to populate in-memory storage for each e2e/intregration test. Each test starts the app with `SEED_FILE` pointing at its own fixture; there is no test-only API for resetting state.
- Create unit tests to cover calculation logic, but not dataflow. Dataflow should be covered by e2e/integration tests.

## Frontend

### Frontend Framework
- For the frontend use Vue 3 with Composition API.
- Remembering the entered name is handled entirely by the Vite frontend using tab-scoped `sessionStorage`. There is no backend flag or environment variable for it.
- Make the SPA firendly for running in VS Code/Cursor in-build browser for UI-testing.
- Owner's calender and Visitor's calendars are two different components.
- When `/cal/{name}` has no calendar yet: if `{name}` is the entered name the owner module shows the create-calendar form, otherwise the visitor module shows a "calendar not found" page with a link back to the start page.
- Use playwright for frontend tests.

### CSS Framework
- For CSS styling use Tailwind CSS framework.
