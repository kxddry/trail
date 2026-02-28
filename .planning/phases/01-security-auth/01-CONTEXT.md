# Phase 1: Data Integrity & Auth Cleanup - Context

**Gathered:** 2026-02-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove auth bypass entirely, add logging for device ownership reassignment, add error logging to navigation handler. Most requirements in this phase were already satisfied in the codebase — the actual work is 3 focused changes.

</domain>

<decisions>
## Implementation Decisions

### Already Satisfied (no work needed)
- **DATA-01**: `upsertTrail()` already uses `db.$transaction()` — race condition is prevented
- **DATA-02**: Import endpoint already has `update: { userId }` — not a no-op, correctly reassigns
- **DATA-04**: Webhook handler already uses `db.$transaction()` — processing is atomic
- **DATA-05**: Sync engine has 6-step backoff schedule (2s→60s), then retries every 60s indefinitely. This is correct for background sync — server will eventually return. No hard stop needed.

### AUTH-05: Remove ACCOUNT_AUTH_BYPASS entirely
- **Decision:** Delete the bypass mechanism completely, not just guard it
- **Scope:** Code files only. Documentation/planning files (docs/plans/, tasks/) are historical — leave them
- **Files to modify:**
  - `apps/account/src/env.ts` — remove env variable definition (line 78)
  - `apps/account/src/lib/auth.ts` — remove `getAuthBypassState()`, `isAuthBypassed()`, bypass logic in `getAuthSession()` (lines 17, 30-31, 59-64)
  - `apps/account/proxy.ts` — remove raw env check (line 7), make auth unconditional
  - `apps/account/vitest.setup.ts` — remove bypass env setup (line 25)
  - `apps/account/src/lib/__tests__/auth.test.ts` — remove bypass mock (line 17)
  - `apps/account/.env.example` — remove bypass line (line 15)
- **Tests:** Mock `getAuthSession()` directly instead of relying on bypass. Claude's discretion on exact approach.
- **Dev workflow:** Always use real auth locally. No bypass needed.

### DATA-03: Device ownership — reassign with logging
- **Decision:** Keep current reassignment behavior (it handles real scenarios: reinstalls, account switches)
- **Change:** Add logging when a device is reassigned from one user to another
- **Log level:** Claude's discretion (warn or info)
- **File:** `apps/account/src/server/backend/trails-sync.ts` lines 148-164
- **Log content:** Device ID, old user ID, new user ID

### DATA-06: Navigation handler — surface errors
- **Decision:** Add error logging to the silent catch block
- **File:** `extension/src/background/navigation/navigation-handler.ts` lines 50-52
- **Current:** Empty catch with comment "silently ignored"
- **Change:** Add console.error/warn with context
- **Note:** The main catch block (lines 195-197) already logs correctly — only the new tab context block needs fixing

### Claude's Discretion
- Log level for device reassignment (DATA-03)
- Test mocking approach after bypass removal (AUTH-05)
- Error log format for navigation handler (DATA-06)

</decisions>

<specifics>
## Specific Ideas

No specific requirements — straightforward cleanup work. Focus on clean removal and good log messages.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `db.$transaction()` pattern already established in `trails-sync.ts` and `nowpayments/route.ts` — use same pattern for any new transactional code
- `getAuthSession()` in `auth.ts` is the single entry point for auth — simplify it by removing bypass branches

### Established Patterns
- Prisma transaction: `db.$transaction(async (tx) => { ... })` — callback receives transaction client
- Error logging: `console.error("[module-name] description:", error)` (seen in navigation-handler.ts main catch)
- Server-side logging: `console.warn("[module] message", { context })` (seen in trails-sync.ts)

### Integration Points
- `proxy.ts` middleware — after removing bypass, the auth check becomes unconditional (existing auth logic stays)
- `vitest.setup.ts` — after removing bypass env, tests need to mock `getAuthSession()` or use Better Auth test utilities
- `auth.ts` exports (`getAuthSession`, `isAuthBypassed`, `getAuthBypassState`) — downstream consumers of removed exports need updating

</code_context>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-data-integrity-auth-cleanup*
*Context gathered: 2026-02-28*
