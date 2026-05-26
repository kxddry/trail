# Trail - Adultify: Production-Grade Product

## UUID v7 for shared trees (replace random-word codes) — Plan (2026-05-26)

### Goal
Shared trees use **UUID v7** identifiers instead of the random base64
codes ("random words"). Delete code left unused by the switch.

### Findings
- Share **code** = PK of `shared_trail_links`, currently
  `base64url(gen_random_uuid())` (v4, 122 random bits), minted
  server-side in `create_share_link` (latest def = migration 021). This
  is the visible `/s/<code>` identifier the user calls "random words".
- Imported **trail id**: `import_shared_trail` (latest def = migration
  026) mints the new trail id with `gen_random_uuid()` (v4) — the only
  v4 trail id in an otherwise all-v7 trail space (normal trails minted
  client-side via `uuidv7()` in `tree-storage.ts`, synced via
  `upsert_trail`, which trusts the client id). Genuine inconsistency.
- `uuid.ts` `uuidv7()` is THE only v7 mint path (per `ids.ts`). PG is
  v17 (no native `uuidv7()` until PG18) → v7 must be client-minted,
  consistent with every other PK. Import is extension-driven, so we can
  pass a client-minted trail id into the RPC.
- Marketing `/s/[code]` does no code-format validation → format change
  safe. `sanitize.ts` touches only the snapshot, not the code.
- Security: v4→v7 for the code drops entropy 122→74 bits (still
  uncrawlable) + leaks creation time (lowest-sensitivity). Codebase
  already accepts this for every other PK. Accepted (advisor-confirmed).

### Plan
- [x] `029_share_uuidv7_ids.sql`: redefine `create_share_link` (accept
      `p_code text`, validate v7, drop server-side gen + retry loop) and
      `import_shared_trail` (accept `p_new_trail_id uuid`, validate v7).
      Drop old signatures; re-GRANT. Add `_rollback/029...`.
- [x] `share-api.ts`: `createShareLink`/`importSharedTrail` mint
      `uuidv7()` and pass the new params.
- [x] `database.types.ts`: add `p_code` / `p_new_trail_id` to the Args.
- [x] Delete unused code: `extension/src/features/sharing/flags.ts`
      (zero importers; doc-comment admits "not consulted at runtime").
- [x] Verify: extension typecheck clean (0 errors), full extension test
      suite 160/160 pass. Validated the PG v7-regex + version-nibble
      checks against the live DB via a non-mutating no-FROM SELECT
      (v7 accepted any-case; v4 and old base64 codes rejected).

### Review (2026-05-26)
- Share code is now a client-minted UUID v7 (the visible /s/<code> is a
  real v7 string, not base64-of-v4). Imported trail ids are v7 too, so
  imported trails match every other trail in the system.
- Server no longer generates codes; it validates the client-minted v7
  shape and keeps a single defensive unique_violation guard (no retry
  loop — collision across 74 random bits is astronomically unlikely).
- `migrations-rement.ts` was checked and left alone (it's the active
  node id re-mint helper, imported by migrations.ts + its test; not dead
  and outside sharing scope).
- NOT applied to prod — `make migrate` + the matching extension build
  are the deploy step (see note below).

### Deploy note
RPC signatures change. Deploy migration (`make migrate`) + the updated
extension together — an old extension build calls the removed signatures
and would fail to create/import shares until updated. (Not applied to
prod by this change.)

## Shared Trails + apps/account Retirement — Plan (2026-05-19)

### Reframing (evidence-backed, see file:line)
The original goal frames four parallel tracks. Code says two are already done:

- **OTP email confirmation is already shipped.** `extension/src/shared/auth/auth-orchestrator.ts:5-39` doc-comment: "Magic links are NOT used". `supabase/templates/confirmation.html` uses `{{ .Token }}` (6-digit code), not a link. `supabase/config.toml:226-241` has `enable_confirmations=true`, `otp_length=6`, `otp_expiry=600`. `LoginApp.tsx:136-139,216,236` routes signup → OTP-verify UI. Nothing to migrate; only verify hosted Dashboard mirrors local config.

- **Extension self-auth is already shipped.** OAuth via `chrome.identity.launchWebAuthFlow` + `exchangeCodeForSession` at `auth-orchestrator.ts:951-1053`. PKCE-only (`supabase.ts:46`). Session in `chrome.storage.local` (`supabase.ts:16-20`). Manual refresh via `chrome.alarms` (service-worker.ts:26-35). Zero calls to `/api/v1/*` (grep confirmed). No `@trail/auth-token` imports. Cross-account wipe in place (`auth-orchestrator.ts:128-151,223-239`). Sync writes go direct to `trails` via RLS (`sync-engine.ts:343-347`), not the service_role-only `upsert_trail` RPC — so migration 017's revoke does not bite.

Net: the real plan is **(1) audit prod alignment, (2) ship sharing, (3) clean up dead code, (4) retire `apps/account`**.

### Architecture decisions (locked)

| Decision | Choice | Rationale |
|---|---|---|
| Share data model | New `shared_trail_links` table with `snapshot jsonb` (frozen at mint time) | Immutable snapshot makes revoke semantics clean and untangles "owner edits after sharing" from leakage; imported clones are independent rows in the importer's `trails` (full clone, not live mirror) — satisfies "removing shared trees does NOT delete from already-imported users" |
| Public read access | `get_shared_trail(code text)` RPC, SECURITY DEFINER, GRANT to anon. **Anon role gets ZERO direct SELECT on `trails` or `shared_trail_links`.** | Matches existing wishlist precedent (`supabase/migrations/010_wishlist_lead_rpc.sql`) |
| Owner ops | `create_share_link`, `list_my_share_links`, `revoke_share_link` RPCs, SECURITY DEFINER, GRANT to authenticated, ownership checks inside | Concentrates write authority server-side; extension/marketing both call the same surface |
| Import RPC | `import_shared_trail(code text)` RPC mints a **new UUID** for the cloned trail, never preserves source id. Uses `FOR SHARE` lock + `revoked_at IS NULL` check inside the function | Atomic against concurrent revoke (premortem #10); prevents cross-trail id collisions (premortem #4.4) |
| Snapshot sanitization | At mint time, before persist: strip URL fragments unconditionally, drop query strings on non-allowlisted hosts, denylist param names (`session`, `token`, `auth`, `code`, `nonce`, `state`, `api_key`), round timestamps to day granularity, drop `layout` offsets, strip unicode bidi-override codepoints (U+202A-U+202E, U+2066-U+2069) from titles, hard-cap title length at 256 chars, hard-cap snapshot at 2MB / 10k nodes | Premortem #1 + #14.2 — the single most likely "we breached our privacy promise" failure mode |
| Web share viewer | `apps/marketing/app/s/[code]/page.tsx` — **top-level, outside `[locale]`** | Short shareable URL `gettrail.net/s/<code>`, no locale leak; middleware matcher adds `s/\|auth/\|` exclusions |
| Extension↔web bridge | Extend existing `trail-bridge-v1` postMessage protocol via content-script. **NOT `externally_connectable`.** | Codebase-consistent (`extension/src/content/bridge/` already wired), works identically in Chrome and Firefox, no need to pin prod/dev extension IDs in marketing build. Add `IMPORT_SHARED_TRAIL` to `extension/src/shared/transport/protocols.ts` and a handler in `extension/src/content/bridge/website-bridge.ts` + `register-runtime.ts` |
| Capability handshake | `PING` response includes `capabilities: string[]` array; marketing import button checks for `"share_import"` before showing | Old extensions installed prior to bridge handler must not show a broken Import button |
| Reset-password page | Ship it at `gettrail.net/auth/reset-password` (top-level, outside `[locale]`) | A user who lost extension access (reinstalled browser) must still be able to recover password without first reinstalling Trail |
| Share-management UI | Extension-only, in the existing settings page | `apps/account` is going away |
| Feature flags | Two: `share_create_enabled` (extension-side) and `share_import_enabled` (marketing-side) | Separation of read/write blast radius; flip create-flag without resubmitting to CWS once the build is on stable channel |
| Public viewer rendering | v1: minimal read-only viewer in marketing (xyflow + d3-hierarchy), NOT extraction of `TrailGraph` from extension | v1 velocity, zero coupling risk; defer shared package to v2 once the surface stabilizes |
| OG/SEO | `noindex` + `nofollow` in `<meta robots>` AND `X-Robots-Tag` header AND `Disallow: /s/` in robots.txt; OG metadata is generic ("A trail on Trail") — **no trail content in `og:title` / `og:description`** | Premortem #9 + #14.3 — first time a share gets posted in a public Slack and Google indexes it, the dataset is open. OG-leakage defeats the opaque-code design. |

### Resolved decisions (2026-05-19)

- **Billing**: never launched → cut entirely in Phase 0 with the rest of the dashboard pages. No billing migration sub-plan. Phase 5 is not blocked by billing.
- **OAuth-as-provider endpoints**: no external consumers → cut with the rest of `apps/account` in Phase 5.
- **Reset-password page**: ship it (Phase 4).
- **`app.gettrail.net` endgame**: 301 redirect for 30 days then NXDOMAIN (delete DNS record). No permanent static page; old links break definitively after the soak.
- **Dashboard access**: open — confirm before Phase 0 start; both Phase 0 audit and Phase 5 URL-config surgery require Supabase Dashboard admin.

### Day-one must-haves (premortem top 5, inline below — not appendixed)

These are enumerated as checkboxes inside the phases where they land. Listed here for visibility:

1. URL sanitization at mint time → Phase 1 (`create_share_link` RPC).
2. Anon-role isolation: no direct SELECT on `trails` or `shared_trail_links`; only `get_shared_trail` RPC → Phase 1.
3. Snapshot semantics: snapshot at mint, `FOR SHARE` lock + `revoked_at IS NULL` check inside `import_shared_trail`, NEW UUIDs on import, 2MB/10k-node cap, no CDN cache on `/s/<code>` → Phase 1 + Phase 2.
4. `noindex` + `X-Robots-Tag` + `Disallow: /s/` + generic OG → Phase 2 viewer.
5. Three-actor cross-tenant trap (owner / viewer / importer): pending-import slot must be added to `wipeUserScopedLocalState` (`auth-orchestrator.ts:128-151`); import dialog shows the exact account name; capability handshake on PING → Phase 2.

### Phase 0 — Audit (0.5–1.5d, no user-facing change)

- [ ] Confirm hosted Supabase Dashboard mirrors local `supabase/config.toml`: Site URL, Additional Redirect URLs include `https://pginmdonnghdkcmnhjkniphopcfapodc.chromiumapp.org/*` and `https://gettrail.net/auth/reset-password`, the six email templates uploaded match repo files, password policy = `lower_upper_letters_digits_symbols`, OTP length/expiry mirror, `secure_password_change=ON`.
- [ ] Verify in Google Cloud Console: only `chromiumapp.org` URIs are required as OAuth authorized redirects; prune any `app.gettrail.net` entry.
- [ ] Capture audit findings in `supabase/DASHBOARD.md` as the going-forward source of truth.
- [ ] Per-page fate decisions for `apps/account/(dashboard)/*`: all of `{trails, settings, activity, onboarding, billing}` are cut — extension owns these (or they were never launched).

### Phase 1 — Sharing DB layer (2–3d, no user-facing change)

- [ ] `supabase/migrations/018_shared_trail_links.sql`: table with `code text PK` (gen via `gen_random_bytes(16)` → base64url, 22 chars, ~128 bits entropy), `trail_id uuid REFERENCES trails(id) ON DELETE CASCADE`, `owner_id uuid` (denormalized for RLS perf), `snapshot jsonb NOT NULL`, `created_at`, `revoked_at`, `view_count bigint DEFAULT 0` (premortem: bigint not int4 — anon-callable view-count is a flood vector). Index `(code) WHERE revoked_at IS NULL`, `(owner_id, created_at DESC)`. RLS: owner-only (`auth.uid() = owner_id`). Rollback file at `_rollback/018_shared_trail_links.sql`.
- [ ] `supabase/migrations/019_share_rpcs.sql`:
  - `create_share_link(p_trail_id uuid) RETURNS jsonb` — SECURITY DEFINER, `SET search_path = ''`, validates `auth.uid() = trails.user_id`, **runs the sanitizer on the snapshot before persist** (strip fragments + denylisted query params + bidi-override unicode in titles + truncate to 256 chars + cap at 2MB/10k nodes), GRANT EXECUTE TO authenticated, returns `{ code, url }`. UNIQUE-violation retry loop on code generation.
  - `list_my_share_links() RETURNS SETOF shared_trail_links` — SECURITY INVOKER, GRANT to authenticated, leverages owner RLS.
  - `revoke_share_link(p_code text) RETURNS boolean` — SECURITY DEFINER, soft-delete (`UPDATE ... SET revoked_at = now() WHERE code = $1 AND owner_id = auth.uid() AND revoked_at IS NULL`), GRANT to authenticated.
  - `get_shared_trail(p_code text) RETURNS jsonb` — SECURITY DEFINER, `SET search_path = ''`, validates `revoked_at IS NULL`, returns snapshot + owner display_name (no email), increments `view_count` via separate fire-and-forget UPDATE to limit flood-write cost, GRANT to anon + authenticated.
  - `import_shared_trail(p_code text) RETURNS uuid` — SECURITY DEFINER, **`SELECT ... FOR SHARE` on the share row with `revoked_at IS NULL` check in the same transaction**, mints **new** UUID for cloned trail, refuses self-import (`owner_id != auth.uid()`), inserts into importer's `trails` with all node IDs regenerated, GRANT to authenticated, returns new trail id.
- [ ] `supabase/tests/shared_trail_links.rls.test.sql` (pgTAP): anon cannot SELECT on table; owner-only SELECT; cross-user create fails; revoked links stop resolving; expired share fails import; new UUIDs on clone; ON DELETE CASCADE fires when trail deleted; collision retry works.
- [ ] Sanitizer is a separate SQL function `_sanitize_trail_snapshot(jsonb) RETURNS jsonb` invoked by `create_share_link`; unit-tested with adversarial inputs (URLs with `?token=...`, RTL-override titles, oversized blobs).

### Phase 2 — Sharing client surfaces + CWS cutover (4–6d dev + 1–7d CWS wait)

Order: build extension first, submit to CWS, ship marketing with flag off, flip flag after extension reaches stable.

- [ ] **Extension protocol**: add `IMPORT_SHARED_TRAIL` message constant to `extension/src/shared/transport/protocols.ts` (alongside existing `PING`, `OPEN_PANEL`); add to `WebsiteProtocolMap` type with `(code: string) => { ok: true; treeId: string } | { error: string }`.
- [ ] **Extension bridge handler**: in `extension/src/content/bridge/website-bridge.ts` and `register-runtime.ts`, add `IMPORT_SHARED_TRAIL` handler that (a) refuses if extension is signed-out (queue the code into a new `chrome.storage.session` `pendingShareImportItem`, send `OPEN_PANEL`, return error), (b) if signed-in, calls `supabase.rpc('import_shared_trail', { p_code: code })` under the user's JWT, (c) opens the imported tree in sidepanel.
- [ ] **Capability handshake**: extend `PING` response with `capabilities: string[]`; include `"share_import"` once the handler is wired. Marketing checks this before rendering Import button.
- [ ] **Account-switch wipe**: add the new `pendingShareImportItem` to `wipeUserScopedLocalState` in `extension/src/shared/auth/auth-orchestrator.ts:128-151` (ref lesson `tasks/lessons.md` 2026-04-27).
- [ ] **Extension Share dialog** (`extension/src/apps/sidepanel/ui/components/ShareDialog.tsx`): shadcn `Dialog`. Switch labeled "Available to anyone with your link" → flip on calls `create_share_link`, shows the URL with copy-button. Below: disabled section "Only select users (Coming soon)" with shadcn `Tooltip` "Available in a future update". On dialog close while sharing is on: stays shared. Bottom: "Stop sharing" link in destructive color; click → confirm dialog with copy **"Anyone with the link loses access. People who already imported keep their copy."** → calls `revoke_share_link`. Per memory `feedback_shadcn_only.md`, all UI through shadcn.
- [ ] **Extension Share entry point**: add "Share" item to the active-tree action menu in sidepanel (sibling to existing Pin/Archive/Delete patterns per `ContextMenus.tsx:220-450`). Gated by `share_create_enabled` PostHog flag.
- [ ] **Extension management UI**: new "Shared links" section in extension settings — `list_my_share_links` → list with copy-button + revoke per row. Empty state with one-line explainer.
- [ ] **Marketing Supabase clients**: add `apps/marketing/src/lib/supabase/server.ts` and `client.ts` (copy patterns from `apps/account/`); add `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY` to `apps/marketing/.env.example`.
- [ ] **Marketing middleware update**: change matcher in `apps/marketing/middleware.ts:9` to `/((?!api|_next|_vercel|robots.txt|sitemap.xml|s/|auth/|.*\\..*).*))` so `/s/*` and `/auth/*` skip i18n.
- [ ] **Marketing share viewer**: `apps/marketing/app/s/[code]/page.tsx` (server component) calls `get_shared_trail` via anon Supabase server client; `notFound()` on revoked/missing. Read-only graph render (minimal xyflow + d3-hierarchy, no extraction from extension for v1). Minimal `layout.tsx` (small branded header, no marketing nav).
- [ ] **Marketing viewer SEO/privacy**: `export const metadata` with `robots: { index: false, follow: false, googleBot: { index: false, follow: false, noimageindex: true } }`; add `X-Robots-Tag: noindex, nofollow` response header; `<meta name="referrer" content="no-referrer">`; OG metadata is **generic** ("A trail on Trail") — no trail content in `og:title` / `og:description`; create/update `apps/marketing/app/robots.ts` to add `Disallow: /s/`.
- [ ] **Marketing 404**: `apps/marketing/app/s/[code]/not-found.tsx` with "This trail isn't available" + Install Trail CTA.
- [ ] **Marketing Import button**: on `/s/<code>`, gated by `share_import_enabled` env flag AND capability handshake; clicks call `sendWebsiteMessage('site/import-shared-trail', { code })` with a 2s timeout; on timeout, show "Install Trail extension" link + copyable code fallback (per `feedback_mvp_quality.md` — verify the fallback states work). On success, show toast + send `OPEN_PANEL` to surface the imported tree. **Do not** redirect to `chrome-extension://...?treeId=...` (platform-unreliable).
- [ ] **Favicon proxy**: shared snapshots include `favicon` fields; `chrome://favicon/*` URLs 404 in a browser and external favicons are tracker-pixel vectors (premortem #14.1). v1: drop `favicon` field at sanitize time, viewer fetches favicons from `https://www.google.com/s2/favicons?domain=...` based on hostname. Defer self-hosted favicon proxy to v2.
- [ ] **PostHog flags**: declare `share_create_enabled` and `share_import_enabled` (defaults: false). Wire into `extension/src/features/sharing/flags.ts` (new file) and into marketing via Vercel env var.
- [ ] **CWS submission** of the extension build with sharing code dormant; wait for stable channel.
- [ ] **Staged flip**: staff → 10% → 100%, monitoring `IMPORT_SHARED_TRAIL` error rate + Postgres logs.

### Phase 3 — Dead-code purge (0.5–1d, no user-facing change)

- [ ] Delete `apps/account/src/lib/trail-extension.ts` (dead per `tasks/reports/2026-04-19-full-review.md` #1).
- [ ] Delete `apps/account/app/auth/extension-relay/` (dead per same report).
- [ ] Update `apps/account/components/app-sidebar.tsx:13` to drop the `notifyAuthRevoked` call referencing the relay.
- [ ] Grep for `@trail/auth-token` imports outside `apps/account/src/server/backend/`; confirm only account is using it.
- [ ] Audit `apps/account/app/auth/callback/route.ts` and `auth/login/route.ts` for the now-dead `?source=extension` branch; prune.

### Phase 4 — Marketing `/auth/reset-password` (1d)

- [ ] **Before code ships**, add `https://gettrail.net/auth/reset-password` to Supabase Dashboard → URL Configuration → Additional Redirect URLs.
- [ ] `apps/marketing/app/auth/reset-password/page.tsx` (client component): extract `?code=` from URL, call `supabase.auth.exchangeCodeForSession`, show password+confirm form with live policy hints (mirror policy from memory `project_password_policy.md`: lower+upper+digit+symbol min 8), call `supabase.auth.updateUser({ password })`. Success state: "Open Trail extension" CTA via existing `OPEN_PANEL` website-message; fallback Install link.
- [ ] `apps/marketing/app/auth/reset-password/layout.tsx`: small centered card layout, no marketing nav.
- [ ] `apps/marketing/src/lib/password-policy.ts`: validator + hints (shared with reset page; tiny duplication of extension's policy is fine for v1).
- [ ] States: loading, invalid/expired link (with "Request new link" form that pings extension to do `resetPasswordForEmail`), policy violation (inline hints), passwords-mismatch, network error (retry), success.
- [ ] **Update extension**: in `auth-orchestrator.ts:854-882` `requestPasswordReset`, set `redirectTo: "https://gettrail.net/auth/reset-password"` instead of `chrome.identity.getRedirectURL()`. Strict improvement: now the email link works in a browser too.
- [ ] Defensive: call `supabase.auth.signOut()` before `exchangeCodeForSession` to prevent cross-account confusion (premortem #5).
- [ ] Locale: English-only v1; accept `?lang=` param but no i18n yet. Flag follow-up ticket.

### Phase 5 — Retire `apps/account` (2–3d dev + 30d soak)

- [ ] Supabase Dashboard: remove `https://app.gettrail.net/*` from Additional Redirect URLs; switch Site URL to `https://gettrail.net` if currently the account host.
- [ ] Vercel: add 301 redirect rule on the `trail-account` project: `*` → `https://gettrail.net$1` (preserve path/hash). Keep alive 30 days.
- [ ] Marketing: drop hardcoded `NEXT_PUBLIC_APP_URL` fallback in `apps/marketing/lib/public-env.ts:7`; grep marketing for `app.gettrail.net` references and update.
- [ ] CI: in `.github/workflows/ci-web.yml`, remove account env vars (lines 38-50), the `--filter @trail/account` from Typecheck (line 72), the Build (account) step (lines 76-77).
- [ ] Root `package.json:9`: remove `"dev:account"` script.
- [ ] Delete `apps/account/` directory. `pnpm install` regenerates lock without account (workspace glob `apps/*` auto-excludes).
- [ ] Delete `packages/auth-token/` (account-only consumer per inventory).
- [ ] Docs: update `README.md`, `extension/CONTRIBUTING.md`, `trail_privacy_policy_terms_of_service.md` (privacy policy must mention sharing in the same shipping window as Phase 2 — public sharing breaks the "data stays local" promise).
- [ ] After 30 days of soak with redirect log monitoring: delete the Vercel `trail-account` project AND delete the `app.gettrail.net` DNS record. Endgame is NXDOMAIN — no permanent landing page.

### Out of scope (explicitly v2 or later)

- "Only select users" sharing (UI shows it greyed-out with "Coming soon" tooltip)
- Refresh-snapshot for share owners (snapshot is frozen at mint; create a new link for updates)
- Self-hosted favicon proxy (v1 uses Google s2/favicons URL substitution after dropping the source's favicon field)
- Interactive read-only graph in marketing matching the extension's TrailGraph (v1 ships minimal viewer, defer extraction)
- Localized share viewer UI (v1 is English-only; trail content is user-language regardless)
- View-count UI surfaces (raw counter exists in DB; surface to owner in v2)
- Per-share expiration / TTL (column omitted from `shared_trail_links` v1; add when needed)
- Account-deletion GDPR purge of imported clones (premortem #14.11) — surface in privacy policy; tooling later

### Verification before declaring shipped

- [ ] pgTAP tests in CI pass; anon role explicitly tested to fail SELECT on both new tables/views.
- [ ] Extension Playwright e2e: share-from-extension → import-from-different-account → revoke → import fails with friendly message.
- [ ] Marketing E2E: load `/s/<valid>`, `/s/<revoked>`, `/s/<missing>` show expected pages; `Disallow: /s/` present in `robots.txt`; `X-Robots-Tag` header present in response.
- [ ] Manual: paste a real share link in Slack; verify OG preview is generic ("A trail on Trail"), not user content.
- [ ] Manual: sign out / sign in as different user with `pendingShareImportItem` set; verify it's wiped before the new user sees anything.
- [ ] Cross-browser smoke: Chrome stable + Firefox latest; the postMessage bridge must work in both.
- [x] Privacy policy updated to disclose sharing (`trail_privacy_policy_terms_of_service.md`).

### Implementation results (2026-05-19)

Status: code for Phases 1, 2, 3, 4 landed locally; account/auth-token directories deleted from disk (Phase 5 source-code piece); operations (Supabase Dashboard URL config, CWS submission, Vercel redirect, DNS) still TBD.

**Phase 1 — DB layer.**
- `supabase/migrations/018_shared_trail_links.sql` — table + RLS + indexes; anon SELECT denied, owner-only direct access; `view_count BIGINT` per premortem.
- `supabase/migrations/019_share_rpcs.sql` — `create_share_link`, `list_my_share_links`, `revoke_share_link`, `get_shared_trail` (anon-callable), `import_shared_trail` with `FOR SHARE` lock + `revoked_at IS NULL` re-check + new UUID mint + self-import refusal. Server caps at 2 MB / 10 000 nodes.
- Rollbacks at `_rollback/018_*.sql` and `_rollback/019_*.sql`.
- `supabase/tests/share_links.test.sql` covers 18 cases including anon isolation, ownership guards, structural caps, NEW-UUID-on-import, revoke idempotency, and get/import after revoke.

**Phase 2 — Client surfaces.**
- Extension protocol: added `WEBSITE_MESSAGE.IMPORT_SHARED_TRAIL` + `WebsitePingReply.capabilities` and a new `EXTENSION_MESSAGE.IMPORT_SHARED_TRAIL_FROM_SITE` (`extension/src/shared/transport/protocols.ts`).
- Capability registry at `extension/src/shared/transport/capabilities.ts` advertises `"share_import"`.
- Bridge handler in `extension/src/content/bridge/{website-bridge,register-runtime,runtime}.ts` forwards page→SW.
- Background handler at `extension/src/background/messaging/handlers/share-from-site-handler.ts` and wiring in `register-extension-messaging.ts`.
- Pending-import slot `pendingShareImportItem` in `extension/src/shared/config/storage-items.ts`; wiped on account switch (`auth-orchestrator.ts:128-151`); consumed on first sign-in by `service-worker.ts`.
- Sharing module at `extension/src/features/sharing/{sanitize,share-api,flags}.ts`: TS sanitizer strips URL query+fragment, drops favicon, drops timestamps/visit-count/layout, strips bidi-override unicode, truncates titles at 256 chars. RPC wrappers + buildShareUrl. Flag stub.
- Share dialog at `extension/src/apps/sidepanel/ui/components/ShareDialog.tsx` (shadcn Dialog/Switch/Tooltip) with disabled "Only select users (Coming soon)" affordance and the exact revoke-warning copy ("Anyone with the link loses access. People who already imported keep their copy."). Wired into `TreeDropdown.tsx` action row.
- Added `Icons.Share2` to the central icon registry.
- Observability: 7 new `AnalyticsEvent` entries (`share_create_*`, `share_revoked`, `share_import_*`).
- Marketing public viewer at `apps/marketing/app/s/[code]/{page,layout,not-found}.tsx` + `import-button.tsx` + `shared-trail-tree.tsx`. Server-fetches `get_shared_trail`; generic OG metadata; `<meta robots>`+`X-Robots-Tag`+`Disallow: /s/`+`Cache-Control: private, no-store`.
- Marketing Supabase clients at `apps/marketing/lib/supabase/{server,client}.ts`; types and API at `lib/shared-trail-*.ts`.
- Marketing middleware excludes `/s/*` and `/auth/*` from the next-intl locale matcher.
- `apps/marketing/next.config.mjs` sets `X-Robots-Tag` + `Cache-Control` headers for `/s/*`. `app/robots.ts` disallows `/s/`.
- `apps/marketing/.env.example` adds `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_SHARE_IMPORT_ENABLED=false`.

**Phase 3 — Dead-code purge.**
- Folded into Phase 5: removed alongside the `apps/account` directory rather than landing as a separate cleanup commit.

**Phase 4 — Reset-password page.**
- `apps/marketing/app/auth/reset-password/{page,layout}.tsx` with PKCE `exchangeCodeForSession`, password policy hints, success → "Open Trail extension" CTA, defensive `signOut()` before code exchange (premortem #5).
- `apps/marketing/lib/password-policy.ts` mirrors the Supabase `lower_upper_letters_digits_symbols` + min 8 policy.
- Extension `requestPasswordReset` in `auth-orchestrator.ts:854-882` now points `redirectTo` at `https://gettrail.net/auth/reset-password`.

**Phase 5 — Account retirement.**
- `apps/account/` and `packages/auth-token/` removed from the workspace.
- Root `package.json` `dev:account` script removed.
- `.github/workflows/ci-web.yml` no longer builds/typechecks account; placeholder Supabase env wired for marketing builds.
- `Makefile`, `README.md`, `trail_privacy_policy_terms_of_service.md` updated.
- **Still TBD (operational, outside this code change):** add `https://pginmdonnghdkcmnhjkniphopcfapodc.chromiumapp.org/*` and `https://gettrail.net/auth/reset-password` to Supabase Dashboard → URL Configuration; flip `NEXT_PUBLIC_SHARE_IMPORT_ENABLED=true` in marketing Vercel env after extension CWS submission reaches stable; add a 30-day `app.gettrail.net` → `gettrail.net` 301 redirect in Vercel; submit extension build to CWS; after the 30-day soak, delete the trail-account Vercel project and the `app.gettrail.net` DNS record (endgame is NXDOMAIN per the locked decision).

**Verification gates passed.**
- `pnpm typecheck` (extension, marketing, packages/db) — green.
- `pnpm -r test` (extension custom test runner + marketing vitest) — 17 + 11 tests pass.
- `pnpm --filter @trail/marketing build` — clean build, `/s/[code]` dynamic, `/auth/reset-password` static.
- Extension `pnpm check` — lint clean, format clean, typecheck clean (3 pre-existing unrelated warnings).

**Known follow-ups deferred to v1.5+ (called out in plan):**
- "Only select users" sharing implementation.
- "Refresh snapshot" for share owners.
- Self-hosted favicon proxy.
- Localized share viewer UI.
- Interactive read-only graph in marketing (v1 renders a static nested list; xyflow extraction punted).
- View-count UI surfaces.

## Comprehensive Review: 2026-04-28
- [x] Record review scope, checklist, and artifact paths
- [x] Run local quality gates: lint, tests, typecheck, web builds, extension checks
- [x] Run targeted account API/security and extension runtime tests
- [x] Inspect security/auth/data boundaries and verify high-risk candidates
- [x] Inspect extension runtime, sync, auth-transition, and test-harness drift
- [x] Inspect UI/UX/a11y/responsive hotspots across marketing, account, and extension surfaces
- [x] Inspect CI/release/devops quality gates and stale documentation
- [x] Revalidate old findings from `tasks/reports/*`
- [x] Create `tasks/review/2026-04-28/findings.json`
- [x] Create `tasks/review/2026-04-28/dashboard.html`
- [x] Add review results summary and next actions

### Review Results
- Artifacts: `tasks/review/2026-04-28/findings.json` and `tasks/review/2026-04-28/dashboard.html`; Russian copies: `tasks/review/2026-04-28/findings.ru.json` and `tasks/review/2026-04-28/dashboard.ru.html`.
- Scope: clean local `dev` baseline `f0e25577`, audit-only; no production accounts or external secrets used.
- Finding ledger: 33 total findings: 7 P0, 16 P1, 10 P2. Includes 14 old-report revalidations instead of blindly copying prior issues.
- Highest-risk active items: public `internal:<uuid>` bearer acceptance on billing/subscription routes, account deletion RPC fallback that can self-delete every accessible trail, AUTH_TRANSITION contract drift blocking aggregate tests, stale extension Playwright expectations, targeted account API mock/env drift, and production dependency advisories.
- Local gates: `pnpm typecheck`, `pnpm -C apps/marketing build`, `pnpm -C extension check`, `pnpm -C extension build`, targeted extension runtime tests, marketing tests, and package DB tests passed or passed with recorded warnings.
- Failing or blocked gates: `pnpm lint`, `pnpm test`, `pnpm -C apps/account build`, `pnpm -C extension test`, targeted account API/security tests, extension Playwright e2e, `pnpm -C extension preview:ui`, `pnpm audit --prod`, and Supabase pgTAP local DB verification.
- Browser/UI checks: marketing routes loaded locally; account routes redirected to login when unauthenticated but emitted next-intl `INVALID_KEY` errors for dotted error message keys; extension preview was reachable but Vite logged unresolved import errors. Dashboard itself was browser-checked at desktop and mobile widths with no load errors or horizontal overflow.
- Deferred fix order: start with P0/P1 security/data integrity, then test-gate repair, CI/release hardening, dependency upgrades, and UI/a11y backlog.

## Spotlight V3: Tree-aware Navigator
- [x] Extend Spotlight contracts/results/actions for tree-aware nodes, external fallback actions, and graph preview RPC
- [x] Index pinned/current/archived tree nodes for cross-tree Spotlight search
- [x] Implement foreign-tree open flow and default-search-engine fallback actions
- [x] Fix Spotlight graph hover so transient hover never recenters and committed selection restores correctly
- [x] Add foreign-tree graph preview in Spotlight and restructure the left rail into titled sections
- [x] Run Spotlight typecheck/tests and capture follow-up notes

## Phase 1: Requirements Gathering (Agent Teams)
- [ ] **Security Architect** - Auth, session persistence, token lifecycle, vulnerabilities
- [ ] **QA Engineer** - Bug discovery, test gaps, error handling audit
- [ ] **DevOps Engineer** - CI/CD gaps, deployment hardening, monitoring
- [ ] **UX Reviewer** - UI/UX issues, error states, loading states, accessibility

## Phase 2: Backlog Creation
- [ ] Synthesize findings into prioritized backlog
- [ ] Critical bugs first (auth session expiry bug)
- [ ] CI/CD improvements
- [ ] Code quality improvements

## Phase 3: Implementation (Agent Teams)
- [ ] Fix auth session persistence bug (user-reported)
- [ ] Fix all discovered bugs
- [ ] Implement CI/CD improvements
- [ ] Code quality fixes

## Phase 4: Verification & PR
- [ ] Run all tests
- [ ] Verify auth fix works
- [ ] Create PR to main

## Onboarding Review: 2026-04-22
- [x] Read external onboarding research note from `~/vault/inbox/20260416-Qsq-Sj_rojU-How Top Apps Design Onboarding.txt`
- [x] Inspect current account onboarding flow and supporting copy
- [x] Compare current flow against research principles and identify friction/gaps
- [x] Write review summary with prioritized UX improvements

### Review Notes
- Current flow is a 4-step slideshow (`welcome -> install -> firstTrail -> done`) with mostly explanatory copy and no product preview or live activation feedback.
- `Skip for now` marks onboarding as complete and redirects to `/trails`, so an unactivated user can permanently exit the flow without installing the extension or capturing a first trail.
- The aha moment is delayed until after the user installs the extension, leaves the app, browses somewhere else, and later returns manually. The flow does not guide or verify that path.
- Empty `/trails` already repeats the same install CTA, which suggests the current onboarding and first empty state should likely be merged into one activation checklist instead of two disconnected experiences.
- Highest-value improvements: replace slideshow steps with task-based activation, make progress state real, show Trail in action immediately, and keep onboarding pending until extension install + first captured trail.

## Extension Onboarding Review: 2026-04-22
- [x] Locate the sidepanel onboarding flow and persisted onboarding state
- [x] Inspect wizard, interactive tour, celebration, CTA, and localized copy
- [x] Compare the extension flow against the referenced onboarding note
- [x] Summarize highest-impact improvements for the extension flow

### Review Notes
- The extension flow is materially stronger than the account web onboarding: it already uses outcome-first copy, persona-based personalization, and a try-before-sign-in interactive tour.
- The main weakness is front-loaded explanation: 5 modal screens before the first interactive payoff is still too much friction for a sidepanel extension surface.
- `skipOnboarding()` sets `phase: "done"` immediately, both from the wizard and from the tour coach, so users can permanently exit before experiencing the branch/revisit payoff.
- The final CTA completes onboarding whether the user signs in or skips, which is fine if activation is the goal, but weak if sync adoption is a core business outcome.
- Russian locale content for onboarding is still mostly English, so the extension currently loses tone, trust, and comprehension for RU users.

## Sidepanel — slow initial load on big trees (2026-05-19, code-structural ranking, not yet profiled)

### Headline cause: ~7–9 full traversals of the same tree before first paint
The active tree JSON is walked, validated, allocated, or otherwise iterated end-to-end ~7–9 times between SW cold-wake and the first ReactFlow paint. Each walk is O(N) with allocations; on a 5–10k node tree these compound into the dominant wall-clock cost.

The walks, in order, for a cold SW open:

1. `tree-storage.ts:386` — SW loads JSON from `chrome.storage`, runs `NavigationTreeMapper.fromJSON`: Zod `safeParse` (`shared/schemas/node.ts:45`) **per node** + `new TreeNode` per node + recursive `appendChildren`. Zod safeParse on a moderately complex schema is the per-node bottleneck.
2. `tree-handlers.ts:141` — SW runs `NavigationTreeMapper.toJSON(tree)`: full recursive walk just to re-serialize back to JSON for the RPC reply.
3. `tree-handlers.ts:116` (`coversAllNodes`) — SW walks the JSON tree again to verify cached positions cover every node.
4. Port message: structured-clone of the JSON blob across the SW↔sidepanel boundary (one more O(N) pass under the hood, plus payload-size penalty).
5. `store.ts:391` — sidepanel `bootstrapGraph` runs `NavigationTreeMapper.fromJSON(payload.tree)` AGAIN: Zod safeParse per node + new TreeNode per node.
6. `store.ts:392` — `new PinnedManager(tree)` walks the in-memory tree.
7. `useGraphLayout.ts:43` — `computeChainFoldInfo` DFS (skipped only when `settings.privacy.collapselist` is empty).
8. `useGraphLayout.ts:50` — `computeGeometry`:
   - `treeToEdges` (`transforms.ts:136`) DFS over the JSON tree.
   - `computeTreePositions` (`tree-layout.ts:32`) — d3-hierarchy build + Reingold–Tilford layout (cache-miss path; see fix #3).
9. `useGraphLayout.ts:58` — `computeActivePathIds` (`transforms.ts:33`): builds a SECOND d3-hierarchy + linear `.find` to locate `currentNodeId`.
10. `useGraphLayout.ts:64` — `treeToNodes` (`transforms.ts:49`) DFS.
11. `layout.ts:158` — `applyNodeMetadata` final pass.

(`tree.size()` is O(1) from a maintained counter — not a walk.)

Then ReactFlow mounts. Even with `onlyRenderVisibleElements`, every node object is allocated upstream of culling.

### Amplifiers

- **A. Layout-cache miss doubles the deserialization tax.** When `buildTreeSnapshot` doesn't have positions covering every node (typical after any recent mutation — debounced positions cache only saves ~1.5s after `cacheTree`), it ships positions=null and fires `requestLayoutRefinement` (`notifications.ts:126`). That posts a second `TREE_UPDATED` once positions are computed. `useRuntimeMessages` (`useRuntimeMessages.ts:16`) routes it to `applyTreeState` (`store.ts:411`) which **runs `NavigationTreeMapper.fromJSON` AGAIN** and reallocates `PinnedManager`. The user sees an initial layout, then a second full render storm ~one tick later. The cold-open critical path effectively pays for steps 5–11 twice.

- **B. `React.lazy(TrailGraph)` adds a chunk fetch after bootstrap.** `App.tsx:35` lazy-loads TrailGraph (which transitively imports xyflow/react, d3-hierarchy, motion CSS, fold-chains). The dynamic import only starts AFTER `bootstrapStatus === "ready"`, so the user sees the bootstrap skeleton → the Suspense fallback skeleton → the actual graph. Cold cache: 100–300ms of extra serial round-trip after bootstrap data arrives.

- **C. Lifecycle "enter" mass-annotation on first mount.** `useNodeLifecycleEnabled()` defaults ON (`flags.ts:60`). On first mount `prevIdsRef.current` is empty, so every visible node is classified as "entering": cloned with className + staggered `animationDelay` (`useNodeLifecycle.ts:114`), CSS keyframe `graph-node-enter 280ms` starts on each, and a `setTimeout` fires another `useMemo` recomputation at ~432ms (`useNodeLifecycle.ts:194`). For a large viewport-filling tree this is N object allocations + N GPU animations + a second render pass shortly after.

- **D. `getTreeState` awaits `authReady`.** `tree-handlers.ts:447` `await authReady` before serving the tree. `authReady` (`auth-orchestrator.ts:96`) resolves only after `initAuth` runs, which on a cold SW with a signed-in user can include a Supabase client init + `users` upsert (`auth-orchestrator.ts:179`). The active tree blob is already user-correct on disk (the orchestrator wipes per-user state on identity mismatch), so this gate is conservative at the cost of a guaranteed cold-open delay.

- **E. Per-node `useUpdateNodeInternals` on TrailNode mount.** `TrailNode.tsx:81` fires a measure-and-update side effect on each mounted node. Bounded by `onlyRenderVisibleElements`, but when `smoothFitView` settles the camera into a mid-zoom (LOD = "near"), each visible node fires the effect and queues an internal recompute in xyflow.

### Proposed fixes (priority by code-structural impact, not yet measured)

1. **[P0] Drop Zod from the tree deserialization hot path.** Replace `normalizeNodeData` (`shared/schemas/node.ts:45`) with a hand-rolled normalizer (`typeof url === 'string' ? url : ''` etc.). Zod safeParse with this many transform branches is the dominant per-node cost on **two** of the cold-open walks (and **three** when the layout-refinement push fires). Keep Zod at trust boundaries: sync pull payloads from the server, import bundles. Local-storage and SW↔sidepanel transit are not trust boundaries — the data was already validated when it entered the system.

2. **[P0] Eliminate the SW JSON round-trip for `getTreeState`.** Cache the most recent serialized JSON alongside the in-memory tree in `tree-storage.ts` and invalidate on `cacheTree`. `buildTreeSnapshot` then serves the cached JSON directly instead of running `NavigationTreeMapper.toJSON` on every snapshot request. Drops walk #2 entirely; on snapshot-after-mutation paths still has to re-serialize, but the cold-open path (no mutations between SW wake and sidepanel open) saves the walk.

3. **[P0] Always include positions in the FIRST `getTreeState` response — kill the double-render path.** When `coversAllNodes` fails, compute positions synchronously inline in `buildTreeSnapshot` (the same d3 work the sidepanel would do — better in the SW with the source-of-truth in-memory tree) and ship them in the initial response. Removes amplifier A: no `requestLayoutRefinement` push, no second `applyTreeState` → no second `NavigationTreeMapper.fromJSON` + `PinnedManager` rebuild + render storm. d3-hierarchy layout is fast enough (5–10k nodes ≈ 30–80ms) to be worth the synchronous cost vs. the doubled deserialization.

4. **[P1] Eager-import TrailGraph in parallel with bootstrap, or drop `React.lazy` for it.** Either kick off `import("@features/graph/components/TrailGraph.js")` at module top-level in `apps/sidepanel/ui/main.tsx` (in parallel with the RPC queries and observability init), or remove the lazy split entirely. The bundle is on the critical path for ~every sidepanel open; the lazy split only delays first paint without saving any work for the user. Removes amplifier B.

5. **[P1] Skip the lifecycle "enter" cohort on the very first mount.** In `useNodeLifecycle` (`useNodeLifecycle.ts:79`), detect first-render (`prevIdsRef.current.size === 0 && currentIds.size >= LARGE_COHORT_THRESHOLD`) and treat it as a bootstrap paint: pass nodes through unchanged, just seed `prevIdsRef` and `lastSnapshotRef`. Removes amplifier C: no thousand-way `className` cloning and no 432ms re-render storm. Subsequent expand/collapse cohorts (the actual intent of the animation) still work normally.

### Recommended fix combination (root-cause, no костыли)

After consulting the advisor and grepping sidepanel `state.tree` consumers (`SelectionActionBar`, `PinnedDropdown`, `CommandPalette`, `ContextMenus`, `useShortcuts`, `delete-tree`, `command-palette-search`, store reducers), every consumer uses **only read methods**: `findNodeById`, `getRoot`, `getCurrent`/`getCurrentId`, `getChildren`, `iter`, `size`. None of them call mutation methods like `navigate`, `setCurrent`, `deleteNode`, etc. — those live exclusively in the background SW. This unlocks the cleanest fix.

**A. [Architectural] Stop constructing OOP TreeNodes on the sidepanel side.** Make `treeJSON` the single source of truth on the sidepanel. In `bootstrapGraph`/`applyTreeState`, build two indexes in a single O(N) walk:
- `nodeIndex: Map<NodeId, NavigationNodeJSON>` — replaces `tree.findNodeById`.
- `parentIndex: Map<NodeId, NodeId>` — replaces `node.getParent()` (used by selection/delete helpers).

Adapter shims (`findNodeById`, `getChildren`, `getRoot`, `iter`) operate on the JSON. This is the rewrite: delete `state.tree`, delete `state.pins` (PinnedManager — derive `isPinned` from `node.data.pinned` directly or build a Set in the same walk), wire the existing consumers to read from `nodeIndex` / `treeJSON.root`.

**What this eliminates:**
- Walk 5 (`NavigationTreeMapper.fromJSON` in `bootstrapGraph`/`applyTreeState` — Zod safeParse + `new TreeNode` per node).
- Walk 6 (`new PinnedManager(tree)` — another walk).
- **Doubles the savings under amplifier A**: when the layout-refinement second `TREE_UPDATED` lands, `applyTreeState` no longer pays the deserialization tax twice.
- Removes need for fix #2 (cached SW-side JSON) — the SW already keeps `treeJSON` derivable from the in-memory tree; the savings move to the sidepanel where the wall-clock matters.

**B. [P0] Drop Zod from `normalizeNodeData` — or stop normalizing on the deserialize path entirely.** Once the sidepanel doesn't `fromJSON`, only the SW cold-load path remains (`tree-storage.ts:386`). Validate once at trust boundaries (sync pull, import bundles); local storage and SW↔sidepanel transit are not trust boundaries. The current double-normalization is defense-in-depth with measurable cost and no new attacker surface — the data was validated when it entered the system.

**C. [P0] Synchronous positions in the first `getTreeState` response.** Compute d3 layout inline in `buildTreeSnapshot` when `coversAllNodes` fails (bounded by a wall-clock budget — say 150ms — with null fallback for pathological trees). Removes the `requestLayoutRefinement` second-push pattern. d3 Reingold–Tilford on 5–10k nodes is ~30–80ms in practice, comfortably under budget. The "compute later, notify with another TREE_UPDATED" pattern was a костыль from when precompute was async; one transactional response is the correct shape.

**D. [P0] Remove `React.lazy(TrailGraph)`.** TrailGraph IS the sidepanel. Lazy-splitting your primary view is overhead with no payoff — the user opens the panel TO see the graph; deferring its chunk only delays first paint.

**E. [P0] Run auth init in parallel with `getTreeState`, not as a gate.** The active tree blob is already user-correct on disk: `wipeUserScopedLocalState` (`auth-orchestrator.ts:128`) clears it on identity mismatch BEFORE the tree handler can read stale data. The `await authReady` in `tree-handlers.ts:447` is double-protection at the cost of a guaranteed cold-SW delay for every signed-in user. Auth gating belongs on push/sync (where wrong-user writes matter), not on read.

**F. [P1] Lifecycle-skip rule, reformulated.** First mount = `prevIdsRef.current.size === 0`. Full stop. No node-count threshold needed — bootstrap paint is not an "entering" cohort regardless of tree size. Pass nodes through unchanged on first render, just seed `prevIdsRef` and `lastSnapshotRef`. Subsequent expand/collapse cohorts work normally.

### Ordering and why

`A → B` is the big architectural win and unlocks the rest. `C, D, E` are independent and can land in any order. `F` is a small, clean change worth bundling.

**Verification before shipping A:** confirm in the SW that no message reply path other than `buildTreeSnapshot` constructs `NavigationTree` and ships it to the sidepanel. `useRuntimeMessages` only handles `TREE_UPDATED` which feeds `applyTreeState` → same rewrite covers it. Conflict-related RPCs (`getStoredTreeForConflict`, `fetchConflictPreview`) return their own shapes — verify they don't transitively need a sidepanel-side OOP tree.

### Caveats / what to verify before shipping fixes

- **Ranking is code-structural, not measured.** Build with a real 5–10k node tree, capture a Chrome Performance flame chart of a cold-SW sidepanel open, and confirm Zod safeParse + the two JSON round-trips actually dominate. The amplifiers (A–E) are well-evidenced in code but the relative weights are a guess until profiled. Per `feedback_mvp_quality`: don't ship fixes without measuring.
- **Fix #2 must keep the JSON cache invalidated on every `cacheTree` call** — a stale cached JSON served back to the sidepanel would silently drift from the in-memory tree.
- **Fix #3 makes `getTreeState` synchronously expensive on cache miss** — verify no other caller depends on the snapshot returning in <X ms. Currently only the bootstrap path calls `getTreeState`.
- **Fix #5 must NOT skip when the cohort is small** — onboarding tree (1–5 nodes), empty-state-to-first-node, etc., where the "entering" animation is actually a desired UX cue.
- Verify `tree.size()` in `background/state/nav-tree.ts` — if it's a walk rather than a maintained counter, fix it (one-line change).

---

## Fix drag-to-reparent lag (2026-05-20)

### Problem

After commit `d7e7a94` ("cursor-tight drag via imperative DOM"):
1. The dragged node still doesn't follow the cursor with zero lag.
2. Connected edges (branches) do not move during drag — they only update on release.

### Root cause

Current `handleNodesChange` wrote `--drag-x`/`--drag-y` CSS variables on the dragged node's DOM element; an `!important` rule in `pane.css` overrode xyflow's inline transform. Empirically (and per the `882b9fd → d7e7a94` post-mortem), in xyflow v12 controlled mode:
- The rendered node position comes from the React-controlled `nodes` prop. Without a state update, the dragged node stays at its layout position visually AND xyflow's internal `nodeInternals.position` (used for edge endpoint resolution) stays frozen.
- The CSS-variable workaround moved the node visually but did NOT advance `nodeInternals`, so edge `d` paths stayed pinned to the source's pre-drag position.

The prior "round-trip through React state" attempt was actually correct — the lag it caused came from putting `dragOverride` inside `displayNodes`'s deps, forcing a full-tree map (~5000 entries) + a `useNodeLifecycle` pass downstream on every pointermove tick. ~5000 × 2 array iterations per tick is what added 30–50ms, not React state per se.

### Fix

Restore React-state-driven drag position, applied AFTER the heavy memos so they stay cold:

- New `dragPosition: { id, x, y } | null` state, updated in `onNodesChange` on every `position+dragging` change.
- Cleared in `onNodeDragStop`.
- Override applied in a new downstream `finalNodes` memo: `lifecycleNodes → finalNodes`. Single O(N) pass per tick, only the dragged node gets a new object reference.
- `displayNodes`/`lifecycleNodes` deps unchanged → those memos stay cold.
- Dropped the `data-drag-active` / `!important` CSS hack; React state is the single source of truth.

This makes xyflow's internal `nodeInternals` track the drag position via the controlled `nodes` prop → incident edges follow the dragged node in real time.

### Plan

- [x] Edit `extension/src/features/graph/components/TrailGraph.tsx`:
  - [x] Add `dragPosition` state.
  - [x] Rewrite `handleNodesChange` to `setDragPosition` (with reference-stable bailout).
  - [x] Drop `clearDragTransform`; call `setDragPosition(null)` in `handleNodeDragStop`.
  - [x] Add `finalNodes` memo (after `lifecycleNodes`); use it as ReactFlow `nodes` prop.
  - [x] Update inline doc comments to reflect new approach.
- [x] Edit `extension/src/features/graph/pane.css`:
  - [x] Remove the `[data-drag-active="true"]` `!important` rule and its preamble comment.
- [x] Typecheck (no new errors from our files), lint, prettier, relevant unit tests (`reparent.test.ts`, `graph-layout.test.ts`) — all green.
- [x] Commit and push to `claude/fix-drag-reparent-lag-NddIp`.
- [ ] Open PR to `main`.

### Review

- TrailGraph.tsx: +49/-28 lines net; the drag-handler section is the only logic change, the rest is doc comments.
- pane.css: removed 22 lines (the `data-drag-active` block + preamble).
- The new `finalNodes` memo is the only new per-tick work during drag: a single O(N) array `.map` where unchanged nodes pass through by identity. xyflow's nodes-prop diff finds exactly one changed object and updates its transform + the few incident edges.
- `getIntersectingNodes`, validity ring, reparent commit on drop — all unchanged.

### Follow-up: relayout transition was animating the dragged node

User reported after the first fix that edges followed but the node itself still trailed the cursor. Root cause: `relayout.css` applies `transition: transform 350ms ease-in-out` to **every** `.react-flow__node` when the `graph--relayout-animated` class is on the container (which it almost always is). That transition was intended for tree-topology morphs (collapse/expand) — but it also fires during drag, so each React-state-driven transform write was being tweened over 350ms instead of jumping immediately. The cursor moved, the node interpolated behind it.

Connected edges have no `d` transition, so they snap — which is why the previous fix made them follow instantly while the node alone lagged.

Fix: xyflow adds a `.dragging` class to the actively-dragged node (see `useDrag` in `@xyflow/react`). One CSS rule in `relayout.css` clears the transform transition on `.react-flow__node.dragging`, so the dragged node lands its new transform in the same paint as the pointermove. Other nodes keep their relayout interpolation.

- [x] Edit `extension/src/features/graph/motion/relayout.css`: add `.react-flow__node.dragging { transition: none }` override.

---

## React Flow Antipatterns Audit — 2026-05-20

### Goal
Find every React Flow / @xyflow/react antipattern in `extension/src/features/graph/`. No code changes — produce a review report.

### Scope (files with @xyflow/react usage)
- `components/TrailGraph.tsx` (872 lines, main consumer)
- `components/TrailNode.tsx` (357 lines, custom node)
- `components/GraphControls.tsx` (62 lines)
- `components/LodController.tsx` (26 lines)
- `hooks/useGraphLayout.ts` (87 lines)
- `hooks/useCmdWheelZoom.ts` (71 lines)
- `motion/useCameraControls.ts` (169 lines)
- `motion/useNodeLifecycle.ts` (232 lines)
- `lod.ts`, `types.ts`

### Plan
1. Read main files into context.
2. Launch 3 parallel Explore subagents:
   - **Agent A**: TrailGraph.tsx — state, props, memoization, handlers
   - **Agent B**: TrailNode.tsx + LOD + motion hooks — node render perf
   - **Agent C**: useGraphLayout + useCameraControls + useCmdWheelZoom — layout, camera, side-effects
3. Synthesize findings, dedupe, rank by impact (perf vs correctness vs maintainability).
4. Write `tasks/reports/react-flow-antipatterns.md` with file:line citations.
5. Commit + push to `claude/find-react-flow-antipatterns-neXa9`.

### Review
Полный отчёт: `tasks/reports/2026-05-20-react-flow-antipatterns.md`.

**Резюме:** код React Flow слоя в `extension/src/features/graph/` очень тщательно оптимизирован — большинство канонических антипаттернов (новые `nodeTypes`, отсутствие мемоизации nodes/edges, вложенные провайдеры, тяжёлый `node.data`) **отсутствуют**.

Найдено **5 настоящих** антипаттернов:
1. **Критический** — `useMemo` мутирует 4 рефа и читает `performance.now()` (`useNodeLifecycle.ts:66-200`). Работает только потому, что Strict Mode сегодня не double-invoke'ит `useMemo`. Сломается под React Compiler / concurrent rendering / возможным ужесточением React 19+.
2. **Критический** — присваивание `displayNodesRef.current = displayNodes` в теле рендера (`TrailGraph.tsx:564-565`).
3. **Заметный** — inline `proOptions={{...}}` literal (`TrailGraph.tsx:850`).
4. **Заметный** — `applyNodeMetadata` + `treeToNodes` пересоздают все ~5к node-объектов при любом изменении metadata (`layout.ts:158`, `transforms.ts:49-117, 75-91`). Дампируется RF-диффом и `TrailNode` memo, но даёт GC-пики.
5. **Заметный** — `onNodesChange` молча игнорирует не-position changes (`TrailGraph.tsx:212-221`) без комментария "почему".

И ~4 спорных паттерна (O(N) finds, identity-churn smoothCenter, getIntersectingNodes per-frame, per-node useUpdateNodeInternals) — minor.

Кода не менял: задача — audit-only. Если решите фиксить, приоритеты в отчёте.

## Tree storage: unify active vs stored split (refactor, 2026-05-23)

**Problem.** `extension/src/background/services/tree-storage.ts` keeps the active tree's data under `activeTreeItem` (single global key) while every other tree lives under `treeBlobKey(id)` with an index entry. The "active" role is conflated with the storage tier, so every "operate on tree by id" call site has to branch on `if (active.id === treeId)`. When a call site forgets the branch, the active tree behaves as if it doesn't exist.

**Evidence of the smell.**
- `doPushTree` (`extension/src/background/sync/sync-engine.ts:465-468`) — explicit active-vs-stored fork.
- `DELETE_TREE` (`extension/src/background/messaging/handlers/tree-lifecycle-handlers.ts:501-596`) — two full code paths under `isActive`.
- `stashActiveTree` / `takeStoredTree` (`tree-storage.ts:786, 817`) — exist only to shuttle data between the two tiers.
- `EXPORT_TREE` (fixed 2026-05-23 in `tree-lifecycle-handlers.ts:624`) — forgot the branch, threw "Tree not found" on the current trail's share / export.
- Several handlers implicitly assume "the active tree may or may not have an index entry" — this is the bug surface.

**Target shape.**
1. **Storage keys.** Every tree (including the active one) lives under `treeBlobKey(id)`. `activeTreeMetaItem` reduces to `activeTreeIdItem: string` (just a pointer).
2. **Index.** Every tree has an entry, no exceptions. No special-casing the active id in or out of the index.
3. **Hot path stays cheap.** Keep `cachedTree`, `scheduleSave`, `flushSaveNow` exactly as today — they're the reason for the split in the first place. The flush writes to `treeBlobKey(activeId)` instead of `activeTreeItem`. Same debounce, same coalescing, identical cost on the per-navigation write path.
4. **Reads unify.** `getFullStoredRecord(id)` works for the active id too because the blob lives in the same place. When `id === activeId` and `cachedTree` is dirty, serve from the in-memory cache; otherwise decode the blob. One code path for every "load tree by id" call.
5. **Migration.** One-shot on SW startup: if `activeTreeItem` exists, decode it, write to `treeBlobKey(activeId)`, ensure index entry, delete `activeTreeItem`. Idempotent — safe to re-run on every wake until the legacy key is gone.

**Branches that disappear after the refactor.**
- `if (active.id === treeId)` in `doPushTree`.
- The `isActive` fork in `DELETE_TREE`.
- The two paths in `stashActiveTree` / `takeStoredTree` (becomes "swap the `activeTreeIdItem` pointer").
- The active-vs-stored branch we just added to `EXPORT_TREE`.
- The "active tree isn't in the index" assumption scattered across snapshot builders, switcher UI, and sync-engine code.

**Risk.**
- Hot-path regression if the flush key swap is done wrong. Validate with `bench:sidepanel-cold-load` and a per-navigation write-latency probe before/after.
- Migration races at SW startup. Run migration under the existing `withTreeLock` and gate every read of `activeTreeItem` behind a "legacy fallback" until the migration has been observed to complete at least once.
- Index growth: the active tree now always has an entry. Tree-list UI already filters by stub-ness; verify it doesn't double-count.

**Out of scope.**
- Compression format changes. Keep `encodeTree` / `decodeTree` as-is.
- Sync protocol changes. The server has no idea which tree is "active" today and that stays true.
- UI changes. The switcher already treats the active tree as just another row by id.

**Definition of done.**
- [ ] `activeTreeItem` is removed from `storage-items.ts`; only the migration reads it.
- [ ] No call site in `extension/src/background/` branches on `active.id === treeId` for storage-routing purposes.
- [ ] `stashActiveTree` and `takeStoredTree` are deleted or reduced to pointer swaps.
- [ ] `getFullStoredRecord(activeId)` returns the live tree.
- [ ] Existing tests pass; add one new test that exports / shares / unloads the active tree by id without special-casing.
- [ ] Cold-load bench (`pnpm run bench:sidepanel-cold-load`) within noise of the pre-refactor baseline.

