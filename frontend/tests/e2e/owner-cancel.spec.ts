import { expect, type Page, test } from "@playwright/test";

import { startApp, type AppHandle } from "./harness";

const MONTH_HEADING =
  /^(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}$/;

const MONTH_NAMES = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
] as const;

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

  await showMonthForDate(page, dayOne);
  await expect(page.getByRole("button", { name: new RegExp(`${dayOne}, 1 booked meeting`) })).toContainText(
    "10:30 Sam"
  );

  await showMonthForDate(page, dayTwo);
  await expect(page.getByRole("button", { name: new RegExp(`${dayTwo}, 1 booked meeting`) })).toContainText(
    "14:00 Alex"
  );

  await showMonthForDate(page, dayFour);
  await expect(page.getByRole("button", { name: new RegExp(`${dayFour}, 1 booked meeting`) })).toContainText(
    "09:00 Jordan"
  );

  await showMonthForDate(page, dayOne);
  await page.getByRole("button", { name: new RegExp(`${dayOne}, 1 booked meeting`) }).click();
  await expect(page.getByRole("button", { name: /Cancel meeting with Sam/ })).toHaveCount(2);
  await page.getByRole("button", { name: /Cancel meeting with Sam/ }).first().click();
  await expect(page.getByText("30m call · Sam")).toHaveCount(0);
  await expect(page.getByText("15m call · Alex").first()).toBeVisible();
  await expect(page.getByText("30m call · Jordan").first()).toBeVisible();

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

function utcMonthLabel(dateKey: string): string {
  return new Date(`${dateKey}T00:00:00Z`).toLocaleDateString("en-US", {
    month: "long",
    year: "numeric",
    timeZone: "UTC",
  });
}

function monthHeadingValue(label: string): number {
  const [monthName, year] = label.split(" ");
  return Number(year) * 12 + MONTH_NAMES.indexOf(monthName as (typeof MONTH_NAMES)[number]);
}

async function showMonthForDate(page: Page, dateKey: string): Promise<void> {
  const target = utcMonthLabel(dateKey);
  const heading = page.getByRole("heading", { name: MONTH_HEADING });
  for (let attempt = 0; attempt < 14; attempt += 1) {
    const current = (await heading.textContent())?.trim() ?? "";
    if (current === target) {
      return;
    }
    if (monthHeadingValue(current) < monthHeadingValue(target)) {
      await page.getByRole("button", { name: "Next month" }).click();
    } else {
      await page.getByRole("button", { name: "Previous month" }).click();
    }
  }
  throw new Error(`Could not open calendar month ${target}`);
}
