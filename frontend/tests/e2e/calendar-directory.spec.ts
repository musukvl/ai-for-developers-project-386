import { expect, test } from "@playwright/test";

test("shows an alphabetical directory and excludes the calendar being viewed", async ({ page }) => {
  await page.goto("/cal/alex");
  await page.getByLabel("Your name").fill("Alex");
  await page.getByRole("button", { name: "Continue" }).click();

  await expect(page.getByRole("heading", { name: "alex's calendar" })).toBeVisible();

  const directory = page.getByRole("region", { name: "Other calendars" });
  await expect(directory.getByRole("link")).toHaveText(["blake", "zoe"]);
  await expect(directory.getByRole("link", { name: "alex" })).toHaveCount(0);

  await directory.getByRole("link", { name: "blake" }).click();

  await expect(page).toHaveURL(/\/cal\/blake$/);
  await expect(page.getByText("Book a 30-minute meeting with blake.")).toBeVisible();
  await expect(directory.getByRole("link")).toHaveText(["alex", "zoe"]);
  await expect(directory.getByRole("link", { name: "blake" })).toHaveCount(0);
});
