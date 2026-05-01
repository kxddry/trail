# Trail — Full Project Review (2026-04-19, v2 verified)

Swarm of 10 specialized review agents (5× Opus 4.7, 5× Sonnet 4.6) scanned the `dev` branch (≈38k lines of net source change vs `main`) across 10 scopes. Every finding was then re-verified by a second pass of 10 parallel verifier agents against the actual file:line. Findings below reflect the verified state: CONFIRMED, REVISED (wording), DOWNGRADED (severity), or REMOVED (dead code / false positive). See `CHANGELOG` section at bottom for what moved from v1.

Severity: **P0** exploitable or ship-blocking, **P1** likely bug or hardening, **P2** quality/defense-in-depth, **P3** nit.

Scope tags: `[sec]` `[sb]` `[ext]` `[arch]` `[ts]` `[ux]` `[perf]` `[obs]` `[test]` `[deps]`.

---

## Executive Summary

**Risk level: HIGH.** Three Supabase RLS P0s let an authenticated user rewrite their own `email_verified`/`email`/`auth_session_version`, and the account-deletion RPC doesn't revoke extension sessions or refresh tokens — so a deleted account keeps syncing for up to 30 days. The extension's sync engine is architecturally broken on MV3: `setInterval` timers in the service worker cannot survive eviction, so periodic pull and supabase-js `autoRefreshToken` effectively don't run in production. Architecture health is uneven: `@trail/ui` is a fully orphaned package, `packages/db` ships un-typed (no `Database` generic), and three parallel bearer-token resolvers coexist in `apps/account`. UX is mostly clean; shadcn compliance is high. Testing has 13 "always-pass" stubs gating the extension's CI E2E coverage. The v1 "PKCE verifier leak" P0 was **removed** — proved to be dead code with no caller or listener.

**Counts (verified):** P0 × 6, P1 × 22, P2 × 31, P3 × 13.

**Top-8 to fix first:**

1. `users` RLS lets clients flip `email_verified`, rewrite `email`, bump `auth_session_version` (P0 `[sb]`).
2. Account-deletion RPC does not revoke `extension_device_sessions` or `oauth_refresh_tokens` (P0 `[sb]`).
3. Client-side fallback wipes all trails via unscoped `UPDATE` if RPC fails (P0 `[sb]`).
4. `setInterval` for sync pull + `autoRefreshToken` in MV3 service worker (P0 `[ext]`).
5. `drainPendingOps` runs before auth loads on SW wake; pending op marked `"skipped"` → terminal → dropped (P0 `[ext]`).
6. `@trail/ui` orphaned + `packages/db` untyped + 3 bearer-token resolvers (P0 `[arch]`+`[ts]`+`[deps]`).
7. `@sentry/browser` default integrations (DOM-bound) bundled into SW with no `integrations: []` override (P1 `[perf]`+`[ext]`).
8. CORS wildcards any `chrome-extension://` origin (P1 `[sec]`).

---

## Dead code — safe to delete now

Consolidated from across the report. Each item was verified: no live caller / no live listener / no import. Landing these deletions first shrinks the blast radius of the P0/P1 work and removes several stale attack-surface claims that agents keep surfacing.

### Flows & modules

- **PKCE extension-relay flow** — `apps/account/app/auth/extension-relay/page.tsx` (entire file) and the `if (source === "extension") { ... }` block in `apps/account/app/auth/callback/route.ts:77-98`. The extension uses `chrome.identity.launchWebAuthFlow` + `supabase.auth.exchangeCodeForSession` directly (`extension/src/shared/auth/auth-orchestrator.ts:671-766`) and never listens for `AUTH_CODE_RELAY`. `extension/tests/transport-contracts.test.ts:90-91` asserts the legacy namespace is removed. No production caller sends `?source=extension`.
- **Account ↔ extension postMessage bridge** — `apps/account/src/lib/trail-extension.ts` (entire file) + its sole caller `apps/account/components/app-sidebar.tsx:13` (`notifyAuthRevoked(...)`). Sends `source:"trail-site"` messages that nothing listens for; always times out silently after ~10s.
- **`packages/ui/src/auth/LoginView.tsx`** — zero runtime consumers. Grep returns no imports anywhere. Staged for reuse and abandoned.
- **`packages/trpc` router artefacts** — `packages/trpc/src/router.ts` (only exports `health`/`me`, never mounted), `packages/trpc/src/trpc.ts`, `packages/trpc/src/types.ts` (if the db-client type re-export is moved to a `./types` entry, see P2.24). The only real consumer of `@trail/trpc` is the JWT helper `extension-token.ts`. Rename package to `@trail/auth-token` and delete the tRPC pieces + `@trpc/server` dep.
- **`apps/account/app/v1/[...path]/route.ts`** — 308-redirect shim from `/v1/*` → `/api/v1/*`. Set a kill date (one forced-update cycle) and delete.
- **`packages/ui/src/marketing/components/ui/*`** — `button.tsx`, `label.tsx`, `skeleton.tsx`, `switch.tsx`, `accordion.tsx` duplicate the base primitives in `packages/ui/src/components/`. Delete or dedupe when `packages/ui` is wired or deleted.
- **Entire `packages/ui/`** (P0.6 option A) — if the decision is not to adopt it, delete the package and trim the lockfile. Zero consumers exist today.

### Dead schema / migrations

- **`wishlist_leads` table** — `supabase/migrations/001_create_schema.sql:156-173` + RLS at `004_rls_policies.sql:123-128`. Zero TypeScript references. Either wire it to a form or drop the table.
- **`auth_session_version` re-hardening** — the column is still useful, but migrations `002` → `005` left behavioural ambiguity (see P2.8). Not dead, but ensure the `public.users.email_verified` backfill runs before the cleanup week.

### Dead dependencies

- `apps/account/package.json` — `react-icons` (zero imports)
- `extension/package.json` `dependencies` — `p-memoize`, `@tanstack/react-virtual` (zero imports)
- `extension/package.json` `devDependencies` — bare `lucide` (only `lucide-react` is used)
- Root `package.json` `dependencies` — `@radix-ui/react-slot`, `class-variance-authority` (shadcn-CLI scaffold leftovers; no root consumer)
- `extension/wxt.config.ts:83` — `"alarms"` permission (zero `chrome.alarms`/`browser.alarms` call sites; keep only if P0.4 is implemented with alarms)

### Dead lines / stubs

- `extension/src/shared/types/ids.ts:10` — commented-out `WindowId` brand type.
- 5 declared analytics events never fired — `observability.ts:48-79` `AnalyticsEvent` union lists `node_created`, `node_deleted`, `node_reparented`, `tree_created`, `tree_switched` with zero `captureEvent(` callsites. Either wire them or remove from the type.
- 13 "always-pass" smoke stubs in `extension/tests/smoke-e2e.test.ts` (P1.21). Replace the 3 highest-risk with real Playwright tests; delete the rest.

### Repo hygiene

- `tasks/reports/` is committed, not gitignored — 6 `.md` files tracked. Add to `.gitignore` + `git rm --cached`.
- `packages/db/src/generated/` was deleted in a prior commit; regenerate via `supabase gen types typescript --linked > packages/db/src/generated/database.ts` as part of P0.6.

---

## P0 — Critical (ship-blockers)

### P0.1 `[sb]` `users` RLS `update_own` has no column allow-list
- `supabase/migrations/004_rls_policies.sql:29-31` — `FOR UPDATE USING (id=auth.uid()) WITH CHECK (id=auth.uid())`. Verified: `email`, `email_verified`, `auth_session_version` are all client-writable. Breaks forced-sign-out (server uses `auth_session_version` as the sole revocation signal at `apps/account/src/server/backend/oauth.ts:491-511`).
- **Fix:**
  ```sql
  REVOKE UPDATE ON users FROM authenticated;
  GRANT UPDATE (name, image, image_url, onboarding_seen_at, updated_at)
    ON users TO authenticated;
  ```

### P0.2 `[sb]` Account-deletion RPC doesn't revoke extension sessions/refresh tokens
- `supabase/migrations/006_account_deletion_rpc.sql:41-63` — soft-deletes `trails`, marks old `device_sessions`; zero references to `extension_device_sessions` (`001:176-188`) or `oauth_refresh_tokens` (`001:208-221`) which the extension auth path actually reads.
- **Fix:** inside the RPC, also `UPDATE extension_device_sessions SET status='REVOKED' …`, revoke refresh tokens, and bump `auth_session_version`.

### P0.3 `[sb]` Client-side deletion fallback issues unscoped `UPDATE trails`
- `extension/src/apps/settings/pages/AccountPage.tsx:383-412` — on RPC error, runs `supabase.from("trails").update({deleted_at:…}).neq("id","00…")`. `.neq` matches every row; only the RLS `update_own` policy scopes it. Any RLS regression becomes a cross-tenant wipe; a transient RPC error wipes all of the user's trails.
- **Fix:** scope by `user_id` explicitly, or remove the fallback and surface the RPC error.

### P0.4 `[ext]` `setInterval` for sync pull + `autoRefreshToken` in MV3 SW
- `extension/src/background/sync/sync-engine.ts:651-653` — `startPullTimer()` uses `setInterval(periodicPull, 60_000)`. Chrome evicts SWs after ~30s idle; the timer dies silently.
- `extension/src/shared/lib/supabase.ts:39` — `autoRefreshToken: true` uses supabase-js's own internal timer with the same SW-eviction problem. The `alarms` permission is already declared in `wxt.config.ts:83` but never used.
- **Fix:** `chrome.alarms.create("trail-sync-pull", { periodInMinutes: 1 })` + `chrome.alarms.onAlarm.addListener` at SW module top level. Disable `autoRefreshToken` for the background surface and drive refresh via `chrome.alarms`.

### P0.5 `[ext]` `drainPendingOps()` on SW wake runs before auth loads; `"skipped"` is terminal
- `extension/src/background/sync/sync-engine.ts:688-690` — `void drainPendingOps().catch(() => {})` fires at SW cold start. `doPushActive`/`doPushStored` return `"skipped"` when not signed-in, and `"skipped"` is listed alongside `"ok"`/`"conflict"` as terminal at line 123 → the op is removed from the queue without ever hitting the network.
- **Fix:** treat `"skipped"` as non-terminal (keep the op queued), or gate `drainPendingOps` on the first `signed-in` transition.

### P0.6 `[arch]`+`[deps]`+`[ts]` Three structural liabilities (one cluster)

- **`@trail/ui` is a dead package.** Verified: grep `from "@trail/ui"` returns zero hits across workspaces. `apps/account/next.config.mjs:12-16` `transpilePackages` doesn't list it. No `apps/*/package.json` or `extension/package.json` declares it as a dep. All three surfaces re-implement the same shadcn primitives in `components/ui/`.
  - **Fix:** delete `packages/ui/` (and run `pnpm install` to trim the lockfile) OR migrate `apps/marketing` to actually consume it.

- **`packages/db` ships untyped.** `packages/db/src/client.ts:22-26` calls `createClient(…)` with no `Database` generic. `packages/db/src/generated/` directory doesn't exist. Every `.select().maybeSingle()` returns `any`. 6+ hand-written row types drift from schema (`DbTrailRow` duplicated in 4 files, plus `TrailRow` in `extension/src/background/sync/sync-engine.ts:423`). `typed<T>()` at `apps/account/src/server/backend/user.ts:23` is an unchecked assertion. The sole surviving `: any` in production code (`apps/account/app/api/v1/billing/webhooks/nowpayments/route.ts:233 (claimResult.data as any[]).length`) is a symptom of this root cause.
  - **Fix:** `supabase gen types typescript --linked > packages/db/src/generated/database.ts`. Export `Database` alongside `SupabaseClient`. Parameterize: `createClient<Database>(…)`. Delete all hand-written row types; derive from `Database["public"]["Tables"][…]["Row"]`. Type the account Supabase clients at `apps/account/src/lib/supabase/{server,client}.ts`.

- **Three parallel bearer-token resolvers** in `apps/account` — `getUserFromToken` (`src/lib/auth.ts:47-70`), `resolveUserId` (`src/server/backend/auth/resolve-user.ts:10-22`), `getUserFromBillingBearerToken` (`src/server/backend/auth/billing-user.ts:8-25`). All three call `verifyExtensionToken` + fetch from `public.users`; three different return shapes. Plus two wrappers for the extension-token verifier itself (`src/server/extension-auth.ts:10` and `src/server/backend/auth/extension-auth.ts:14`).
  - **Fix:** single `getAuthenticatedUser(request, opts): Promise<User|null>`. Delete the wrappers + duplicates.

---

## P1 — High (hardening / likely bugs)

### Security

- **P1.1 `[sec]`** `apps/account/src/server/api/cors.ts:6` — `origin?.startsWith("chrome-extension://")` grants any extension origin. **Fix:** allowlist explicit extension IDs via env var.
- **P1.2 `[sec]`** Rate limiter in-memory Map per-Lambda, keyed on `x-forwarded-for` (`apps/account/src/server/api/rate-limit.ts:4`, used by oauth/authorize, oauth/token, nowpayments webhook). Verified: the file does have a self-cleanup loop — v1's "no cleanup" claim was wrong. Core weakness remains (state not shared across instances; attacker rotates XFF). **Fix:** derive IP from trusted proxy hop; move to Upstash Redis.
- **P1.3 `[sec]`** Website-bridge content script has no `event.origin` check — `@webext-core/messaging/page` installs a bare `window.addEventListener("message", …)` with no origin guard. Any iframe on `gettrail.net`/`app.gettrail.net` can drive `openPanel`, `enterEditorMode`, `cancelEditorMode`. **Fix:** wrap with a pre-listener rejecting `event.origin !== window.location.origin`.
- **P1.4 `[sec]`** `apps/account/app/auth/logout/route.ts:28-31` — Bearer path is cryptographically authenticated (v1 framing was wrong); real issue is the cookie-session path has no CSRF protection. **Fix:** require CSRF token on the cookie path; split routes if needed.
- **P1.5 `[sec]`** Google OAuth fallback parses tokens from URL fragment — `extension/src/shared/auth/auth-orchestrator.ts:750-760` else-branch reads `access_token`/`refresh_token` from `parsedResponse.hash` with no `state` check. **Fix:** delete the fragment fallback; require `code` + PKCE.
- **P1.6 `[sec]`** `apps/account/app/api/v1/trails/import/route.ts:52-63` JSON DoS — `request.json()` no byte cap; `apps/account/src/server/api/schemas.ts:114-126` `treeNodeSchema` `z.lazy().passthrough()` unbounded; `payload: z.unknown()`. **Fix:** cap bytes via `request.text()` + `JSON.parse`; cap `nodeCount` + recursion depth.
- **P1.7 `[sec]`** `apps/account/src/server/api/cors.ts:9` returns `"Access-Control-Allow-Origin": ""` instead of omitting; older runtimes can treat `""` as wildcard. **Fix:** omit the header.

### Supabase

- **P1.8 `[sb]` `wishlist_leads` `insert_anon` accepts arbitrary `user_id/ip/utm_*`** — `supabase/migrations/004_rls_policies.sql:123-128` `WITH CHECK (true)`. **Fix:** SECURITY DEFINER RPC that derives IP/UA server-side, or tighten the policy.
- **P1.9 `[sb]` OAuth token tables allow user-controlled INSERT/UPDATE** — `004_rls_policies.sql:145-170` on `oauth_authorization_codes` + `oauth_refresh_tokens`. A user can pre-plant refresh-token hashes; they can't sign JWTs but they can poison rotation and obtain server-signed access tokens. **Fix:** drop INSERT/UPDATE policies; service role owns writes.
- **P1.10 `[sb]` `extension_device_sessions` `update_own` has no column allow-list** — `004_rls_policies.sql:134-142`. User can flip `status='ACTIVE'` on a revoked session or rewrite `session_version`. **Fix:** drop INSERT/UPDATE policies.
- **P1.11 `[sb]` `auth_session_version` bump is read-then-write, not atomic** — `apps/account/src/server/backend/oauth.ts:491-511`. **Fix:** single-statement `UPDATE users SET auth_session_version = auth_session_version + 1 WHERE id=$1`.

### MV3

- **P1.12 `[ext]` `web_accessible_resources` exposes `assets/*.woff2` to `<all_urls>`** — `extension/wxt.config.ts:86-91`. Installation fingerprinting from any website. **Fix:** narrow `matches` or remove WAR.
- **P1.13 `[ext]` `alarms` permission declared but unused** — `wxt.config.ts:83`; grep for `chrome.alarms`/`browser.alarms` returns zero hits. Will be justified by P0.4 fix; remove otherwise.

### Performance

- **P1.14 `[perf]`+`[ext]` `@sentry/browser` bundled into SW with default integrations** — `extension/src/shared/lib/observability.ts:166-182` inits Sentry for `"background"` surface without `integrations: []` override. Defaults include `BrowserApiErrors`, `Breadcrumbs`, `GlobalHandlers` which access `window`/`document` (undefined in SW) → Sentry silently fails its init, real SW errors never reported. **Fix:** pass `integrations: []` for the background surface, or use `@sentry/core` with a minimal `BrowserClient`. (v1 had this as part of P0.8; downgraded from P0 because it's silent init failure, not a crash.)

### Type safety

- **P1.15 `[ts]` `isNavigationTreeJSON` is an unsound type predicate** — `extension/src/shared/schemas/node.ts:53-61`. Zod validates `root: z.unknown().nullable()` but the predicate narrows to `NavigationNodeJSON | null`. A string passes. **Fix:** recursive `navigationNodeJSONSchema` with `z.lazy`, or drop the narrowing signature.
- **P1.16 `[ts]` Extension ↔ background messages have no runtime validation** — `extension/src/shared/transport/protocols.ts:54-89` is compile-time only. **Fix:** wrap every `onExtensionMessage` handler with a zod parse.
- **P1.17 `[ts]` `SupabaseClient` in tRPC context is untyped** — `packages/trpc/src/types.ts:23` types `db: SupabaseClient` (equivalent to `SupabaseClient<any,"public",any>`). Will remain `any` after P0.6's schema gen unless parameterized here.

### State / errors / observability

- **P1.18 `[obs]` `fireAndForget` drops user mutations with only `console.error`** — `extension/src/apps/sidepanel/api/actions.ts:60-65`. Nine keyboard shortcuts (pin/unpin/delete) fail silently. **Fix:** `showOperationError(…)` + `captureError(…)`.
- **P1.19 `[obs]` Network blip → permanent sign-out** — `extension/src/shared/auth/auth-orchestrator.ts:275-278` catches any `getSession()` throw and emits `{status:"signed-out"}`. **Fix:** differentiate network errors from auth errors.
- **P1.20 `[obs]` Sync-drain failure on SW wake is fully swallowed** — `extension/src/background/sync/sync-engine.ts:690` `void drainPendingOps().catch(() => {})`. **Fix:** log + `captureError` + notify sidepanel.

### Testing

- **P1.21 `[test]` 13 smoke-e2e stubs that always pass** — `extension/tests/smoke-e2e.test.ts` contains 13 `assert.ok(true, 'stub — automation pending')` lines; CI runs them as real tests. **Fix:** convert at minimum auth, sync-fail, website-ping to real Playwright tests.
- **P1.22 `[test]` Zero tests for RLS policies, migrations, or `request_account_deletion()`** — 12 tables have RLS; the destructive RPC has no test. **Fix:** pgTAP via `supabase test db`.
- **P1.23 `[test]` `packages/db` has no test harness at all** — no `scripts.test`, no `vitest.config`, zero test files. **Fix:** after P0.6's `createDb()` factory, add `vitest.config.ts` + integration tests.

### Deps

- **P1.24 `[deps]` `react-icons` unused in `apps/account`** — `package.json "react-icons":"^5.5.0"`, zero imports, ~100+ MB on disk.
- **P1.25 `[deps]` `@supabase/supabase-js` version split** — `packages/db ^2.49.8`, `apps/account ^2.101.0`, `extension ^2.103.3`. Lockfile resolves two distinct versions of every `@supabase/*` sub-package. **Fix:** bump `packages/db` to `^2.103.3`.
- **P1.26 `[deps]` Build tools in extension `dependencies`** — `autoprefixer`, `postcss`, `tailwindcss`, `shadcn` are runtime-declared. **Fix:** move to `devDependencies`.
- **P1.27 `[deps]` `p-memoize` + `@tanstack/react-virtual` declared in extension deps, never imported**. Remove.
- **P1.28 `[deps]` Root `package.json` runtime deps (`@radix-ui/react-slot`, `class-variance-authority`)** — no root `src/`, shadcn-CLI scaffold leftovers.

---

## P2 — Medium (hardening + quality)

### Security / Supabase

- **P2.1 `[sec]` `/api/feedback` unauthenticated Telegram relay** — `apps/marketing/app/api/feedback/route.ts:22`. Verified: already applies IP rate limit (3/min), length cap (`MAX_MESSAGE_LENGTH=1000`), HTML-escape before Telegram. Real risk is spam amplification, not data exposure. v1 severity was overstated. **Fix:** add origin check + CAPTCHA.
- **P2.2 `[sec]` Host-header-derived `url.origin` in auth callback** — `apps/account/app/auth/callback/route.ts:22-23`. Exploitable only on misconfigured deployments where `host` isn't from a trusted proxy. **Fix:** derive from `env.appBaseUrl` server-side.
- **P2.3 `[sec]` Middleware session cookie attributes** — `apps/account/src/lib/supabase/middleware.ts:15-22` forwards `options` from `@supabase/ssr`. Supabase SDK does set `secure/sameSite/httpOnly` correctly by default; issue only materializes if the SDK version's defaults drift. **Fix:** explicitly set cookie options to avoid SDK-default drift.
- **P2.4 `[sb]` 6-digit OTP + 10-tries/5min/IP is distributed-brute-forceable** — `supabase/config.toml:209,237-240`; `token_verifications` default is per-IP. Captcha block commented at 214-217. **Fix:** enable `[auth.captcha]`; extend OTP to 8 for recovery.
- **P2.5 `[sb]` `set_updated_at()` has no `SET search_path`** — `supabase/migrations/003_updated_at_trigger.sql:4-12`. Trap if ever flipped to `SECURITY DEFINER`. **Fix:** `SET search_path = ''`.
- **P2.6 `[sb]` `request_account_deletion` `search_path` includes `extensions`** — `006:31`; function doesn't call `extensions.*`. **Fix:** `SET search_path = ''` + fully qualify.
- **P2.7 `[sb]` `account_deletion_requests` relies on "no policy = deny"** — fragile to future policy additions. **Fix:** `REVOKE INSERT,UPDATE,DELETE FROM authenticated,anon` explicitly.
- **P2.8 `[sb]` `public.users.email` drifts from `auth.users.email`** — after migration 005, `ensurePublicUser` uses `ignoreDuplicates:true` at `apps/account/src/server/backend/user.ts:88`, never refreshed; `email_verified:true` is hardcoded at line 83. **Fix:** re-sync from `auth.users` on every session refresh; stop blindly setting `email_verified:true`.

### MV3

- **P2.9 `[ext]` `scripting` permission auto-injected in dev** — `.output/chrome-mv3-dev/manifest.json:23` present; `wxt.config.ts` permissions don't list it. Prod build strips it. Document or declare.
- **P2.10 `[ext]` `pushHistory` rate-limit window resets on SW wake** — `extension/src/background/sync/sync-engine.ts:69`. Rate limit effectively bypassed on frequent evictions. **Fix:** persist to `session:` storage.
- **P2.11 `[ext]` `TabManager` class-instance state lost on SW wake** — `extension/src/background/state/tab-manager.ts:24-28` (instance fields, not module-scope). `hydrate()` at `service-worker.ts:73` restores `lastNodeByTab`; `ignoredTabs`/cycle state aren't. **Fix:** persist `ignoredTabs` to session storage; document `cycleOrder` as ephemeral if intentional.
- **P2.12 `[ext]` Dynamic `import("../sync/sync-engine.js")` silently swallowed** — `extension/src/background/messaging/notifications.ts:204-208`. **Fix:** log + `captureError`.
- **P2.13 `[ext]` Webnavigation handler swallows all errors** — `extension/src/background/navigation/webnavigation.ts:50`. Blind spot for the core capture path. **Fix:** keep swallow, add log + `captureError`.
- **P2.14 `[ext]` `runMigrations` runs twice on update** — `extension/src/background/service-worker.ts:45,62` (`onInstalled` + module load). Idempotent but redundant. **Fix:** drop one path.
- **P2.15 `[ext]` `p-debounce` push not flushed on SW suspend** — `extension/src/background/sync/sync-engine.ts:398`; `service-worker.ts:53-56` `onSuspend` only flushes tree storage. **Fix:** swap to a debounce variant with `.flush()` (e.g. `lodash.debounce`); flush on suspend.
- **P2.16 `[ext]` `posthog-js` bundled into SW** — `extension/src/shared/lib/observability.ts:19` top-level import; `initObservability("background")` guards runtime init at line 189, so no runtime failure — but ~110 KB of dead code ships in the background chunk. v1's "P0 runtime crash" framing was wrong. **Fix:** dynamic import inside the non-background branch.

### Architecture

- **P2.17 `[arch]` No data-access layer in `apps/account`** — service-role `db` imported directly into RSC pages, Server Actions, route handlers. Verified: 14 files in `apps/account/app/` import `@trail/db` directly (`(dashboard)/trails/mutations.ts`, `(dashboard)/activity/page.tsx`, all 13 files under `app/api/v1/**`). Every `.eq("user_id", …)` is a tenant-scoping bug waiting. **Fix:** `src/server/data/{trails,users,subscriptions,…}` repos.
- **P2.18 `[arch]` `packages/trpc` is a ghost router** — `packages/trpc/src/router.ts:3-11` only `health`+`me`; never mounted (no `fetchRequestHandler`/`createCallerFactory`/`[trpc]` route anywhere). Real consumers pull only the JWT helper. **Fix:** rename to `packages/auth-token`; delete `router.ts`/`trpc.ts`.
- **P2.19 `[arch]` `packages/db` throws at module import** — `client.ts:6-16`. Crashes any test that imports tRPC context types transitively. **Fix:** `createDb()` factory.
- **P2.20 `[arch]` Four lib-folder conventions in `apps/account`** — `lib/`, `components/`, `src/lib/`, `src/server/`, `src/server/backend/` all coexist. Consolidate.
- **P2.21 `[arch]` `packages/ui/src/marketing/` is a mini-app inside a component package** — `sections/` has 6 page-sections; `ui/` duplicates primitives (`button.tsx`, `label.tsx`, `skeleton.tsx`, `switch.tsx`, `accordion.tsx`). Extract to `apps/marketing`.
- **P2.22 `[arch]` `/app/v1/[...path]/route.ts` "temporary" 308-redirect shim** — 5 HTTP methods, no deletion date. Set a kill date.
- **P2.23 `[arch]` `@ui/*` alias** in `extension/tsconfig.base.json` (not `tsconfig.app.json` as v1 said) shadows a future `@trail/ui` import. Rename before integrating.
- **P2.24 `[arch]` `packages/db/package.json` `exports` field puts throwing module at `./`** — transitively loaded by any type-only import via `packages/trpc/src/types.ts:1`. **Fix:** move type re-exports to a `./types` entry.
- **P2.25 `[arch]` Three parallel auth impls never reconciled** — `extension/src/shared/auth/auth-orchestrator.ts` (789 lines), `apps/account/app/login/login-card.tsx`, and the **now-dead** `apps/account/app/auth/extension-relay/page.tsx` (see Removed Findings below — delete this file). `packages/ui/src/auth/LoginView.tsx` was staged for reuse; no consumer. **Fix:** extract `packages/auth`.

### Type safety

- **P2.26 `[ts]` PUT/PATCH payload validation asymmetric** — `apps/account/src/server/api/schemas.ts:77,88`; PUT calls `isJsonValue` at `[id]/route.ts:207`, PATCH skips it at 352. **Fix:** recursive `jsonValueSchema` used by both.
- **P2.27 `[ts]` `TrailSummary` DTO duplicated** — `apps/account/src/server/trails.ts:4-17` vs `apps/account/src/server/backend/trail-serializers.ts:61-93`. Different shapes. Consolidate.
- **P2.28 `[ts]` `trailsListQuerySchema.limit` silently swallows bad input as 50** — `schemas.ts:47-54`. **Fix:** `z.coerce.number().int().positive().max(200).default(50)`.
- **P2.29 `[ts]` `payload: unknown` leaks through public API** — `apps/account/src/server/backend/trail-serializers.ts:36,53`. **Fix:** reuse `treePayloadSchema` as both validator + DTO source.
- **P2.30 `[ts]` OAuth token response shape not shared** — `apps/account/app/api/v1/oauth/token/route.ts:50-57,72-79` duplicates the literal across two branches. **Fix:** export `OAuthTokenResponse` zod schema + type.
- **P2.31 `[ts]` NOWPayments webhook HMAC computed on re-serialized payload** — `apps/account/app/api/v1/billing/webhooks/nowpayments/route.ts:77-81,174-187`. Provider signs raw bytes; the sorted re-serialize can diverge. **Fix:** HMAC over raw body.
- **P2.32 `[ts]` `Record<string, unknown>` used as DB update payload** — `apps/account/app/api/v1/trails/[id]/route.ts:340-369,371-373`. Column-name typos silently become no-ops. **Fix:** `Partial<Database["public"]["Tables"]["trails"]["Update"]>` after P0.6.

### UX / performance / observability / state

- **P2.33 `[ux]` `backdrop-blur-sm` on `SyncConflictBanner`** — `extension/src/apps/sidepanel/ui/components/SyncConflictBanner.tsx:57`. Violates "no glass morphism" rule.
- **P2.34 `[ux]` `blur-2xl` decorative glow behind onboarding logo** — `extension/src/apps/sidepanel/ui/onboarding/steps/WelcomeStep.tsx:9-11`. AI-slop pattern.
- **P2.35 `[ux]` `backdrop-blur-sm` on marketing `PricingCard`** — `packages/ui/src/marketing/components/sections/PricingSection.tsx:44`.
- **P2.36 `[ux]` `SetPasswordForm` confirm-error via `FieldDescription` (no `role="alert"`)** — `extension/src/apps/login/SetPasswordForm.tsx:70`. Compare `VerifyForm.tsx:73` which uses `FieldError`.
- **P2.37 `[ux]` Login/signup inputs missing `autoComplete`** — `extension/src/ui/components/login-form.tsx:70-96`; `signup-form.tsx:67-86`. Password managers broken.
- **P2.38 `[ux]` `rel="extension"` on external links** — `extension/src/ui/components/login-form.tsx:117,121`. Invalid; use `rel="noreferrer"`.
- **P2.39 `[ux]` Onboarding `delay-*` stagger classes** — `StartStep.tsx`, `PrivacyStep.tsx`, `BranchStep.tsx`, `ReadyStep.tsx`. Additionally: `delay-125`, `duration-400` aren't in default Tailwind — **silently no-ops**. Violates "instant animations" rule. **Fix:** remove intra-step delays; if staggering intended, define the tokens.
- **P2.40 `[perf]` `loadTree()` serializes reads that could parallel** — `extension/src/background/services/tree-loader.ts:17-21`. `getActiveSavedAt()` independent of `getOrCreateTree()`. **Fix:** `Promise.all`.
- **P2.41 `[perf]` `buildTreesSnapshot()` serializes two independent reads, called 7× per mutation handler** — `extension/src/background/messaging/handlers/tree-handlers.ts:179-184`. **Fix:** `Promise.all`.
- **P2.42 `[perf]` 6 components select full `state.tree`** — `ContextMenus.tsx`, `CommandPalette.tsx`, `PinnedDropdown.tsx`, `RenameNodeDialog.tsx`, `DeleteTreeConfirmModal.tsx`. Re-render on every tab navigation. **Fix:** gate selectors on dialog-open / context-menu-open state.
- **P2.43 `[perf]` `openNodeIds: new Set(...)` on every `applyTreeState`** — `extension/src/apps/sidepanel/ui/state/store.ts:298,368`. Breaks reference stability for `TrailGraph`. **Fix:** reuse previous Set when contents equal.
- **P2.44 `[perf]` `persistLastNodeByTab()` writes on every navigation** — `extension/src/background/state/tab-manager.ts:125,179,236`. No debounce. **Fix:** `pDebounce(…, 100)`.
- **P2.45 `[obs]` Dual auth state — Zustand vs orchestrator module cache** — `extension/src/apps/sidepanel/ui/hooks/useAuthTransitionToast.ts:4-7` imports directly from orchestrator. **Fix:** drive from Zustand.
- **P2.46 `[obs]` Undo/redo failures silent** — `extension/src/apps/sidepanel/ui/components/FloatingControls.tsx:24-37` `try/catch → console.error`. **Fix:** `showOperationError`.
- **P2.47 `[obs]` 5+ keyboard-shortcut catch sites use bare `console.error`** — `extension/src/apps/sidepanel/ui/hooks/useShortcuts.ts:104,187,220,236,244,254`.
- **P2.48 `[obs]` Inconsistent use of `showOperationError`** — raw `console.error` in `ContextMenus.tsx:249,347`; `CommandPalette.tsx:104,112`; `SettingsPopover.tsx:13`; `FloatingControls.tsx:28,36`. Note: `ContextMenus.tsx:312` already uses `showOperationError` — issue is inconsistency, not absence. `actions.ts:62` is inside a fire-and-forget helper where `console.error` may be intentional.
- **P2.49 `[obs]` 5 of 10 declared analytics events never fired** — `extension/src/shared/lib/observability.ts:48-79` declares `node_created`, `node_deleted`, `node_reparented`, `tree_created`, `tree_switched`; zero `captureEvent(` callsites. (`node_renamed`, `tree_exported`/`tree_imported`, `sync_ok`/`sync_failed` do have callsites.)
- **P2.50 `[test]` Subscription proration/period math untested** — `apps/account/src/server/backend/subscription/{proration,period}.ts`. Silent over/undercharge risk.
- **P2.51 `[test]` Billing provider implementations untested** — `apps/account/src/server/backend/billing/providers/{nowpayments,manual}.ts` have no sibling tests; only the webhook route is tested.
- **P2.52 `[test]` `protectedProcedure` middleware untested** — `packages/trpc/src/__tests__/` has only `extension-token.test.ts`.
- **P2.53 `[test]` OAuth backend PKCE/token rotation untested** — `apps/account/src/server/backend/oauth.ts` fully mocked in API tests.
- **P2.54 `[test]` `architecture-boundaries.test.ts` silently skips if `.output/` stale** — `extension/tests/architecture-boundaries.test.ts:136-139` `if (!existsSync(manifestPath)) { … SKIPPED; return }`. CI runs tests before build.

### Deps

- **P2.55 `[deps]` Bare `lucide` in extension devDependencies** — only `lucide-react` is imported. Remove.

---

## P3 — Low / hygiene / downgraded

- **P3.1 `[sec]` Extension JWT has no `iss`/`aud`** — `packages/trpc/src/extension-token.ts:33-104`. Protects against cross-service secret reuse.
- **P3.2 `[sec]` `console.error` logs full OAuth URL** — `extension/src/shared/auth/auth-orchestrator.ts:708`. Redact.
- **P3.3 `[sec]` `extension/.env.local` exists on disk** — gitignored by root `.env.*` pattern; no leak via git. Only relevant as a reminder that `WXT_*` env values ship publicly in the extension bundle.
- **P3.4 `[ext]` `storage.onChanged` listener registered inside async `initAuth()`** — `extension/src/shared/auth/auth-orchestrator.ts:305`. Chrome's `storage.onChanged` is a permanent API (survives SW context), so this is NOT a structural bug (v1 wrong). Narrow risk only: brief window between SW wake and `await getSession` resolving (~ms) where an event could miss.
- **P3.5 `[ext]` `_favicon` API with `favicon` permission** — NOT `chrome://favicon` (v1 wrong). `extension/src/shared/utils/favicon.ts:5` uses `runtimeGetURL("/_favicon/")` which is the documented MV3 favicon API. No host permission issue. **Removed as a finding; left here as a correction.**
- **P3.6 `[ext]` CSP differs dev vs prod** — dev has `wasm-unsafe-eval`; prod doesn't. Pin prod CSP explicitly.
- **P3.7 `[ext]` `navigator.onLine` check in SW is unreliable** — `extension/src/background/sync/sync-engine.ts:353`. Only a secondary gate. Low impact.
- **P3.8 `[ext]` `unhandledrejection` may fire before Sentry init resolves** — narrow race; `log.error` still works.
- **P3.9 `[ext]` `optimizeDeps.include: ["lucide-react"]`** — dev-only Vite setting; no prod impact (v1 framing was wrong).
- **P3.10 `[ext]` `onSuspend` only flushes tree storage** — duplicates P2.15.
- **P3.11 `[ext]` `viewIntentCounter` resets on SW wake** — `extension/src/background/messaging/notifications.ts:41`. Low impact.
- **P3.12 `[ext]` `sidepanel.html` path hardcoded in two places** — `extension/src/shared/platform/webext.ts:57` + `extension/src/apps/settings/components/SidepanelPeek.tsx:59`. Extract constant.
- **P3.13 `[ux]` `SyncConflictBanner` "Use server" reloads without confirm** — `SyncConflictBanner.tsx:38`. At minimum add tooltip.
- **P3.14 `[ux]` `DeleteTreeConfirmModal` destructive action first** — `DeleteTreeConfirmModal.tsx:74-80`. Reorder Cancel-first.
- **P3.15 `[ux]` `LoginView.tsx:119-123` legacy error display** — zero consumers; dead code. Delete file or consolidate with `<Alert variant="destructive">` if it'll be revived.
- **P3.16 `[ux]` `TrustedBy.tsx:124-125` bg-gradient fade overlays redundant with CSS mask at line 128** — remove the overlay divs.
- **P3.17 `[ux]` Login/signup `CardDescription` says "with your Google account"** but form has email/password — `login-form.tsx:43`, `signup-form.tsx:41`.
- **P3.18 `[ux]` `NewTreeDialog` lowercase dialog title** — `TreeDropdown.tsx:741` `"create a new tree?"` / `"name your new tree"`. Inconsistent with other dialogs.
- **P3.19 `[ts]` Redundant date re-parse after `z.string().datetime()`** — `trails/sync/route.ts:18-23`, `[id]/route.ts:139-144`. Safe but redundant. Downgraded from P2.
- **P3.20 `[ts]` `toApiLabelSource` fallback to `"user"`** — `trail-serializers.ts:15-16`. Unreachable if DB enum stays typed. Downgraded from P2.
- **P3.21 `[ts]` `z.string().url()` deprecated in zod v4** — `schemas.ts:150-151`. Still works; deprecation warning only.
- **P3.22 `[ts]` Extension copied utility hooks use `any`** — `use-memoized-fn.ts:3`, `use-event-listener.ts:6`, etc. Intentional escape hatches matching ahooks API.
- **P3.23 `[ts]` Marketing feedback test uses `as any` ×11**.
- **P3.24 `[ts]` `wishlist_leads` schema has no TS consumer** — dead migration or pre-wired feature.
- **P3.25 `[perf]` `TrailGraph` outer wrapper not `memo()`-wrapped** — `extension/src/features/graph/components/TrailGraph.tsx:431`.
- **P3.26 `[perf]` `useBootstrap` blocks render on `flags` query** — `useBootstrap.ts:64`. Minor.
- **P3.27 `[perf]` `d3-hierarchy` (~14 KB gz) in SW via `layout-precompute.ts:6`** — not a DOM crash; just bundle weight. Extract to pure `@shared/layout`.
- **P3.28 `[perf]` `minisearch` index rebuilt on every tree ref churn** — `CommandPalette.tsx` PaletteBody.
- **P3.29 `[perf]` `handlePaneClick` in `TrailGraph.tsx:340-342` takes `selectedNodeIds` as dep** — Set ref churn. Use `useLatest` like the nearby marquee path.
- **P3.30 `[obs]` Server actions in `apps/account/(dashboard)/trails/mutations.ts:51,73,95,139` don't log Supabase error before discarding**.
- **P3.31 `[deps]` `commander` has 6 transitive versions** — all transitive, no action required (v1 over-stated).
- **P3.32 `[deps]` `tasks/reports/` is committed, not gitignored** — 6 `.md` files tracked. Add `tasks/reports/` to `.gitignore` + `git rm --cached`.
- **P3.33 `[deps]` Commented-out `WindowId` type** — `extension/src/shared/types/ids.ts:10`. Delete.

---

## Removed findings (v1 → v2)

These were in v1 but verification disproved them. Listed here so the conclusions aren't silently overwritten.

1. **v1 P0.1 — "PKCE verifier leaked via URL + postMessage"** — **REMOVED**. `apps/account/app/auth/callback/route.ts?source=extension` branch and `apps/account/app/auth/extension-relay/page.tsx` are dead code. Extension uses `chrome.identity.launchWebAuthFlow` + `supabase.auth.exchangeCodeForSession` directly (`extension/src/shared/auth/auth-orchestrator.ts:671-766`) and never listens for `AUTH_CODE_RELAY`. `extension/tests/transport-contracts.test.ts:90-91` actively asserts the legacy namespace is removed. Cleanup action: delete the relay page + the `if (source === "extension")` block + `apps/account/src/lib/trail-extension.ts` (v1 P1.15).
2. **v1 P1.15 — "Account↔extension postMessage bridge to dead protocol"** — **REMOVED (dead code)**. Same root cause as #1. The `notifyAuthRevoked()` call in `apps/account/components/app-sidebar.tsx:13` always times out silently. Delete `trail-extension.ts` + the call site.
3. **v1 P1.13 — "`_favicon` host permission required"** — **REMOVED**. Implementation uses `chrome.runtime.getURL("/_favicon/…")` which is the documented MV3 API needing only the `favicon` permission (already declared). No degradation.
4. **v1 P3.2 — "JSON-LD only escapes `<`"** — **REMOVED**. `JsonLd.tsx:65` escapes with `\u003c` which blocks `</script>` breakout; JSON-LD input is static server-controlled; standard practice.
5. **v1 P3.9 — "`date-fns` full-library bundle"** — **REMOVED**. `date-fns` v3+ ESM tree-shakes correctly; only the three imported functions land in the bundle.

## Downgrades (v1 → v2)

- v1 P0.1 (PKCE) → removed (see above)
- v1 P0.8 (PostHog + Sentry in SW) → **split**: PostHog to P2.16 (dead code in bundle, not runtime crash), Sentry to P1.14 (silent init failure, real)
- v1 P1.3 (`/api/feedback`) → P2.1 (has rate-limit + length cap + HTML-escape)
- v1 P1.9 (`/auth/logout`) → P1.4 (Bearer path is authenticated; CSRF applies only to cookie path)
- v1 P1.10 (cookie attrs) → P2.3 (SDK default is usually correct)
- v1 P1.11 (`storage.onChanged` async registration) → P3.4 (Chrome API is permanent)
- v1 P1.15 (dead protocol) → removed
- v1 P2.16 (Sentry init race) → P3.8 (narrow race only)
- v1 P2.20 (`optimizeDeps`) → P3.9 (dev-only)
- v1 P2.24 (`toApiLabelSource` fallback) → P3.20 (unreachable if types hold)
- v1 P2.26 (date re-parse) → P3.19 (safe, just redundant)
- v1 P2.63 (commander version bloat) → P3.31 (transitive, no action)
- v1 P3.1 (.env.local) → P3.3 (not actually committed; reminder only)
- v1 P3.11 (`useBootstrap` blocks on flags) → P3.26 (queries are parallel; only final gate blocks)
- v1 P3.17 (`LoginView` legacy) → P3.15 (dead code, downgrade to cleanup)
- v1 P3.21 (`getTelemetryConsent` null) → (removed) fallback `{errors:true,analytics:true}` prevents null at runtime
- v1 P3.27 (`.claude/worktrees` stale) → (removed) worktrees are active per `git worktree list`, not stale

## Appendix — Per-agent verdicts (v1 counts vs v2 after verification)

| Scope | v1 P0 | v1 P1 | v1 P2 | v1 P3 | v2 P0 | v2 P1 | v2 P2 | v2 P3 |
|---|---|---|---|---|---|---|---|---|
| App security | 1 | 3 | 7 | 3 | 0 | 7 | 3 | 3 |
| Supabase security | 3 | 6 | 6 | 3 | 3 | 4 | 5 | 0 |
| Chrome extension MV3 | 4 | 8 | 10 | 5 | 2 | 2 | 7 | 8 |
| Architecture | 5 | 10 | 10 | 5 | (1 cluster) | — | 9 | 0 |
| API/type safety | 1 | 6 | 7 | 5 | (in arch cluster) | 3 | 7 | 5 |
| UI/UX + a11y | 0 | 2 | 6 | 5 | 0 | 0 | 7 | 5 |
| Performance | 2 | 4 | 5 | 2 | 0 | 1 | 5 | 5 |
| State/errors/observability | 0 | 3 | 6 | 3 | 0 | 3 | 5 | 1 |
| Testing | 2 | 4 | 5 | 3 | 0 | 3 | 5 | 0 |
| Dead code/deps | 1 | 5 | 6 | 3 | 0 | 5 | 1 | 2 |

---

## Recommended sequencing

**Week 1 — P0 ship-blockers:** P0.1–P0.3 (Supabase RLS + account deletion), P0.4–P0.5 (SW alarms + drain ordering), plus P0.6's "generate `Database` types + parameterize db" (this one step unblocks ~12 downstream typing findings).

**Week 2 — architecture consolidation:** rest of P0.6 (delete `@trail/ui` or adopt it; consolidate bearer-token resolvers; DAL extraction for `apps/account`). Delete v1 dead code: PKCE relay page + `trail-extension.ts` + `notifyAuthRevoked` call + `LoginView.tsx`.

**Week 3 — P1 hardening:** P1.1–P1.7 (CORS/rate-limit/CSRF/fragment fallback/JSON DoS), P1.8–P1.11 (remaining Supabase RLS hardening), P1.14 (`integrations: []` for background Sentry), P1.18–P1.20 (surface silent failures).

**Week 4 — tests:** P1.21–P1.23 (smoke stubs → real e2e, pgTAP for RLS + deletion RPC, `packages/db` harness), plus P2.50–P2.54 as capacity allows.
