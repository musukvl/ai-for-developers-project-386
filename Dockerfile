FROM node:24-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.14-slim
WORKDIR /app/backend
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --no-dev --no-install-project
COPY backend/ ./
COPY --from=frontend-build /app/frontend/dist /app/frontend-dist
ENV STATIC_DIR=/app/frontend-dist
ENV PORT=5000
EXPOSE 5000
CMD ["/app/backend/.venv/bin/python", "-m", "src.main"]
