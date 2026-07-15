# Frontend Testing Guide

ApexGuidance AI relies on Vitest and React Testing Library for verifying component rendering and route logic.

## 1. Commands

- Run full test suite: `pnpm run test`
- Interactive watcher mode: `pnpm run test:watch`

## 2. Testing Stack

- **Framework**: Vitest (super fast ESM unit runner)
- **Environment**: jsdom (simulated browser layout space)
- **Helpers**: `@testing-library/react` and `@testing-library/jest-dom` for DOM matchers

## 3. Coverage Strategy

We enforce testing across all key architectural boundaries:
1. **Zustand State Stores**: Assert state manipulation, session initialization, and token clearing routines (e.g. `tests/auth.test.tsx`).
2. **Guards & Providers**: Verify route blocking redirects for protected segments (e.g. `GuestRoute` vs `ProtectedRoute`).
3. **Common UI Elements**: Confirm themes, alerts, buttons, and loading indicator render specs.
