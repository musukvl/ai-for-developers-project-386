import { expect, test } from '@playwright/test'

test('user enters a name and can create a calendar', async ({ page }) => {
  await page.goto('/')
  await page.getByTestId('name-input').fill('Alex')
  await page.getByTestId('enter-name').click()
  await expect(page.getByTestId('create-calendar')).toBeVisible()
  await page.getByTestId('create-calendar').click()
  await expect(page).toHaveURL(/\/cal\/alex$/)
  await expect(page.getByText('Calendar: alex')).toBeVisible()
})

test('missing visitor calendar reports an error', async ({ page }) => {
  await page.goto('/cal/no-calendar')
  await page.getByTestId('name-input').fill('Sam')
  await page.getByTestId('enter-name').click()
  await expect(page.getByText('Calendar not found')).toBeVisible()
})
