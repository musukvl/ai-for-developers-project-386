import path from "node:path";
import { fileURLToPath } from "node:url";

import { defineConfig, devices } from "@playwright/test";

/**
 * Each e2e spec gets its own isolated (Vite dev server, Flask backend) pair,
 * seeded from its own fixture under tests/fixtures/. Playwright's `webServer`
 * waits on `GET /api/health` before any test in that spec's project runs.
 */

const FRONTEND_ROOT = path.dirname(fileURLToPath(import.meta.url));
const BACKEND_ROOT = path.resolve(FRONTEND_ROOT, "../backend");
const FIXTURES_DIR = path.resolve(FRONTEND_ROOT, "tests/fixtures");
const LOGS_DIR = path.resolve(FRONTEND_ROOT, "../logs/e2e");

interface Scenario {
  name: string;
  seedFile: string;
  backendPort: number;
  frontendPort: number;
}

const scenarios: Scenario[] = [
  { name: "happy-path", seedFile: "happy-path.yml", backendPort: 5301, frontendPort: 5401 },
  { name: "owner-cancel", seedFile: "owner-cancel.yml", backendPort: 5302, frontendPort: 5402 },
  {
    name: "calendar-not-found",
    seedFile: "calendar-not-found.yml",
    backendPort: 5303,
    frontendPort: 5403,
  },
  {
    name: "calendar-directory",
    seedFile: "calendar-directory.yml",
    backendPort: 5304,
    frontendPort: 5404,
  },
];

const reuseExistingServer = !process.env.CI;

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: process.env.CI ? 1 : 0,
  reporter: "list",
  use: {
    trace: "on-first-retry",
  },
  projects: scenarios.map((scenario) => ({
    name: scenario.name,
    testMatch: `${scenario.name}.spec.ts`,
    use: {
      ...devices["Desktop Chrome"],
      baseURL: `http://localhost:${scenario.frontendPort}`,
    },
  })),
  webServer: scenarios.flatMap((scenario) => {
    const backendEnv: Record<string, string> = {
      PORT: String(scenario.backendPort),
      SEED_FILE: path.join(FIXTURES_DIR, scenario.seedFile),
      LOG_FILE: path.join(LOGS_DIR, `${scenario.name}-backend.jsonl`),
    };
    const frontendEnv: Record<string, string> = {
      VITE_BACKEND_PORT: String(scenario.backendPort),
    };
    return [
      {
        command: "uv run python -m src.app",
        cwd: BACKEND_ROOT,
        url: `http://localhost:${scenario.backendPort}/api/health`,
        reuseExistingServer,
        timeout: 60_000,
        env: backendEnv,
      },
      {
        command: `npm run dev -- --port ${scenario.frontendPort} --strictPort`,
        cwd: FRONTEND_ROOT,
        url: `http://localhost:${scenario.frontendPort}`,
        reuseExistingServer,
        timeout: 60_000,
        env: frontendEnv,
      },
    ];
  }),
});
