import { expect, test } from "@playwright/test";

import { futureDateKey } from "./helpers";

/** Seeded from tests/fixtures/owner-cancel.yml: morgan owns a calendar with
 * one existing booking by riley. */
test("owner cancels a booking and the slot becomes available again", async ({ page }) => {
  const dateKey = futureDateKey(2);

  await page.goto("/");
  await page.getByLabel("Your name").fill("morgan");
  await page.getByRole("button", { name: "Continue" }).click();

  await expect(page.getByRole("heading", { name: "Welcome back, morgan" })).toBeVisible();
  await page.getByRole("link", { name: "Go to my calendar" }).click();

  await expect(page).toHaveURL(/\/cal\/morgan$/);
  await expect(page.getByText("riley")).toBeVisible();

  await page.getByRole("button", { name: "Cancel" }).click();

  await expect(page.getByText("No upcoming bookings yet.")).toBeVisible();
  await expect(page.getByText("riley")).toHaveCount(0);

  await page.getByRole("button", { name: new RegExp(`^${dateKey}`) }).click();
  await expect(page.getByText("13:00–13:30")).toBeVisible();
});
