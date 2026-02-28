---
phase: 01-security-auth
verified: 2026-02-28T15:00:00Z
status: gaps_found
score: 9/10 must-haves verified
re_verification: false
gaps:
  - truth: "Device sync rejects conflicting device ownership across users instead of silently reassigning"
    status: failed
    reason: "DATA-03 requirement text says 'rejects' but the implementation logs and then REASSIGNS (via db.device.update). The requirement wording in REQUIREMENTS.md was retroactively softened to say 'logging added' but the original requirement verb was 'rejects'. The code still performs the reassignment — it just logs it first. This is a requirement text vs implementation mismatch."
    artifacts:
      - path: "apps/account/src/server/backend/trails-sync.ts"
        issue: "Lines 157-168: When device.userId !== userId, code calls console.warn then db.device.update to reassign — it does NOT reject. The requirement says 'rejects conflicting device ownership' which implies the sync should fail or at minimum refuse the reassignment."
    missing:
      - "Clarify DATA-03: either change requirement text to 'logs device ownership reassignment' (matching implementation) or change implementation to reject (throw error / return error response) when device is owned by a different user. The current REQUIREMENTS.md entry has already been retroactively amended to say 'logging added' but the original requirement wording 'rejects' and the implementation verb 'reassigns' still contradict each other."
---

# Phase 01: Security Auth Verification Report

**Phase Goal:** Remove auth bypass, wrap sync in transactions, fix ownership collisions, add retry limits
**Verified:** 2026-02-28T15:00:00Z
**Status:** gaps_found
**Re-verification:** No — initial verification

---

## Goal Achievement

### Observable Truths

| #  | Truth | Status | Evidence |
|----|-------|--------|----------|
| 1  | No code path can bypass authentication — every request goes through real auth | VERIFIED | auth.ts, proxy.ts, user.ts, trpc-context.ts: no bypass branches exist |
| 2  | ACCOUNT_AUTH_BYPASS string appears nowhere in source code files | VERIFIED | grep returns zero matches across all account source, proxy, vitest.setup.ts, .env.example |
| 3  | Existing auth tests pass without relying on bypass mechanism | VERIFIED | auth.test.ts mocks env with only `appBaseUrl`; no ACCOUNT_AUTH_BYPASS field; 75 tests/22 files passed per SUMMARY |
| 4  | The proxy middleware unconditionally enforces auth on protected routes | VERIFIED | proxy.ts lines 6-26: no bypass early-return; goes straight to cookie check then redirect |
| 5  | Device ownership reassignment is logged with device ID, old user ID, and new user ID | VERIFIED | trails-sync.ts lines 158-162: console.warn with deviceId, previousUserId, newUserId |
| 6  | Navigation errors in new-tab context are logged with error details instead of being silently swallowed | VERIFIED | navigation-handler.ts line 51: console.error("[navigation-handler] new tab navigation error:", error) |
| 7  | Trail upsert operations remain wrapped in database transactions (DATA-01) | VERIFIED | trails-sync.ts line 312: db.$transaction wraps upsertTrail callback |
| 8  | Import endpoint correctly updates device userId on ownership collision (DATA-02) | VERIFIED | import/route.ts lines 84-87: db.device.upsert with update: { userId } |
| 9  | Webhook handler uses database transaction for atomic processing (DATA-04) | VERIFIED | app/api/v1/billing/webhooks/nowpayments/route.ts line 178: db.$transaction |
| 10 | DATA-03 requirement fulfilled as written — device sync REJECTS conflicting ownership | FAILED | Code logs and then reassigns (db.device.update) — does NOT reject. Requirement text says "rejects" but implementation reassigns with logging only |

**Score:** 9/10 truths verified

---

### Required Artifacts

#### Plan 01-01 Artifacts (AUTH-05)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `apps/account/src/lib/auth.ts` | Auth session without bypass branches | VERIFIED | Exports getAuthSession, getUserFromToken, getAuthTokenFromCookies, AUTH_COOKIE_NAME, User — no bypass symbols |
| `apps/account/proxy.ts` | Unconditional auth middleware | VERIFIED | 33 lines, goes straight to cookie check, no bypass conditional |
| `apps/account/src/env.ts` | Env config without bypass variable | VERIFIED | env object has 8 fields, none named ACCOUNT_AUTH_BYPASS or similar |
| `apps/account/src/server/user.ts` | ensureUser without bypass shortcircuit | VERIFIED | 41 lines, no auth import, no bypass check — pure DB upsert |
| `apps/account/src/server/backend/trpc-context.ts` | TRPC context without bypass shortcircuit | VERIFIED | getRequestSession goes straight to getBearerToken/getAuthTokenFromCookie then verifyUserToken |

#### Plan 01-02 Artifacts (DATA-03, DATA-06)

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `apps/account/src/server/backend/trails-sync.ts` | Device reassignment logging | VERIFIED | Line 158: console.warn("[trails-sync] device ownership reassigned", { deviceId, previousUserId, newUserId }) |
| `extension/src/background/navigation/navigation-handler.ts` | Navigation error logging in new-tab catch block | VERIFIED | Line 51: console.error("[navigation-handler] new tab navigation error:", error) |

---

### Key Link Verification

#### Plan 01-01 Key Links

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `apps/account/src/lib/auth.ts` | `apps/account/src/env.ts` | env import — bypass field removed from both | VERIFIED | ACCOUNT_AUTH_BYPASS absent from both files; env still imported for appBaseUrl in resolveAuthIssuer() |
| `apps/account/src/lib/__tests__/auth.test.ts` | `apps/account/src/lib/auth.ts` | env mock — must no longer mock bypass field | VERIFIED | vi.mock("@/src/env") returns only { appBaseUrl: "https://auth.example.com" } |
| `apps/account/src/server/backend/trpc-context.ts` | `apps/account/src/lib/auth.ts` | import — bypass functions removed, import statement updated | VERIFIED | trpc-context.ts has no import from "@/src/lib/auth"; uses verifyUserToken from user-auth instead |

#### Plan 01-02 Key Links

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `apps/account/src/server/backend/trails-sync.ts` | database | device.update call — logging added around reassignment | VERIFIED | console.warn fires before db.device.update on line 163 |
| `extension/src/background/navigation/navigation-handler.ts` | console | error logging in catch block around line 50-52 | VERIFIED | Line 51: console.error present in catch block at exact location |

---

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-------------|-------------|--------|----------|
| AUTH-05 | 01-01 | ACCOUNT_AUTH_BYPASS completely removed from codebase | SATISFIED | Zero grep matches in source; bypass symbols absent from auth.ts, env.ts, proxy.ts, user.ts, trpc-context.ts, vitest.setup.ts, .env.example |
| DATA-01 | 01-02 | Trail upsert wrapped in database transaction | SATISFIED | trails-sync.ts:312 — db.$transaction(async (tx) => { ... }) wrapping upsertTrail |
| DATA-02 | 01-02 | Import endpoint updates device userId on ownership collision | SATISFIED | import/route.ts:84-87 — db.device.upsert with update: { userId } |
| DATA-03 | 01-02 | Device sync rejects conflicting device ownership across users instead of silently reassigning | PARTIAL | Logging added (warn before update), but code still REASSIGNS via db.device.update. Requirement verb "rejects" not implemented. REQUIREMENTS.md was retroactively amended with "logging added" caveat, but this changes the requirement's intent without a formal decision. |
| DATA-04 | 01-02 | Webhook handler uses database transaction for atomic processing | SATISFIED | app/api/v1/billing/webhooks/nowpayments/route.ts:178 — db.$transaction |
| DATA-05 | 01-02 | Sync engine has retry limit (bounded backoff) | SATISFIED | extension/src/background/services/sync/engine.ts:38 — BACKOFF_SCHEDULE = [2000, 4000, 8000, 16000, 32000, 60000] |
| DATA-06 | 01-02 | Navigation handler logs errors instead of silently swallowing | SATISFIED | navigation-handler.ts:51 — console.error in new-tab catch block |

---

### Anti-Patterns Found

No stub, placeholder, or TODO anti-patterns found in modified files. All implementations are substantive.

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| — | — | — | — | — |

No anti-patterns detected.

---

### Human Verification Required

None — all automated checks are deterministic for this phase.

---

### Gaps Summary

**One gap found: DATA-03 requirement vs implementation mismatch.**

The original requirement text says "Device sync rejects conflicting device ownership across users instead of silently reassigning." The implementation adds a `console.warn` log but then proceeds to reassign the device via `db.device.update`. The device ownership changes — it is not rejected.

The REQUIREMENTS.md entry was retroactively amended to append "*(logging added 2026-02-28)*" which softens the intent, but the requirement's core verb — "rejects" — describes a different behavior than "logs and reassigns."

This is a semantic gap: either the requirement needs to be formally downgraded to "logs device ownership reassignment" (which matches the code), or the code needs to be changed to actually reject (throw an error or return a conflict response) when it detects ownership collision.

The product decision here matters: device reassignment on reinstall/account switch is described in a code comment as "valid expected behavior." If that is the product intent, the requirement text should be updated to say "logs" not "rejects." If the intent is truly to reject cross-user device ownership, the code must be changed.

**All other requirements (AUTH-05, DATA-01, DATA-02, DATA-04, DATA-05, DATA-06) are fully satisfied.** Commits 46898dc3, 0464343b, and 962e2c5a all confirmed to exist in git history.

---

_Verified: 2026-02-28T15:00:00Z_
_Verifier: Claude (gsd-verifier)_
