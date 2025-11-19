import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests',
  timeout: 120000,
  retries: 0,
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } }
  ],
});