# syntax=docker/dockerfile:1

# ---- Stage 1: build the Vue SPA -------------------------------------------
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---- Stage 2: install backend dependencies and run the app ----------------
FROM python:3.12-slim AS backend
WORKDIR /app/backend

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --no-dev --no-install-project

COPY backend/src/ ./src/
RUN uv sync --no-dev

# Built SPA, served by Flask alongside the API.
COPY --from=frontend-build /app/frontend/dist ./static

ENV STATIC_DIR=/app/backend/static
ENV PORT=5000
ENV LOG_LEVEL=INFO

EXPOSE ${PORT}

# Run the already-synced venv's interpreter directly rather than `uv run`,
# which re-syncs (and would fetch the dev dependency group) on every start.
CMD [".venv/bin/python", "-m", "src.app"]
