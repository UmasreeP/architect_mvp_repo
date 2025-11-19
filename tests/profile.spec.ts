import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/loginPage';

test('profileUpdateTest - failing assertion', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.login('demo', 'password');

  // Simulate API call/assertion failure
  const status = 500; // simulated wrong status
  expect(status).toBe(200); // this will fail in a real run / reflected in test-report
});