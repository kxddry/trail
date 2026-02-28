---
phase: 01-security-auth
plan: "01"
subsystem: auth
tags: [security, bypass-removal, auth-cleanup]
dependency_graph:
  requires: []
  provides: [clean-auth-no-bypass]
  affects: [apps/account/src/lib/auth.ts, apps/account/proxy.ts, apps/account/src/env.ts]
tech_stack:
  added: []
  patterns: [unconditional-auth-enforcement]
key_files:
  created: []
  modified:
    - apps/account/src/env.ts
    - apps/account/src/lib/auth.ts
    - apps/account/proxy.ts
    - apps/account/src/server/user.ts
    - apps/account/src/server/backend/trpc-context.ts
    - apps/account/vitest.setup.ts
    - apps/account/src/lib/__tests__/auth.test.ts
    - apps/account/.env.example
decisions:
  - "Kept env import in auth.ts because resolveAuthIssuer() still uses env.appBaseUrl — plan note about removing it was incorrect; verified before acting"
metrics:
  duration: "~2 minutes"
  completed: 2026-02-28
  tasks_completed: 2
  files_modified: 8
---

# Phase 1 Plan 1: Remove ACCOUNT_AUTH_BYPASS Summary

**One-liner:** Removed ACCOUNT_AUTH_BYPASS dev bypass entirely — all auth paths now enforce real token verification unconditionally.

## What Was Done

Deleted all branches of the ACCOUNT_AUTH_BYPASS mechanism from the apps/account codebase. Every request through the proxy middleware, every tRPC context creation, and every `ensureUser` call now requires a real JWT token. The three exported symbols (`getAuthBypassState`, `isAuthBypassed`, `devUser`) are gone from `auth.ts`. The env object no longer carries the bypass field. Tests mock `getAuthSession()` via the env stub approach that was already in place — no test changes required beyond removing the stale `ACCOUNT_AUTH_BYPASS: false` field from the env mock.

## Tasks Completed

| Task | Description | Commit | Files Changed |
|------|-------------|--------|---------------|
| 1 | Remove bypass from env, auth module, proxy | 46898dc3 | env.ts, auth.ts, proxy.ts |
| 2 | Remove bypass from consumers, tests, config | 0464343b | user.ts, trpc-context.ts, vitest.setup.ts, auth.test.ts, .env.example |

## Verification Results

- `grep -r "ACCOUNT_AUTH_BYPASS|isAuthBypassed|getAuthBypassState|devUser" apps/account/` — zero matches
- `pnpm vitest run` in apps/account — 75 tests, 22 test files, all passed
- `pnpm tsc --noEmit` in apps/account — no errors

## Deviations from Plan

### Auto-fixed Issues

None — plan executed exactly as written with one noted observation:

**Observation (not a deviation):** The plan stated "Remove the `env` import — it is only used by `getAuthBypassState()`." However, `resolveAuthIssuer()` also uses `env.appBaseUrl`, so the import must remain. The plan noted "Verify no other usage in the file before removing" — verification confirmed keeping the import was correct. No action taken beyond what the plan specified.

## Decisions Made

- Retained `import { env } from "@/src/env"` in auth.ts since `resolveAuthIssuer()` depends on `env.appBaseUrl` — bypass was not the only consumer of the env import.

## Self-Check: PASSED
