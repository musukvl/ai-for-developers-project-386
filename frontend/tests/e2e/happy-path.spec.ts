import { expect, test } from "@playwright/test";

import { futureDateKey } from "./helpers";

/**
 * Mirrors spec/use_cases/happy-path.md: enter a name, create a calendar,
 * publish availability, and have another user book a slot. Two isolated
 * browser contexts stand in for two separate browser tabs, since the
 * entered name is scoped to `sessionStorage` per tab.
 */
test("enter name, create calendar, publish availability, and book a meeting", async ({ browser }) => {
  const dateKey = futureDateKey(2);
  const formattedDate = dateKey.replaceAll("-", ".");

  const ownerContext = await browser.newContext();
  const ownerPage = await ownerContext.newPage();

  await ownerPage.goto("/");
  await ownerPage.getByLabel("Your name").fill("Alex");
  await ownerPage.getByRole("button", { name: "Continue" }).click();

  await expect(ownerPage.getByRole("heading", { name: "Create your calendar" })).toBeVisible();
  await ownerPage.getByRole("button", { name: "Create calendar" }).click();

  await expect(ownerPage).toHaveURL(/\/cal\/alex$/);
  await expect(ownerPage.getByRole("heading", { name: "alex's calendar" })).toBeVisible();

  await ownerPage.getByRole("button", { name: new RegExp(`^${dateKey}`) }).click();
  await ownerPage.getByLabel("Start time").selectOption("10:00");
  await ownerPage.getByLabel("End time").selectOption("11:00");
  await ownerPage.getByRole("button", { name: "Publish availability" }).click();

  await expect(ownerPage.getByText("10:00–10:30")).toBeVisible();
  await expect(ownerPage.getByText("10:30–11:00")).toBeVisible();

  const visitorContext = await browser.newContext();
  const visitorPage = await visitorContext.newPage();

  await visitorPage.goto("/cal/alex");
  await visitorPage.getByLabel("Your name").fill("Sam");
  await visitorPage.getByRole("button", { name: "Continue" }).click();

  await expect(visitorPage.getByText("Book a 30-minute meeting with alex.")).toBeVisible();
  await visitorPage.getByRole("button", { name: new RegExp(`^${dateKey}`) }).click();

  await visitorPage
    .getByRole("listitem")
    .filter({ hasText: "10:00–10:30" })
    .getByRole("button", { name: "Book" })
    .click();

  await expect(visitorPage.getByText(`${formattedDate} 10:00`)).toBeVisible();
  await expect(visitorPage.getByText("10:00–10:30")).toHaveCount(0);
  await expect(visitorPage.getByText("10:30–11:00")).toBeVisible();

  await ownerPage.reload();
  await expect(ownerPage.getByText(`${formattedDate} 10:00`)).toBeVisible();
  await expect(ownerPage.getByText("sam")).toBeVisible();

  await ownerContext.close();
  await visitorContext.close();
});
