# Implementation details

- The application is a Single Page Application (SPA) with a backend API.
- The backend and frontend should be packed together as a single Docker image for deployment.

## Backend

### API Framework
- For backend use Python with Flask framework.
- Flask also should serve the frontend static files.

### Storage
- For storage use in-memory storage (e.g., Python dictionaries) to hold calendar and booking data. No persistent database is required.

### Logging
Logging is a crucial part for debugging with the AI Agent.
Use logging to track API requests and errors for debugging purposes. 

## Frontend

### Frontend Framework
For the frontend use Vue 3 with Composition API.

### CSS Framework
For CSS styling use Tailwind CSS framework.
