# Task: Make share functionality production-ready (fix private sharing) — 2026-05-27

## Root cause (verified)
`supabase/templates/magic_link.html` renders `{{ .Token }}` — a 6-digit code,
NOT a clickable `{{ .ConfirmationURL }}` link. This is intentional (config.toml:253
— the extension can't consume magic-link URLs; Chrome opens them outside the
extension storage origin). But `apps/marketing/app/s/[code]/restricted-share-gate.tsx`
calls `signInWithOtp({ emailRedirectTo, shouldCreateUser:false })` and only completes
via a *clicked magic link* (`?code=` → `exchangeCodeForSession`). Since the email is a
code with no link, the gate is a dead end → private sharing never works.

## Fix: rewrite the gate to OTP code-entry (matches the email actually sent)
Mirror the extension's proven pattern (`extension/src/shared/auth/orchestrator/flows.ts`).

- [x] Map share architecture (page/gate/api/RPC/RLS/extension) — done via Explore agents
- [x] Confirm root cause (template + config + gate code) — done
- [ ] Rewrite `restricted-share-gate.tsx`:
  - [ ] Step 1 (email): `signInWithOtp({ email, options: { shouldCreateUser: false } })`.
        Drop `emailRedirectTo` (dead — no ConfirmationURL in template).
        - success → advance to code-entry step
        - user-not-found / "signups not allowed" → keep explicit, actionable
          "no Trail account — install the extension & sign up first" message
        - rate-limit (`over_email_send_rate_limit`, max_frequency=60s) → "try again in a moment"
  - [ ] Step 2 (code): 6-digit `Input` (numeric, one-time-code), strip ws + `/^\d{6}$/`,
        `verifyOtp({ email, token, type: "email" })` → `window.location.reload()`.
        - expired/invalid → keep form mounted, offer resend
  - [ ] Remove dead magic-link `?code=` / `exchangeCodeForSession` path
  - [ ] Keep "signed in but not on allowlist" branch (authenticated=true)
  - [ ] Rewrite all "click the link" copy → "enter the code"
- [ ] No Supabase template/config changes (code-email is intentional)
- [ ] Keep `shouldCreateUser:false` (web auth surface deliberately minimal — project_auth_surface)
- [ ] Verify: typecheck/lint the marketing app; review full gate once more

## Notes / assumptions
- `verifyOtp` type for a `signInWithOtp`-issued code = `"email"` (EmailOtpType in session.ts:23).
- Cookie parity: `verifyOtp` via `createBrowserClient` writes `sb-*` cookies (document.cookie),
  same path the existing `exchangeCodeForSession`+reload relied on → server re-reads on reload.
- `flowType:"pkce"` is irrelevant to `verifyOtp` (only affects OAuth/magic-link code exchange).

## Review
**Done — share private gate rewritten to OTP code entry.**
- `restricted-share-gate.tsx` fully rewritten: email → `signInWithOtp({shouldCreateUser:false})`
  → 6-digit `Input` → `verifyOtp({type:"email"})` → `window.location.reload()`. Dead
  magic-link `?code=`/`exchangeCodeForSession` path removed. Resend + "use a different
  email" + rate-limit/expiry error mapping added. Copy rewritten ("Email me a code",
  "enter the code", removed "click the link").
- Verified: `tsc --noEmit` clean, eslint clean, prettier formatted.
- Cookie parity confirmed at the library level: `createBrowserClient` (no `cookies`
  option) uses the `document.cookie` branch in `@supabase/ssr` cookies.js:91-103;
  `setAll` writes synchronously and `_saveSession` is awaited inside `verifyOtp`, so the
  `sb-*` cookies exist before `reload()` → server re-runs `get_shared_trail` with the
  viewer's identity.
- Bonus root-cause insight: even a working magic link couldn't have worked in prod — a
  per-code `emailRedirectTo` (`/s/<uuid>`) can't be redirect-allowlisted. OTP has no
  redirect, so it sidesteps that too.

## Adjacent finding (out of literal "share" scope) — web password reset has the SAME bug
`supabase/templates/recovery.html` also renders `{{ .Token }}` (a code, no link), but
`apps/marketing/app/auth/reset-password/page.tsx` completes via `exchangeCodeForSession(?code=)`
— a magic-link click flow. CAVEAT: the repo `recovery.html` is code-only, but config.toml is
local-only; the *hosted* recovery template wasn't empirically confirmed (the user only reported
the share/magic_link email as code-only). If the hosted recovery template also carries a
`{{ .ConfirmationURL }}`, the old `?code=` flow may have worked. The OTP rewrite is correct
either way (cross-device, matches extension). 30-sec confirm: trigger one recovery email.
(Extension recovery works — it uses `verifyEmailOtp(..., "recovery")`.) Fix mirrors the
share gate: email → `resetPasswordForEmail` → 6-digit `verifyOtp({type:"recovery"})` →
set-password form. Surfaced to user for a scope decision.

**Done (user approved) — `/auth/reset-password` rewritten to self-service OTP.**
- Three steps on one page: email → `resetPasswordForEmail` (swallows `user_not_found` —
  recovery is an enumeration target) → 6-digit `verifyOtp({type:"recovery"})` →
  set new password (`updateUser`) → signOut → success. No reload needed (recovery session
  + updateUser share one client). signOut on mount clears any lingering session (premortem #5).
- Removed dead `exchangeCodeForSession(?code=)` path. Kept password-policy hints + success CTA.
- Verified: tsc clean, eslint clean, prettier formatted.

## What I deliberately did NOT change (verified sound, per advisor)
- Server ACL in `get_shared_trail` RPC, owner-only RLS, view-count rate-limit, snapshot
  sanitization, UUIDv7 validation, existence-leak resistance, extension ShareDialog/import.
- Supabase email templates / config (code-email is intentional for the extension).
