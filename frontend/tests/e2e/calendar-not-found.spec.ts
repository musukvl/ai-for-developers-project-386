import { expect, test } from "@playwright/test";

test("visiting an unknown calendar shows a not-found page with a link back to start", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByLabel("Your name").fill("taylor");
  await page.getByRole("button", { name: "Continue" }).click();

  await expect(page.getByRole("heading", { name: "Create your calendar" })).toBeVisible();

  await page.goto("/cal/does-not-exist");

  await expect(page.getByRole("heading", { name: "Calendar not found" })).toBeVisible();
  await page.getByRole("link", { name: "Back to start" }).click();

  await expect(page).toHaveURL("/");
  await expect(page.getByRole("heading", { name: "Create your calendar" })).toBeVisible();
});
