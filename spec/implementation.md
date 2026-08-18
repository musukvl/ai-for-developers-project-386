# Implementation requirements

## Application architecture requirements

- The application is a Single Page Application (SPA) with a backend API.
- The backend and frontend should be packed together as a single Docker image for deployment.
- Zero deployment required for the project it should be possbile to build it with the single Dockerfile from soruces from scratch
- Don't mix roles in code: owner logic and visitor logic should be splitted to different components/modules.
- The name entry screen belongs to the shared application shell, not to the owner or visitor modules. The shell resolves the entered name and mounts the owner or visitor module for a calendar.

## Dev envionment requirements
- It should be possible to run SPA and backend in developer machine without Docker
- Consider all required tools already present on developer machine, like uv, node and so on.
- SPA and backend should be easy to change. 
- Use hot-reload for SPA
- Dev environment is WSL2 Ubuntu 26, or native Ubuntu 26. 

## Backend

### API Framework
- For backend use Python with Flask framework.
- Flask also should serve the frontend static files.
- Make sure `loguru` logging covered the code flow.

### Storage
- For storage use in-memory storage (e.g., Python dictionaries) to hold user, calendar and booking data. No persistent database is required.
- Create separate layer for storage.
- On application start it should be possible to populate in-memory storage with some yaml file data.
- In-memory storage should be populated on start with sample data from the seed.yml
- Seed data declares users, calendars, availability and bookings by normalized user name, so a seeded calendar can be managed by entering its owner's name.
- Place seed.yml to the Dockerfile so there are some data on app start.

### Logging
- Output data might needed for AI agent to debug and track progress.
- Use logging to track API requests and errors for trace and debugging purposes. 
- Log output should be easy to analyze by agent

### Testing
- Tests should produce logs, which can be analyzed by the Agent.
- Create integration tests and e2e tests as main usecases.
- Create yaml files to populate in-memory storage for each e2e/intregration test.
- Create unit tests to cover calculation logic, but not dataflow. Dataflow should be covered by e2e/integration tests.

## Frontend

### Frontend Framework
- For the frontend use Vue 3 with Composition API.
- Remembering the entered name is handled entirely by the Vite frontend using tab-scoped `sessionStorage`. There is no backend flag or environment variable for it.
- Make the SPA firendly for running in VS Code/Cursor in-build browser for UI-testing.
- Owner's calender and Visitor's calendars are two different components.
- Use playwright for frontend tests.

### CSS Framework
- For CSS styling use Tailwind CSS framework.
