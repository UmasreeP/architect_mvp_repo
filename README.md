# Architect MVP Demo - Playwright Mini Repo

This mini repo is created for demonstrating the **Autonomous Test Architect Agent (Astra)** MVP.

## Contents
- `tests/` - three illustrative Playwright tests:
  - `login.spec.ts` (stable)
  - `checkout.spec.ts` (contains intentional flaky patterns)
  - `profile.spec.ts` (contains an intentional failing assertion)
- `pages/loginPage.ts` - simple page object used in tests
- `playwright.config.ts` - minimal Playwright config
- `.github/workflows/e2e.yml` - example CI stub
- `test-report.json` - sample test report mirroring the intentional test outcomes

## How to use
- You don't need to run Playwright for the feasibility demo.
- Use the included `test-report.json` with your analyze script to show Astra detecting flaky/failing tests.
- If you wish to run tests locally, install dependencies:
```bash
npm install
npx playwright install
npx playwright test
```