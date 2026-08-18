# Calls Calendar

A small public calendar app: owners publish one-off UTC availability and visitors book 30-minute slots.

## Run locally

The backend needs Python 3.14+ and uv. The frontend uses the Linux Node installation from nvm (do not run the Windows npm available through `/mnt/c` in WSL).

```sh
cd backend
uv sync --all-groups
uv run python -m src.main
```

In another terminal:

```sh
cd frontend
source ~/.nvm/nvm.sh && nvm use 24
npm install
npm run dev
```

Open `http://localhost:5173`. Vite proxies `/api` to Flask on port 5000.

## Test

```sh
cd backend && uv run pytest
cd frontend && source ~/.nvm/nvm.sh && nvm use 24 && npx playwright install --with-deps && npm run test:e2e
```

Each test uses a dedicated YAML seed fixture. Logs are JSON Lines under `backend/logs/`.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `SEED_FILE` | `src/seed.yml` | YAML data loaded at startup, relative to `backend/` |
| `PORT` | `5000` | Flask port |
| `LOG_LEVEL` | `INFO` | Minimum log level |
| `LOG_FILE` | `logs/app.jsonl` | JSON Lines log destination |
| `STATIC_DIR` | unset | Built SPA directory, set in the container |

## Container

```sh
docker build -t calls-calendar .
docker run --rm -p 5000:5000 calls-calendar
```

The image builds the Vue SPA with Node and serves it through the single threaded Flask process.