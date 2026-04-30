# Manual smoke tests — Codex review 2026-04-28

These cover REVAL-003 (alarms-driven sync) and the post-deploy regression
checks for BATCH 3 (auth integrity) and BATCH 4 (data integrity). Run
after each release that touches the listed surfaces.

## REVAL-003 — chrome.alarms drives sync-pull (not setInterval)

**Surface:** extension background service-worker.

1. Open `chrome://extensions` → Trail → "Service worker" link → DevTools.
2. In the DevTools console run: `chrome.alarms.getAll().then(console.log)`.
3. Expect an entry with `name: "trail-sync-pull"` and `periodInMinutes` set.
4. Run `setInterval = () => { throw new Error("setInterval used") }` to
   trip any background code that still relies on `setInterval` instead
   of `chrome.alarms`.
5. Wait ~30 s; service worker should not throw.
6. Force-trigger via `chrome.alarms.create("trail-sync-pull", { delayInMinutes: 0.05 })`
   and verify a sync-pull is logged in DevTools.

## BATCH 3 — auth-integrity flow regression

**Surface:** account web + extension.

1. Sign up a fresh email via the account login page. Confirm the email
   in the verification link.
2. Query Supabase Dashboard → Table editor → `public.users`:
   confirm `email_verified` mirrors `auth.users.email_confirmed_at` (true
   after click). Before BATCH 3 the server used to write `email_verified=true`
   optimistically; now it must come from the RPC.
3. Reset the password (forgot-password flow), log in again. Inspect
   `public.users.auth_session_version`: should have incremented (proves
   the new `bump_auth_session_version` RPC was called).
4. Sign out from two devices simultaneously. `auth_session_version`
   should increment by 2 (or eventually settle to 2 above pre-test value).
   Read-modify-write would have lost one increment; the RPC is atomic.

## BATCH 4 — DATA-002 device-user-mismatch hard reject + extension wipe

**Surface:** account API + extension storage.

1. Sign in to the extension as user A. Trigger a sync; inspect
   `chrome.storage.local` for the `trail_device_id` key. Note the value.
2. Sign out. Sign in as user B in the same browser profile.
3. Query `chrome.storage.local` again — `trail_device_id` should be
   reset (null or a fresh UUID). The `wipeUserScopedLocalState` flow
   (`extension/src/shared/auth/auth-orchestrator.ts:150`) clears it
   on user-change.
4. Trigger a sync as user B. Inspect Supabase `devices` table:
   the previous device row owned by user A is unchanged; user B has a
   new device row.
5. Negative test: temporarily disable the wipe by injecting the old
   device id back into storage as user B, then trigger sync.
   Expected: HTTP 409 `device_user_mismatch`. Pre-BATCH-4 the server
   would silently re-assign the device row to user B.

## REL-001 (defer) — chunk size warnings

Build extension and inspect `.output/chrome-mv3/` chunk sizes. Background
chunk currently > 500 kB and react-vendor > 600 kB. Defer per plan; track
in next release if user-facing impact (extension cold-start time) regresses.
