# API Normalization Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Replace legacy internal backend flows with a single /v1 API that powers wishlist, device sessions, trails sync, and extension connection workflows.

**Architecture:** Move all backend logic into `apps/api` with public `/v1` routes, authenticated via Auth0 (dashboard) and extension JWT (extension). The account and marketing apps become clients of the API. Trails use a hybrid model with JSON payload + summary columns and tombstones for deletions.

**Tech Stack:** Next.js route handlers, Prisma/Postgres, Auth0 JWT verification (JWKS via `jose`), extension JWT (HMAC), TypeScript.

---

### Task 1: Add API auth configuration + dependencies

**Files:**
- Modify: `apps/api/.env.example`
- Modify: `apps/account/.env.example`
- Modify: `apps/api/package.json`
- Create: `apps/api/src/server/auth/jwks.ts`
- Create: `apps/api/src/server/auth/user-auth.ts`
- Create: `apps/api/src/server/auth/extension-auth.ts`
- Create: `apps/api/src/server/auth/headers.ts`
- Test: `apps/api/src/server/auth/__tests__/user-auth.test.ts`
- Test: `apps/api/src/server/auth/__tests__/extension-auth.test.ts`

**Step 1: Add required env vars**
Add to `apps/api/.env.example`:
- `AUTH0_DOMAIN=`
- `AUTH0_AUDIENCE=`
- `TRAIL_EXTENSION_JWT_SECRET=`

Add to `apps/account/.env.example` (if missing):
- `AUTH0_AUDIENCE=`

**Step 2: Add dependency**
Add `jose` to `apps/api/package.json` dependencies.

**Step 3: Write failing tests**
Create `apps/api/src/server/auth/__tests__/user-auth.test.ts`:
```ts
import { verifyUserToken } from "../user-auth";

test("rejects missing token", async () => {
  await expect(verifyUserToken(null)).resolves.toBeNull();
});
```

Create `apps/api/src/server/auth/__tests__/extension-auth.test.ts`:
```ts
import { createExtensionToken, verifyExtensionToken } from "../extension-auth";

test("creates and verifies token", () => {
  const token = createExtensionToken("user_1", 60).token;
  const payload = verifyExtensionToken(token);
  expect(payload?.sub).toBe("user_1");
});
```

**Step 4: Run tests to see failures**
Run: `pnpm --filter @trail/api test` (expect failure until test runner is added).

**Step 5: Add minimal test runner**
Add `vitest` + config (if none exists) in `apps/api`.

**Step 6: Implement auth helpers**
- `headers.ts`: parse `Authorization: Bearer ...`.
- `jwks.ts`: cache JWKS using `createRemoteJWKSet`.
- `user-auth.ts`: verify Auth0 JWT with `AUTH0_DOMAIN` + `AUTH0_AUDIENCE`.
- `extension-auth.ts`: port logic from `apps/account/src/server/extension-auth.ts`.

**Step 7: Re-run tests**
Run: `pnpm --filter @trail/api test` (expect PASS).

**Step 8: Commit**
Commit with message: `Add API auth helpers`.

---

### Task 2: Update Prisma schema for new models

**Files:**
- Modify: `packages/db/prisma/schema.prisma`
- Create: `packages/db/prisma/migrations/<timestamp>_api_normalization/migration.sql`
- Modify: `packages/db/src/generated/*` (via prisma generate)

**Step 1: Write schema changes**
Add models:
- `WishlistLead`
- `WishlistLeadSource` (or enum array)
- `Device`
- `DeviceSession`
- `AccountSettings`
- `Trail`
Remove legacy model:
- `ExtensionLoginCode`

**Step 2: Run migration**
Run: `pnpm --filter @trail/db prisma migrate dev --name api_normalization`

**Step 3: Generate Prisma client**
Run: `pnpm --filter @trail/db prisma generate`

**Step 4: Commit**
Commit with message: `Add API normalization models`.

---

### Task 3: Core server services (wishlist, devices, trails)

**Files:**
- Create: `apps/api/src/server/wishlist.ts`
- Create: `apps/api/src/server/devices.ts`
- Create: `apps/api/src/server/trails-sync.ts`
- Test: `apps/api/src/server/__tests__/trails-sync.test.ts`

**Step 1: Write failing test for sync merge**
Create `apps/api/src/server/__tests__/trails-sync.test.ts`:
```ts
import { mergeTrailUpdates } from "../trails-sync";

test("rejects stale updates after tombstone", () => {
  const server = { id: "t1", updatedAt: new Date("2026-01-01"), deletedAt: new Date("2026-01-02") };
  const client = { id: "t1", updatedAt: new Date("2026-01-01T12:00:00Z"), deletedAt: null };
  const result = mergeTrailUpdates(server, client);
  expect(result.applied).toBe(false);
});
```

**Step 2: Run tests**
Run: `pnpm --filter @trail/api test` (expect FAIL).

**Step 3: Implement services**
- `wishlist.ts`: upsert by email, merge sources and metadata.
- `devices.ts`: claim device, refresh session TTL, list devices.
- `trails-sync.ts`: merge logic for LWW + tombstones + 30-day retention.

**Step 4: Re-run tests**
Run: `pnpm --filter @trail/api test` (expect PASS).

**Step 5: Commit**
Commit with message: `Add core wishlist/devices/sync services`.

---

### Task 4: Implement /v1 wishlist endpoints

**Files:**
- Create: `apps/api/app/v1/wishlist/route.ts`
- Test: `apps/api/app/v1/__tests__/wishlist.test.ts`

**Step 1: Write failing test**
Create `apps/api/app/v1/__tests__/wishlist.test.ts` with a minimal handler invocation and expected status.

**Step 2: Implement endpoint**
- Validate email + source.
- Call wishlist service.

**Step 3: Run tests**
Run: `pnpm --filter @trail/api test`.

**Step 4: Commit**
Commit with message: `Add wishlist API`.

---

### Task 5: Implement /v1 auth portal flow

**Files:**
- Create: `apps/api/src/server/portal-sessions.ts`
- Create: `apps/api/app/v1/auth/portal/route.ts`
- Create: `apps/api/app/v1/auth/portal/[id]/route.ts`
- Create: `apps/api/app/v1/auth/portal/[id]/approve/route.ts`
- Test: `apps/api/app/v1/__tests__/auth-portal.test.ts`

**Step 1: Write failing tests**
Add tests for `start → pending → approve` flow.

**Step 2: Implement session store**
Use DB table `PortalSession` or `TrailPortalSession` (add if needed) with TTL.

**Step 3: Implement endpoints**
- Start session: generate id, return URL.
- Poll: return status.
- Approve: require user auth, issue extension JWT.

**Step 4: Run tests**
Run: `pnpm --filter @trail/api test`.

**Step 5: Commit**
Commit with message: `Add auth portal flow`.

---

### Task 6: Implement /v1 extension connect flow

**Files:**
- Create: `apps/api/src/server/connect-sessions.ts`
- Create: `apps/api/app/v1/extension/connect/route.ts`
- Create: `apps/api/app/v1/extension/connect/[id]/route.ts`
- Create: `apps/api/app/v1/extension/connect/[id]/approve/route.ts`
- Test: `apps/api/app/v1/__tests__/extension-connect.test.ts`

**Step 1: Write failing tests**
Add tests for `start → pending → approve` flow.

**Step 2: Implement session store**
Use DB table `ExtensionConnectSession` with TTL.

**Step 3: Implement endpoints**
- Start session: user auth.
- Poll: user auth.
- Approve: extension auth.

**Step 4: Run tests**
Run: `pnpm --filter @trail/api test`.

**Step 5: Commit**
Commit with message: `Add extension connect flow`.

---

### Task 7: Implement /v1 devices + settings endpoints

**Files:**
- Create: `apps/api/app/v1/devices/route.ts`
- Create: `apps/api/app/v1/devices/claim/route.ts`
- Create: `apps/api/app/v1/devices/[id]/revoke/route.ts`
- Create: `apps/api/app/v1/account/settings/route.ts`
- Test: `apps/api/app/v1/__tests__/devices.test.ts`

**Step 1: Write failing tests**
Add tests for claim and list.

**Step 2: Implement endpoints**
- Claim uses extension auth + metadata.
- List uses user auth.
- Revoke marks device/session revoked.
- Settings get/patch with enum days.

**Step 3: Run tests**
Run: `pnpm --filter @trail/api test`.

**Step 4: Commit**
Commit with message: `Add devices and settings API`.

---

### Task 8: Implement /v1 trails endpoints + sync

**Files:**
- Create: `apps/api/app/v1/trails/sync/route.ts`
- Create: `apps/api/app/v1/trails/route.ts`
- Create: `apps/api/app/v1/trails/[id]/route.ts`
- Create: `apps/api/app/v1/trails/[id]/restore/route.ts`
- Test: `apps/api/app/v1/__tests__/trails.test.ts`

**Step 1: Write failing tests**
Add tests for list, delete (tombstone), restore, and sync merge.

**Step 2: Implement endpoints**
- Sync uses extension auth + LWW merge.
- List uses user auth, supports includeDeleted.
- Delete sets `deletedAt`.
- Restore clears `deletedAt`.

**Step 3: Run tests**
Run: `pnpm --filter @trail/api test`.

**Step 4: Commit**
Commit with message: `Add trails API`.

---

### Task 9: Move account snapshot + plans to API

**Files:**
- Move: `apps/account/src/server/account-snapshot.ts` → `apps/api/src/server/account-snapshot.ts`
- Create: `apps/api/app/v1/account/route.ts`
- Create: `apps/api/app/v1/plans/route.ts`
- Create: `apps/api/app/v1/subscription/route.ts`
- Create: `apps/api/app/v1/billing/route.ts`
- Create: `apps/api/app/v1/subscription/checkout/route.ts`
- Create: `apps/api/app/v1/billing/portal/route.ts`

**Step 1: Implement snapshot + plans**
Reuse logic but ensure it reads from API db models.

**Step 2: Implement endpoints**
Use extension auth for account/billing endpoints, public for plans.

**Step 3: Commit**
Commit with message: `Add account and billing API`.

---

### Task 10: Update extension client to use API + new flows

**Files:**
- Modify: `extension/src/shared/config/backend.ts`
- Modify: `extension/src/sidepanel/api/account/remote.ts`
- Modify: `extension/src/sidepanel/ui/hooks/useAuthPortalFlow.ts`
- Modify: `extension/src/background/services/tree-storage.ts`
- Create: `extension/src/background/services/trail-sync.ts`
- Modify: `extension/src/background/service-worker.ts`
- Modify: `extension/src/shared/types/account.ts`

**Step 1: Update API base URL**
Point to `https://api.gettrail.net` and keep basePath `/v1`.

**Step 2: Add deviceId storage in chrome.storage.sync**
Implement load/save for `deviceId`.

**Step 3: Implement full sync service**
Push full list + deleted, apply updates, handle tombstones.

**Step 4: Wire sync triggers**
Run at startup, every 5 min, and on manual save.

**Step 5: Update auth portal flow**
Use new `/v1/auth/portal` endpoints and handle `extensionToken`.

**Step 6: Commit**
Commit with message: `Update extension to new API and sync`.

---

### Task 11: Update account app to call API directly

**Files:**
- Modify: `apps/account/src/server/internal-api.ts` (or replace usage)
- Modify: `apps/account/app/(app)/extension/page.tsx`
- Modify: `apps/account/app/v1/auth/portal/route.ts`
- Modify: `apps/account/app/v1/auth/portal/[id]/route.ts`
- Modify: `apps/account/app/api/extension/exchange/route.ts`

**Step 1: Replace legacy extension login code flow**
Switch to `POST /v1/auth/portal/{id}/approve`.

**Step 2: Use API base URL**
Stop calling internal `/api/internal/extension/*` routes.

**Step 3: Commit**
Commit with message: `Update account app for new auth flows`.

---

### Task 12: Update marketing + account waitlist forms

**Files:**
- Modify: `apps/marketing/...` waitlist form handlers
- Modify: `apps/account/...` billing waitlist dialog

**Step 1: Send POST /v1/wishlist**
Attach `source`, `utm_*`, `referrer`, `pagePath`, `userAgent`, `ip`, `country`.

**Step 2: Commit**
Commit with message: `Wire wishlist to API`.

---

### Task 13: Remove legacy extension login code system

**Files:**
- Delete: `apps/api/src/server/extension-login.ts`
- Delete: `apps/api/app/api/internal/extension/*`
- Delete: `apps/account/src/server/extension-login.ts`
- Delete: `packages/db/...ExtensionLoginCode*`

**Step 1: Remove code + routes**
Clean up imports and callers.

**Step 2: Run typecheck**
Run: `pnpm --filter @trail/api typecheck` and `pnpm --filter @trail/account typecheck`.

**Step 3: Commit**
Commit with message: `Remove legacy extension login code`.

---

### Task 14: Final verification

**Files:**
- None

**Step 1: Run checks**
- `pnpm --filter @trail/api typecheck`
- `pnpm --filter @trail/account typecheck`
- `pnpm --filter @trail/marketing typecheck` (if forms changed)

**Step 2: Summarize manual testing**
Document a short manual smoke checklist.

**Step 3: Commit**
Commit with message: `Verify API normalization changes`.

---

## Notes
- Keep extension UI changes minimal unless requested.
- Avoid boolean prop proliferation when adjusting UI (`@vercel-composition-patterns`).
- Remove legacy code paths once new flows are in place.
