# Security Audit Report: Trail Browser Extension + Web App

**Date:** 2026-02-25
**Scope:** Auth token lifecycle, session persistence, extension security, API security
**Priority Focus:** SESSION PERSISTENCE BUG (users logged out after sleep)

---

## Executive Summary

The Trail extension uses a well-designed OAuth 2.0 + PKCE flow with short-lived access tokens (5 min) and long-lived refresh tokens (30 days). Tokens are stored in `chrome.storage.local`, which correctly survives service worker termination. However, **there is no proactive token refresh mechanism** -- the auth orchestrator only refreshes tokens reactively (when something tries to use auth), and the service worker's `setTimeout`-based scheduling is lost when Chrome terminates the worker during sleep. This is the root cause of the session persistence bug.

---

## 1. SESSION PERSISTENCE BUG -- Root Cause Analysis

### Token Lifecycle Overview

| Token | TTL | Storage | Refresh Mechanism |
|-------|-----|---------|-------------------|
| Access Token (extension JWT) | **5 minutes** | `chrome.storage.local` | On-demand only via `silentSync()` |
| Refresh Token | 30 days | `chrome.storage.local` | Rotation on each use |
| Better Auth JWT (web) | 30 days | httpOnly cookie | N/A for extension |

### The Root Cause: No Alarm-Based Token Refresh

**File:** `/Users/iv/dev/trail/extension/src/background/services/auth-orchestrator.ts`

The `AuthOrchestrator` has **no `chrome.alarms` integration for proactive token refresh**. Compare this to other services:

- `SyncEngine` (line 113): Uses `chrome.alarms.create('trail-sync-v3', { periodInMinutes: 1 })`
- `AccountKeeper` (line 129): Uses `chrome.alarms.create('trail_account_snapshot_refresh', { periodInMinutes: 5 })`
- `AuthOrchestrator`: Uses **only `setTimeout`** (line 230) for `scheduleSilentSync()`

```typescript
// auth-orchestrator.ts, line 222-233
scheduleSilentSync(options: { force?: boolean } = {}): void {
  if (!options.force && this.isCooldownActive()) {
    return;
  }
  if (this.syncTimer) {
    clearTimeout(this.syncTimer);
  }
  this.syncTimer = setTimeout(() => {   // <-- THIS IS THE PROBLEM
    this.syncTimer = null;
    void this.silentSync();
  }, SILENT_SYNC_DEBOUNCE_MS);
}
```

**Why this fails:**

1. Manifest V3 service workers are terminated after ~30 seconds of inactivity
2. When the service worker terminates, **all `setTimeout` timers are destroyed**
3. `chrome.alarms` survive service worker termination -- they wake the worker when fired
4. The auth orchestrator's `syncTimer` is a `setTimeout`, so it is lost on termination
5. The access token expires in 5 minutes
6. When the user returns after sleep (hours later), the access token is expired
7. The sync engine fires (via its alarm), but `isAuthenticated()` in `sync/api.ts` only checks if `accessToken` exists -- it does NOT check expiry
8. The sync engine makes requests with the expired access token, gets 401s
9. The 401 from `SyncApiError('unauthorized')` is classified as **non-retryable** (line 211 of engine.ts), so sync stops
10. The sidepanel's `getAccountSnapshot()` tries to fetch with the expired token, gets a 401, falls back to guest snapshot
11. The user sees the logged-out state

### The Precise Failure Chain

```
User sleeps -> Chrome terminates service worker
  -> setTimeout-based auth sync timer is lost
  -> 5-minute access token expires (no refresh happens)
  -> User returns, opens sidepanel
  -> Service worker restarts, runs init()
  -> authOrchestrator.init() calls scheduleSilentSync() with 1s debounce
  -> But BEFORE that fires, syncEngine alarm fires (every 1 min)
  -> syncEngine checks isAuthenticated() -- true (token string exists)
  -> syncEngine makes API call with EXPIRED token
  -> Server returns 401
  -> SyncApiError('unauthorized', 401) thrown
  -> error.retryable = false (unauthorized is non-retryable)
  -> syncEngine enters 'idle' state, stops trying
  -> Meanwhile, silentSync() runs, detects expired token, attempts refresh
  -> Refresh SHOULD succeed (refresh token is still valid for 30 days)
  -> BUT: there's a race condition and cooldown logic that may interfere
```

### Secondary Contributing Factor: The Cooldown

```typescript
// auth-orchestrator.ts, line 167-177
private isCooldownActive(): boolean {
  return Date.now() < this.loginRequiredCooldownUntil;
}

private markLoginRequiredCooldown(): void {
  this.loginRequiredCooldownUntil = Date.now() + LOGIN_REQUIRED_COOLDOWN_MS;
}
```

The cooldown is stored **in memory** (not in `chrome.storage`), so it resets when the service worker restarts. This is actually fine for the sleep scenario. However, if `executeSilentSync()` runs and the access token check passes (token exists but is expired), and the refresh succeeds, the flow SHOULD work. The key question is whether `silentSync()` actually runs before the UI gives up.

### The Actual Bug: Race Between Sync and Auth

The most likely scenario is:

1. Service worker restarts on user interaction
2. `authOrchestrator.init()` schedules silent sync with 1000ms debounce
3. The sidepanel opens and calls `getAccountSnapshot()` immediately
4. `getAccountSnapshot()` reads the expired access token from storage
5. Makes API call to `/api/v1/account` with expired token
6. Gets 401, falls back to guest snapshot
7. UI shows "logged out" state to user
8. 1000ms later, `silentSync()` runs, successfully refreshes the token
9. But the UI already showed logout state; user clicks "sign in" again

The fix needs to ensure that token refresh happens BEFORE any API calls are made with the potentially-expired token.

### Recommended Fix

**Primary fix:** Add a `chrome.alarms`-based proactive refresh to `AuthOrchestrator`:

```typescript
const AUTH_REFRESH_ALARM = 'trail-auth-refresh' as const;
const AUTH_REFRESH_MINUTES = 4; // Refresh before 5-min expiry

init(): void {
  if (this.initialized) return;
  this.initialized = true;

  // Alarm-based proactive refresh (survives service worker termination)
  chrome.alarms.onAlarm.addListener((alarm) => {
    if (alarm.name === AUTH_REFRESH_ALARM) {
      void this.silentSync();
    }
  });
  chrome.alarms.create(AUTH_REFRESH_ALARM, {
    periodInMinutes: AUTH_REFRESH_MINUTES,
  });

  // ... existing webNavigation listener ...
  this.scheduleSilentSync();
}
```

**Secondary fix:** Make `sync/api.ts` check token expiry, not just existence:

```typescript
// sync/api.ts -- isAuthenticated() should also check expiry
export async function isAuthenticated(): Promise<boolean> {
  const result = await chrome.storage.local.get(AUTH_STORAGE_KEY);
  const raw = result[AUTH_STORAGE_KEY] as StoredAuthSession | undefined;
  if (!raw?.accessToken) return false;
  if (!raw.expiresAt) return false;
  const expiresAt = Date.parse(raw.expiresAt);
  // Consider expired if within 30 seconds of expiry
  return Number.isFinite(expiresAt) && expiresAt > Date.now() + 30_000;
}
```

**Tertiary fix:** Make the sidepanel trigger a token refresh before making API calls:

The sidepanel already does this via `useAuthPortalFlow`'s `trySilentSync()`, but it runs asynchronously. The `getAccountSnapshot()` in `useAccountSnapshotQuery` should be guarded so it waits for the auth check to complete before making network requests.

---

## 2. Token Storage Security

### Current State: Acceptable

Tokens are stored in `chrome.storage.local` under key `trail_auth_session`:

```typescript
// auth-orchestrator.ts, line 46-50
async function loadAuth(): Promise<StoredAuthSession | null> {
  const data = await chrome.storage.local.get(AUTH_STORAGE_KEY);
  const auth = data[AUTH_STORAGE_KEY] as StoredAuthSession | undefined;
  return auth ?? null;
}
```

**Assessment:**
- `chrome.storage.local` is the correct choice for extension tokens -- it persists across service worker restarts and browser restarts
- Only accessible to the extension itself (same-extension origin)
- Not accessible to web pages or other extensions
- The access token, refresh token, AND expiry timestamp are stored together
- **No encryption at rest**, but this is standard practice for browser extensions (the Chrome profile itself is the trust boundary)

### Concern: Duplicate Auth Key Definitions

The `AUTH_STORAGE_KEY = "trail_auth_session"` constant is defined in FOUR separate files:

1. `/Users/iv/dev/trail/extension/src/background/services/auth-orchestrator.ts` (line 7)
2. `/Users/iv/dev/trail/extension/src/background/services/sync/api.ts` (line 104)
3. `/Users/iv/dev/trail/extension/src/background/services/account-keeper.ts` (line 9)
4. `/Users/iv/dev/trail/extension/src/background/messaging/handlers/site-message-handlers.ts` (line 30)
5. `/Users/iv/dev/trail/extension/src/sidepanel/api/account/remote.ts` (line 25)
6. `/Users/iv/dev/trail/extension/src/sidepanel/ui/hooks/useAccount.ts` (line 9)

This should be a single shared constant. If the key ever needs to change, missing one file would cause a silent auth failure.

**Recommendation:** Extract to a shared constants file:
```typescript
// shared/config/storage-keys.ts
export const AUTH_STORAGE_KEY = "trail_auth_session" as const;
```

---

## 3. OAuth Flow Security

### PKCE Implementation: Strong

**File:** `/Users/iv/dev/trail/apps/account/src/server/backend/oauth.ts`

- Uses S256 PKCE (line 195-200): code challenge is SHA-256 of code verifier
- Authorization codes are stored hashed (SHA-256, line 171)
- Codes are one-time use (checked `usedAt`, line 189)
- Codes have 5-minute TTL (line 6)
- Code challenges validated with `timingSafeEqual` via `safeEquals()` (line 69-80)
- Redirect URI validation against allowlist (authorize/route.ts line 34-57)

### Refresh Token Rotation: Properly Implemented

**File:** `/Users/iv/dev/trail/apps/account/src/server/backend/oauth.ts`, lines 283-361

- Each refresh rotates the token (old token marked `usedAt` + `revokedAt`)
- New refresh token issued with fresh 30-day TTL
- Old token is invalidated atomically in a transaction
- Checks device session status before allowing refresh

### Concern: Refresh Token Theft Detection Gap

The refresh flow checks if the old token is `usedAt` or `revokedAt` (line 315), but there's no **replay detection** that would invalidate the entire session chain if a previously-used refresh token is presented again. In standard OAuth 2.0 security guidance (RFC 6819), if a refresh token that was already used is presented again, ALL tokens in that chain should be revoked (indicating theft).

Currently, a stolen-and-replayed refresh token simply returns `invalid_grant`. The legitimate user's new refresh token continues to work, but there's no alert or session revocation.

**Recommendation:** If a used refresh token is presented again, revoke all tokens for that device session as a security precaution.

---

## 4. API Authentication Middleware

### Pattern: Per-Route Auth (No Centralized Middleware)

There is **no Next.js middleware** (`middleware.ts` does not exist). Each API route independently validates auth:

```typescript
// Example from trails/sync/route.ts
const token = getBearerToken(request.headers);
const extension = token ? await verifyExtensionToken(token) : null;
if (!extension?.sub) {
  return jsonError("unauthorized", "Unauthorized.", { status: 401 });
}
```

**Routes audited:**

| Route | Auth Check | Correct? |
|-------|-----------|----------|
| `POST /api/v1/trails/sync` | `verifyExtensionToken` | Yes |
| `PUT/GET/DELETE /api/v1/trails/:id` | `verifyExtensionToken` | Yes |
| `GET /api/v1/account` | `verifyExtensionToken` | Yes |
| `POST /api/v1/oauth/token` | None (public, code exchange) | Correct |
| `POST /api/v1/oauth/revoke` | None | **See concern below** |
| `POST /api/v1/oauth/authorize` | Better Auth session | Yes |
| `GET /api/v1/auth/session-state` | Bearer OR cookie | Yes |
| `GET/POST /auth/logout` | Bearer OR cookie | Yes |
| `GET /api/v1/plans` | None (public) | Correct |
| `POST /api/v1/subscription/checkout` | Bearer (billing user) | Yes |
| `POST /api/v1/billing/webhooks/nowpayments` | HMAC signature | Yes |
| `PATCH /api/v1/trails/:id` | `verifyExtensionToken` | Yes |

### Concern: Token Revoke Endpoint Unauthenticated

**File:** `/Users/iv/dev/trail/apps/account/app/api/v1/oauth/revoke/route.ts`

The `/oauth/revoke` endpoint accepts a refresh token and revokes it without requiring any authentication:

```typescript
export async function POST(request: Request) {
  const body = await request.json().catch(() => null);
  const refreshToken = readRefreshToken(body);
  if (refreshToken) {
    await revokeOAuthRefreshToken(refreshToken);
  }
  return new Response(null, { status: 204 });
}
```

This follows RFC 7009 (OAuth Token Revocation), which states the revocation endpoint SHOULD accept unauthenticated requests for public clients. Since the extension is a public client (no client secret), this is technically correct. However, it means anyone who intercepts a refresh token can revoke it (denial of service against the user).

**Risk:** Low. The refresh token itself is the authentication factor.

---

## 5. CSRF Protections

### Web App CSRF: Partially Protected

The logout route properly separates GET (cookie-clear only) from POST (session revocation):

```typescript
// auth/logout/route.ts, line 99-103
export async function GET(request: Request) {
  // GET only clears local cookies -- server-side session revocation is done
  // exclusively via POST to prevent cross-site (CSRF) logout attacks.
  return buildLogoutResponse(NextResponse.redirect(new URL("/", url.origin)));
}
```

However, the POST logout handler has **no CSRF token validation** -- it relies solely on cookie-based session identification. Since the `trail_auth_session` cookie is `sameSite: 'lax'`, top-level navigations from cross-origin sites WILL include the cookie for GET requests but NOT for POST. This provides adequate protection for the POST handler.

### Extension API CSRF: N/A

Extension API calls use `Authorization: Bearer` headers, which browsers will not attach to cross-origin requests. Extension APIs are inherently CSRF-resistant.

### State-changing API Endpoints: Bearer Token Only

All state-changing endpoints (checkout, subscription changes, tree sync) require Bearer token authentication. This is CSRF-safe because:
1. Bearer tokens are not automatically attached by browsers
2. The extension explicitly sets the `Authorization` header
3. CORS is not configured (default deny for cross-origin requests)

---

## 6. Rate Limiting

### Finding: No Rate Limiting on Any API Endpoint

There is **zero rate limiting** across all API endpoints:

- `/api/v1/oauth/token` -- No rate limit on token exchange/refresh
- `/api/v1/oauth/authorize` -- No rate limit on authorization requests
- `/api/v1/trails/sync` -- No rate limit on sync operations
- `/api/v1/account` -- No rate limit on account reads

**Risk Assessment:**
- **Token endpoint brute force:** LOW -- refresh tokens are 48 random bytes (384 bits of entropy), authorization codes are 32 random bytes (256 bits), both stored as hashes
- **Sync abuse:** MEDIUM -- an attacker with a valid token could make unlimited sync requests, potentially causing database load
- **Authorize endpoint abuse:** MEDIUM -- could be used to generate many authorization codes per session

**Recommendation:** Add rate limiting at minimum to:
1. `POST /api/v1/oauth/token` -- limit failed attempts per IP (e.g., 10/min)
2. `POST /api/v1/trails/sync` -- limit per user (e.g., 60/min)
3. `GET /api/v1/oauth/authorize` -- limit per session (e.g., 10/min)

---

## 7. Input Validation

### Token Endpoint: Adequate

The token endpoint validates all required fields:
```typescript
if (!code || !codeVerifier || !redirectUri) {
  return jsonError("invalid_request", "Missing code exchange fields.", { status: 400 });
}
```

### Sync Endpoint: Adequate

Validates `deviceId` and `clientSyncAt`:
```typescript
if (!deviceId) {
  return jsonError("device_id_required", "Device id is required.", { status: 400 });
}
```

### Concern: No Size Limits on Tree Payloads

**File:** `/Users/iv/dev/trail/apps/account/app/api/v1/trails/[id]/route.ts`

The PUT endpoint for tree upsert accepts a `payload` field that contains the full navigation tree JSON. There appear to be no explicit size limits on this payload beyond what Next.js defaults provide (typically ~1MB for body parsing). A malicious user could potentially upload very large tree payloads.

**Recommendation:** Add explicit body size validation for tree payloads.

---

## 8. Extension Content Script Security

### Origin Validation: Strong

**File:** `/Users/iv/dev/trail/extension/src/content/content-script.ts`

- Content script only injected on Trail origins via manifest `content_scripts.matches`
- Runtime origin check with `isAllowedSiteOrigin()` (line 276)
- Only accepts messages from `window` (same frame, line 273)
- Validates message schema, source field, and type against allowlist

### Anti-Replay: Implemented

- TTL check: messages older than 30 seconds rejected (line 283-284)
- Nonce tracking: UUID-based `requestId` prevents replay (line 287-288)
- Nonce set has a max size of 100 with FIFO eviction

### Message Type Allowlist: Properly Scoped

Only 10 specific message types are accepted (line 78-89).

---

## 9. Auth Bypass in Development

**File:** `/Users/iv/dev/trail/apps/account/src/lib/auth.ts`

```typescript
export function getAuthBypassState(): boolean {
  return env.ACCOUNT_AUTH_BYPASS;
}
```

**Risk:** This is a compile-time check from environment variables. It returns a hardcoded dev user when enabled. This is standard practice for development environments. The risk is if `ACCOUNT_AUTH_BYPASS=1` is accidentally deployed to production.

**Mitigation present:** The env variable is NOT set in the example `.env.example` file (it's blank), and it defaults to `false` when not set. However, there's no build-time assertion that prevents it from being set in production.

**Recommendation:** Add a runtime guard:
```typescript
if (process.env.NODE_ENV === 'production' && env.ACCOUNT_AUTH_BYPASS) {
  throw new Error('ACCOUNT_AUTH_BYPASS must not be enabled in production');
}
```

---

## 10. Additional Security Observations

### 10a. Extension Token Verification Includes DB Lookups

**File:** `/Users/iv/dev/trail/apps/account/src/server/backend/auth/extension-auth.ts`

Every API call triggers:
1. JWT signature verification (fast, in-memory)
2. Database lookup for user (`db.user.findUnique`)
3. Database lookup for device session (`db.extensionDeviceSession.findUnique`)
4. Database write to update `lastSeenAt`

This is a good security practice (can revoke sessions server-side), but the 5-minute access token TTL combined with the alarm-driven sync (every 1 minute) means each user generates ~60+ DB queries per hour just for auth verification, plus the `lastSeenAt` write. Consider:
- Increasing access token TTL to 15-30 minutes (since server-side revocation is checked on each call anyway)
- Moving `lastSeenAt` updates to a less-frequent cadence

### 10b. Refresh Token One-Time Use: Correct

Refresh tokens are single-use with rotation. This is the recommended pattern. If a token is compromised and the attacker uses it first, the legitimate user's next refresh will fail, alerting them to the issue.

### 10c. Device Session Versioning: Well-Designed

The `authSessionVersion` on the User model and `sessionVersion` on ExtensionDeviceSession allow global session invalidation (e.g., password change revokes all extension sessions). The JWT includes `ver` claim that is checked against the DB on each request.

### 10d. Web Logout Propagates to Extension

The `AUTH_REVOKED` site message correctly triggers `authOrchestrator.invalidateFromWebLogout()`, which clears tokens and triggers `syncEngine.resetForAccountSwitch()`. This prevents stale sessions after web logout.

---

## Priority Fix List

| Priority | Issue | Impact | Effort |
|----------|-------|--------|--------|
| **P0** | Add `chrome.alarms`-based token refresh to AuthOrchestrator | Fixes session persistence bug | Small (< 20 LOC) |
| **P0** | Make `isAuthenticated()` in sync/api.ts check token expiry | Prevents 401 cascade after expired token | Small (< 10 LOC) |
| **P1** | Ensure sidepanel waits for auth refresh before fetching snapshot | Prevents flash of logged-out state | Medium |
| **P2** | Consolidate `AUTH_STORAGE_KEY` into shared constant | Prevents maintenance bugs | Small |
| **P2** | Add rate limiting to token and sync endpoints | Prevents abuse | Medium |
| **P3** | Add refresh token replay detection | Detect token theft | Medium |
| **P3** | Add production guard for `ACCOUNT_AUTH_BYPASS` | Prevent accidental bypass in prod | Trivial |
| **P3** | Add body size limits for tree payloads | Prevent DoS via large payloads | Small |
| **P4** | Increase access token TTL to reduce DB load | Performance optimization | Trivial config change |
