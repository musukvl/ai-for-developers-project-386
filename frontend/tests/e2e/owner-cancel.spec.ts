import { expect, test } from "@playwright/test";

import { startApp, type AppHandle } from "./harness";

let app: AppHandle;

test.beforeAll(async () => {
  app = await startApp("owner-cancel.yml", "owner-cancel");
});

test.afterAll(async () => {
  await app.stop();
});

test("owner cancels a booking and the slot can be booked again", async ({ page }) => {
  await page.goto(`${app.url}/owner`);
  await expect(page.getByRole("heading", { name: "Booked meetings" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Meetings on this day" })).toBeVisible();
  await page.getByRole("button", { name: new RegExp(`${utcTomorrowKey()}, 1 booked meeting`) }).click();
  await expect(page.getByRole("button", { name: /Cancel meeting with Sam/ })).toHaveCount(2);
  await page.getByRole("button", { name: /Cancel meeting with Sam/ }).first().click();
  await expect(page.getByText("No upcoming meetings.")).toBeVisible();

  await page.goto(app.url);
  await page.getByRole("link", { name: /30m call/ }).click();
  await page.getByRole("button", { name: new RegExp(utcTomorrowKey()) }).click();
  await expect(page.getByRole("button", { name: /Book 10:30/ })).toBeVisible();
});

function utcTomorrowKey(): string {
  const now = new Date();
  const tomorrow = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + 1));
  const year = tomorrow.getUTCFullYear();
  const month = String(tomorrow.getUTCMonth() + 1).padStart(2, "0");
  const day = String(tomorrow.getUTCDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}
