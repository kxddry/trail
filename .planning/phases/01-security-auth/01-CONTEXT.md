# Phase 1: Security & Auth - Context

**Gathered:** 2026-02-28
**Status:** Dissolved — merged into Phase 2

<domain>
## Phase Boundary

Fix session persistence, remove secrets from git, consolidate auth key, block auth bypass in production.

</domain>

<decisions>
## Findings & Decisions

### AUTH-01: chrome.alarms for token refresh
**Already implemented.** `auth-orchestrator.ts` uses `chrome.alarms` with `AUTH_REFRESH_ALARM` at 2-minute intervals. No action needed.

### AUTH-02: Session expired UI
**Already implemented.** `AuthGate.tsx` checks `sessionExpired` state and shows re-login UI. `useAccount.ts` detects token removal via storage listener. No action needed.

### AUTH-03: Remove production secrets from git
**Already protected.** `.env.prod` and `.env.e2e` are in `.gitignore` and NOT tracked in git history. Verified via `git ls-files --cached` and `git log --all`. No action needed.

### AUTH-04: Consolidate AUTH_STORAGE_KEY
**Already centralized.** Key defined once in `storage-keys.ts`, imported by all 6 consumers. No string literal duplicates. No action needed.

### AUTH-05: Remove ACCOUNT_AUTH_BYPASS
**Action required.** Decision: **remove bypass entirely** (not just guard it).
- Delete env variable definition from `env.ts`
- Delete `getAuthBypassState()` from `auth.ts`
- Remove raw env check from `proxy.ts`
- Remove from all `.env.*` files
- No dev bypass needed — always use real auth locally

</decisions>

<specifics>
## Resolution

4 of 5 requirements were already satisfied. AUTH-05 (single task) merged into Phase 2 (Data Integrity). Phase 1 dissolved and removed from roadmap.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 01-security-auth (dissolved)*
*Context gathered: 2026-02-28*
