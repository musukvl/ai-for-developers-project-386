import { expect, test } from "@playwright/test";

import { startApp, type AppHandle } from "./harness";

let app: AppHandle;

test.beforeAll(async () => {
  app = await startApp("calendar-not-found.yml", "calendar-not-found");
});

test.afterAll(async () => {
  await app.stop();
});

test("unknown event type shows a not-found state with a catalog link", async ({ page }) => {
  await page.goto(`${app.url}/book/does-not-exist`);
  await expect(page.getByRole("heading", { name: "Event type not found" })).toBeVisible();
  await page.getByRole("link", { name: "Back to event types" }).click();
  await expect(page.getByRole("heading", { name: "Book a call" })).toBeVisible();
});
