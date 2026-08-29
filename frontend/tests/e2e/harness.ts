/** Start a Flask + Vite pair for one Playwright spec. */

import { spawn, type ChildProcess } from "node:child_process";
import { createServer } from "node:net";
import path from "node:path";
import { fileURLToPath } from "node:url";

const FRONTEND_ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const BACKEND_ROOT = path.resolve(FRONTEND_ROOT, "../backend");
const FIXTURES_DIR = path.resolve(FRONTEND_ROOT, "tests/fixtures");

export interface AppHandle {
  url: string;
  stop: () => Promise<void>;
}

export async function startApp(seedFileName: string, testName: string): Promise<AppHandle> {
  const flaskPort = await freePort();
  const vitePort = await freePort();
  const processes: ChildProcess[] = [];

  const flask = spawn("uv", ["run", "python", "-m", "src.app"], {
    cwd: BACKEND_ROOT,
    env: {
      ...process.env,
      SEED_FILE: path.join(FIXTURES_DIR, seedFileName),
      LOG_FILE: path.join(BACKEND_ROOT, "logs", `${testName}.jsonl`),
      PORT: String(flaskPort),
      STATIC_DIR: "",
    },
    stdio: "pipe",
  });
  processes.push(flask);

  await waitForUrl(`http://127.0.0.1:${flaskPort}/api/health`);

  const vite = spawn("npx", ["vite", "--host", "127.0.0.1", "--port", String(vitePort), "--strictPort"], {
    cwd: FRONTEND_ROOT,
    env: {
      ...process.env,
      API_PROXY: `http://127.0.0.1:${flaskPort}`,
    },
    stdio: "pipe",
  });
  processes.push(vite);

  await waitForUrl(`http://127.0.0.1:${vitePort}`);

  return {
    url: `http://127.0.0.1:${vitePort}`,
    stop: async () => {
      for (const child of processes) {
        if (child.pid) {
          child.kill("SIGTERM");
        }
      }
      await Promise.all(processes.map((child) => waitForExit(child)));
    },
  };
}

function waitForExit(child: ChildProcess): Promise<void> {
  return new Promise((resolve) => {
    if (child.exitCode !== null) {
      resolve();
      return;
    }
    child.once("exit", () => resolve());
    setTimeout(() => {
      child.kill("SIGKILL");
      resolve();
    }, 3000);
  });
}

async function waitForUrl(url: string, timeoutMs = 20_000): Promise<void> {
  const deadline = Date.now() + timeoutMs;
  let lastError: unknown;
  while (Date.now() < deadline) {
    try {
      const response = await fetch(url);
      if (response.ok) {
        return;
      }
    } catch (error) {
      lastError = error;
    }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`Timed out waiting for ${url}: ${String(lastError)}`);
}

function freePort(): Promise<number> {
  return new Promise((resolve, reject) => {
    const server = createServer();
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      if (address && typeof address === "object") {
        const port = address.port;
        server.close(() => resolve(port));
      } else {
        reject(new Error("Could not allocate a TCP port."));
      }
    });
    server.on("error", reject);
  });
}
