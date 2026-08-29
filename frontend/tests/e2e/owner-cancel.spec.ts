import { expect, test } from "@playwright/test";

import { startApp, type AppHandle } from "./harness";

let app: AppHandle;

test.beforeAll(async () => {
  app = await startApp("owner-cancel.yml", "owner-cancel");
});

test.afterAll(async () => {
  await app.stop();
});

test("owner calendar shows meetings on their days and cancel frees the slot", async ({ page }) => {
  await page.goto(`${app.url}/owner`);
  await expect(page.getByRole("heading", { name: "Booked meetings" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Meetings on this day" })).toBeVisible();

  const dayOne = utcDateKey(1);
  const dayTwo = utcDateKey(2);
  const dayFour = utcDateKey(4);

  const samTile = page.getByRole("button", { name: new RegExp(`${dayOne}, 1 booked meeting`) });
  await expect(samTile).toContainText("10:30 Sam");
  await expect(samTile).toBeVisible();

  await showDateOnCalendar(page, dayOne, dayTwo);
  await expect(page.getByRole("button", { name: new RegExp(`${dayTwo}, 1 booked meeting`) })).toContainText(
    "14:00 Alex"
  );

  await showDateOnCalendar(page, dayOne, dayFour);
  await expect(page.getByRole("button", { name: new RegExp(`${dayFour}, 1 booked meeting`) })).toContainText(
    "09:00 Jordan"
  );

  await showDateOnCalendar(page, dayTwo, dayOne);
  await samTile.click();
  await expect(page.getByRole("button", { name: /Cancel meeting with Sam/ })).toHaveCount(2);
  await page.getByRole("button", { name: /Cancel meeting with Sam/ }).first().click();
  await expect(page.getByText("30m call · Sam")).toHaveCount(0);
  await expect(page.getByText("15m call · Alex")).toBeVisible();
  await expect(page.getByText("30m call · Jordan")).toBeVisible();

  await page.goto(app.url);
  await page.getByRole("link", { name: /30m call/ }).click();
  await page.getByRole("button", { name: new RegExp(dayOne) }).click();
  await expect(page.getByRole("button", { name: /Book 10:30/ })).toBeVisible();
});

function utcDateKey(dayOffset: number): string {
  const now = new Date();
  const date = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate() + dayOffset));
  const year = date.getUTCFullYear();
  const month = String(date.getUTCMonth() + 1).padStart(2, "0");
  const day = String(date.getUTCDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

async function showDateOnCalendar(
  page: { getByRole: (role: "button", options: { name: string | RegExp }) => { click: () => Promise<void> } },
  focusedDateKey: string,
  targetDateKey: string
): Promise<void> {
  if (focusedDateKey.slice(0, 7) === targetDateKey.slice(0, 7)) {
    return;
  }
  await page.getByRole("button", { name: "Next month" }).click();
}
