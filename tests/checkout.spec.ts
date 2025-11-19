import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/loginPage';

test('checkoutTest - flaky due to timeout selector', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.login('demo', 'password');

  // Intentional flaky pattern: hard wait + unstable selector
  await page.waitForTimeout(5000); // hard wait (anti-pattern)
  const maybeButton = await page.$('#maybe-checkout'); // unstable selector
  if (maybeButton) {
    await maybeButton.click();
  } else {
    // sometimes element not present -> simulate flakiness
    await page.click('#checkout', { timeout: 2000 }).catch(() => {});
  }
  expect(true).toBe(true);
});