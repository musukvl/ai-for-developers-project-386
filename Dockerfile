# syntax=docker/dockerfile:1

# Rolldown's native binding is published for linux/amd64. Pin the Node stage
# so the SPA build works on hosts that would otherwise pick a different arch.
FROM --platform=linux/amd64 node:22-slim AS frontend-build
WORKDIR /app/frontend

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# ---- Stage 2: install backend dependencies and run the app ----------------
FROM python:3.14-slim AS backend
WORKDIR /app/backend

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --no-dev --no-install-project

COPY backend/src/ ./src/
RUN uv sync --no-dev

COPY --from=frontend-build /app/frontend/dist ./static

ENV STATIC_DIR=/app/backend/static
ENV PORT=5000
ENV LOG_LEVEL=INFO

EXPOSE ${PORT}

CMD [".venv/bin/python", "-m", "src.app"]
