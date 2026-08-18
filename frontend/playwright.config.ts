import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests/e2e',
  use: { baseURL: 'http://127.0.0.1:5173' },
  webServer: [
    {
      command: 'cd ../backend && SEED_FILE=src/seed.yml LOG_FILE=logs/e2e.jsonl uv run python -m src.main',
      url: 'http://127.0.0.1:5000/api/health',
      reuseExistingServer: !process.env.CI,
    },
    {
      command: 'npm run dev -- --host 127.0.0.1',
      url: 'http://127.0.0.1:5173',
      reuseExistingServer: !process.env.CI,
    },
  ],
})
