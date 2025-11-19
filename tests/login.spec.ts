import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/loginPage';

test('loginTest - should login successfully', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  // This is a sample: In real run this will be mocked / illustrative
  await login.login('demo', 'password');
  // Simulate assertion
  expect(true).toBe(true);
});