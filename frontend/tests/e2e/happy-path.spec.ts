import { expect, test } from "@playwright/test";

import { startApp, type AppHandle } from "./harness";

let app: AppHandle;

test.beforeAll(async () => {
  app = await startApp("happy-path.yml", "happy-path");
});

test.afterAll(async () => {
  await app.stop();
});

test("guest books a generated 30m slot without an account", async ({ page }) => {
  await page.goto(app.url);
  await expect(page.getByRole("heading", { name: "Book a call" })).toBeVisible();
  await page.getByRole("link", { name: /30m call/ }).click();

  await expect(page.getByRole("heading", { name: "30m call" })).toBeVisible();
  await page.getByRole("button", { name: new RegExp(utcTomorrowKey()) }).click();
  await page.getByRole("button", { name: /Book 10:00/ }).click();

  await page.getByLabel("Your name").fill("Sam");
  await page.getByRole("button", { name: "Confirm booking" }).click();

  await expect(page.getByRole("heading", { name: "Booking confirmed" })).toBeVisible();
  await expect(page.getByText(/Sam/)).toBeVisible();
  await expect(page.getByRole("alert")).toHaveCount(0);

  await page.goto(`${app.url}/owner`);
  await expect(page.getByText("30m call · Sam")).toBeVisible();
});

function utcTomorrowKey(): string {
  const now = new Date();
  const tomorrow = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + 1));
  const year = tomorrow.getUTCFullYear();
  const month = String(tomorrow.getUTCMonth() + 1).padStart(2, "0");
  const day = String(tomorrow.getUTCDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
