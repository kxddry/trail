# v1.0 Ship Plan — Trail Extension

> Started: 2026-04-16
> Mode: Autopilot. Aggressive scope per user decision.
> Sync strategy: LWW + Obsidian-style visible conflict resolution (not CRDT).
> Observability: Sentry free + PostHog free.

---

## 🔧 Velocipede Audit (2026-04-17) — Reinvented wheels → installed libs

Audit across UI, hooks/utils, animations, state/messaging. Grouped by risk.
**Status:** All non-dropped items shipped. 4 commits: `ded834ba` + `b4d397c1` (shadcn + small wins), `4a2f614a` (tabs/react-query/next-themes/WXT/command-state), plus a final L3/L4/L8 batch. Typecheck clean, tests green.

### Safe wins (small, obvious, no risk)

- [x] S1. `Icons.Loader2 animate-spin` → `<Spinner />` — `TreeDropdown.tsx:306,664`, `OnboardingWizard.tsx:281`
- [x] S2. Raw `<span>pin</span>` → `<Badge>` — `TrailNode.tsx:141`
- [x] S3. Dead `transition-all duration-200` w/ no state change — remove from `FloatingControls.tsx:57`
- [x] S4. Redundant `requestAnimationFrame` wrappers around ReactFlow APIs — remove in `TrailGraph.tsx:126,134`
- [x] S5. Local `formatRelativeTime` copy — import shared one in `SyncConflictBanner.tsx:74-83`
- [x] S6. Dead `uuid()` `Math.random` fallback — use `crypto.randomUUID()` in `observability.ts:71-81`
- [x] S7. Empty `src/shared/utils/debounce.ts` — shared util with cancel/flush, used in `commands.ts`
- [x] S8. "Loading..." text in `SettingsApp.tsx:50` → `<Skeleton>`
- [x] S9. ContextMenu section label — already migrated to `DropdownMenuLabel` before audit, no-op

### Medium wins (clear replacements, moderate effort)

- [x] M1. `formatTime()` + `formatRelativeTime()` → `date-fns` `formatDistanceToNow`/`isToday`/`isYesterday`
- [x] M2. `withTimeout` in `useBootstrap.ts` → native `Promise.race`
- [x] M3. Per-query `retry: 1` for bootstrap reads (replaces manual retry loop in useBootstrap)
- [x] M4. `useSettings` → `useQuery` + optimistic `useMutation`
- [x] M5. `useTrees` → `useQuery` + `useMutation` + `invalidateQueries`
- [x] M6. ScrollArea in ContextMenu — already in place, no-op
- [x] M7. Custom dropdown scroll-lock — removed with M6

### Large (shipped)

- [x] L1. `ContextMenus.tsx` custom positioning — already migrated to shadcn `DropdownMenu` before audit, no-op
- [x] L2. `SettingsApp.tsx` `useState<Page>` nav → vertical shadcn `Tabs`
- [x] L3. `useBootstrap.ts` manual Promise.all+retry → `useQuery` tree (critical + deferred queries, auto-retry via react-query)
- [x] L4. `useShortcuts.ts` 370-line keydown switch → declarative `SHORTCUTS` table + tiny `matches()` dispatcher
- [x] L5. `useSystemThemeListener` + `apply-theme.ts` → `next-themes` ThemeProvider + `useThemeSync` bridge
- [x] L8. `tree-storage.ts` `normalizeXxx` → `zod` `safeParse` schemas (meta, index entry, legacy record)
- [x] L9. `useRuntimeMessages.ts` extra `getCommandState()` RPC → `commandState` on every `TreeUpdatedInput`
- [x] L10. `supabase.ts` `chromeStorageAdapter` raw `browser.storage.local` → WXT `storage.get/set/remove` with `local:sb_` prefix

### Dropped after review (kept for the record)

- ~~L6. trail-logo `@keyframes` → motion~~ — native CSS keyframes are the idiomatic choice for a mount-only logo; motion would add bundle for no benefit.
- ~~L7. setTimeout state resets → AnimatePresence~~ — 650ms checkmark flash / 2s "Copied!" label are idiomatic transient React flags, not mount/unmount concerns.

### Deferred (do not touch)

- D1. `auth-orchestrator.ts` pub-sub pattern — cross-context, load-bearing; refactor only with specific need
- D2. `register-proxy-services.ts` RPC dispatch — transport core, works, skip
- D3. `tree-storage.ts` in-memory loading-promise deduplication — service-worker-specific, not a wheel
- D4. `src/shared/lib/uuid.ts` intentional UUIDv7 (time-ordered DB keys) — keep
- D5. `useIsMobile` — standard shadcn boilerplate; leave

---

## Wave 1 — Bug triage & hygiene (ship-blockers)

- [ ] Version sync: `package.json` 0.9.1 → 1.0.0 to match `wxt.config.ts`
- [ ] Remove ghost `src/features/graph/elk-graph.ts` from tsconfig (file doesn't exist, typecheck fails)
- [ ] Fix shadcn component typecheck errors (`calendar`, `context-menu`, `dropdown-menu`, `menubar`, `slider`, `sonner`, `spinner`)
- [ ] Remove dead deps: `elkjs` (removed from src), `motion` (will re-add after use), audit `@tanstack/react-virtual`
- [ ] Fix `FloatingControls.tsx:15` — unused `_searchInputRef` blocking ⌘K
- [ ] Fix `OnboardingHints.tsx:11` — `#searchBtn` DOM selector points at non-existent element
- [ ] Fix `nav-tree.ts:68` — implement or remove `setRoot` stub
- [ ] Fix `nav-tree.ts:196` — remove contradictory "remove deleteNode" comment
- [ ] Fix `Header.tsx:19` — wire `syncIndicator` to real store state
- [ ] Fix `navigation-handler.ts:107` — honor tab.pinned on new node
- [ ] Fix `commands.ts:87` — `slice(0, 0)` → `[]` for redo invalidation clarity
- [ ] Fix `tab-lru.ts:48` — verify `latestTabId` reset semantics on tab close

## Wave 2 — Dev hygiene & CI/CD

- [ ] Add Husky + lint-staged with pre-commit: `typecheck --changed` + `lint --fix` + `prettier --write`
- [ ] Add `.github/workflows/ci.yml`: lint + typecheck + test + build on PR and main
- [ ] Add `.github/workflows/release.yml`: build .zip on tag push, upload artifact
- [ ] Add `CHANGELOG.md` + `changesets` tooling
- [ ] Replace custom test runner with Vitest (consistency with ecosystem)
- [ ] Add `README.md` (user-facing: what is Trail, install, features)
- [ ] Add `ARCHITECTURE.md` (transport, state, storage, rendering, sync)
- [ ] Add `CONTRIBUTING.md` (setup, commit conventions, testing, PR flow)
- [ ] Update `CSP-RATIONALE.md` (remove stale PixiJS mention)
- [ ] Remove committed `graphify-out/` from repo, add to `.gitignore`

## Wave 3 — Observability

- [ ] Integrate `@sentry/browser` in sidepanel + background + settings; DSN via env var
- [ ] Integrate `posthog-js` for analytics; project key via env var
- [ ] Define analytics event schema (install, onboarding_started/completed, first_tree_created, node_created/deleted, search_used, sync_ok/failed, auth_login/logout, settings_opened, feedback_submitted)
- [ ] Wire global error boundary → Sentry
- [ ] Add error boundary for settings page entrypoint
- [ ] PII masking in Sentry config (URLs, titles stripped from events)
- [ ] Opt-out toggle in settings (respect privacy-first default)

## Wave 4 — Command palette & core UX

- [ ] Wire `cmdk` via `<CommandDialog>`: search nodes, recent trees, actions (new tree, rename, delete, open settings, help)
- [ ] Replace placeholder search input with Command palette overlay on ⌘K / ⌘F / /
- [ ] Add inline node rename RPC (`RENAME_NODE`) + UI (double-click title, Enter to commit, Esc cancel)
- [ ] Add empty states: zero trees, empty tree (first-node CTA), zero search results, offline banner
- [ ] Add feedback button in header menu → opens dialog with "bug/feature/other" → posts to GitHub or mailto
- [ ] Keyboard shortcuts cheat-sheet (⌘/) with full list, not just the implemented ones
- [ ] Node context menu: edit title, edit URL, copy link, duplicate, open in new tab, pin, delete (consolidate existing menus)

## Wave 5 — Onboarding wizard

- [ ] Multi-step onboarding: welcome → explain concept → permissions priming → create first tree (interactive) → demo tree explore → done
- [ ] Replace tooltip-based `OnboardingHints` with proper wizard (stored `trail_onboarding` flag)
- [ ] Demo tree preset: "Research: How Chrome Extensions Work" (preloaded tree with ~20 interesting nodes)
- [ ] Permissions priming screen: explain webNavigation + tabs BEFORE chrome asks
- [ ] Skip button on every step, progress indicator

## Wave 6 — Settings overhaul

- [ ] Account page (profile, sign in/out, subscription status placeholder)
- [ ] Data page (export JSON, export Markdown, import, clear local data, delete account w/ confirmation)
- [ ] Shortcuts page (view all, future: customize)
- [ ] Privacy page (policy link, terms link, telemetry opt-out, encryption toggle when implemented)
- [ ] About page (version, changelog link, credits, report bug, suggest feature)
- [ ] Replace existing flat nav with shadcn Sidebar + nested pages
- [ ] Keep existing Appearance + Behavior + Trees pages, reorganize under new structure

## Wave 7 — Theme system

- [ ] Audit: default to `system` preference, not forced light/dark
- [ ] Remove FOUC: inject theme script in `<head>` before bundle (synchronous)
- [ ] Verify all shadcn components respect `data-theme` attribute
- [ ] Settings → Appearance → Theme picker: Light / Dark / System
- [ ] Persist via `chrome.storage.local` + reflect across all surfaces (sidepanel, settings, future popup)

## Wave 8 — Auth & sync foundations

- [ ] `@supabase/supabase-js` client factory for extension (SUPABASE_URL + ANON_KEY from env)
- [ ] `chrome.identity.launchWebAuthFlow` + PKCE auth flow → Google OAuth via Supabase
- [ ] Session persistence in `chrome.storage.local` (trail_auth_session per existing schema)
- [ ] Background auth orchestrator: refresh token on wake, broadcast auth state to sidepanel
- [ ] Sync engine skeleton: subscribe to local tree mutations, debounced push to server
- [ ] LWW reconciliation: server returns (id, updated_at, body_checksum); local picks newer by updated_at
- [ ] Visible conflict UI: banner "This tree was updated on another device" with "Keep mine / Use server / Review side-by-side" buttons
- [ ] Side-by-side diff viewer for conflict review

## Wave 9 — Migrations, offline, rate limiting

- [ ] Local schema versioning: `trail_schema_version` storage key, migration runner on background wake
- [ ] Initial v1 migration (baseline) so future changes are trackable
- [ ] Offline queue: pending ops array in `chrome.storage.local`, drain on online event
- [ ] Sync debounce: batch tree updates at 2s, flush immediately on tab close
- [ ] Rate limiting: at most 10 sync requests / 30s window, retry with exponential backoff
- [ ] Service worker keep-alive strategy: alarms API for periodic sync checks

## Wave 10 — Tests

- [ ] Migrate from custom `tests/*.test.ts` runner to Vitest
- [ ] Add React Testing Library for component tests
- [ ] Add Playwright MV3 runner (loads unpacked extension)
- [ ] E2E suite: install → onboard → create tree → edit node → search → open settings → export
- [ ] E2E suite: sign in flow (with supabase test project), create tree, switch device, see sync
- [ ] E2E suite: conflict resolution (mutate same tree on two client instances)
- [ ] Unit: sync engine, conflict resolver, migration runner, LWW comparator

## Wave 11 — Animations

- [ ] Integrate `motion` (already in deps, unused) or `framer-motion`
- [ ] Animate: Command palette open/close, settings page transitions, onboarding step advance, node add/remove in graph, sync banner slide-in, toast stack
- [ ] Keep instant: selection indicator, theme switch (per user feedback), hover states
- [ ] Reduce-motion respect via `prefers-reduced-motion` media query

## Wave 12 — Polish & scaffolds

- [ ] i18n scaffold via `chrome.i18n`: create `_locales/en/messages.json`, extract hardcoded strings
- [ ] i18n second language: `_locales/ru/messages.json` (user is RU; ship bilingual)
- [ ] Accessibility audit: focus rings on all interactive elements, `aria-label` on icon-only buttons, keyboard nav in Command palette, Escape to close dialogs, sensible tab order
- [ ] Storybook setup (`@storybook/react-vite`): stories for core UI components
- [ ] Changelog auto-gen from commit messages via `changesets`

## Wave 13 — Performance

- [ ] Profile baseline: React DevTools Profiler + Chrome Performance on 3100-node tree
- [ ] Offload d3-hierarchy layout to Web Worker (or keep in background service worker since it's already there)
- [ ] Virtualize tree list in Trees settings page (`@tanstack/react-virtual`)
- [ ] Virtualize pinned dropdown if >50 items
- [ ] Connect `adaptivePerformance` flag to actual graph render path (currently disconnected)
- [ ] Incremental layout cache: invalidate only affected subtree on node add, not full recompute

## Wave 14 — Release prep

- [ ] Permissions audit: verify minimal set, write per-permission justification to store listing
- [ ] CSP tightening: verify no `unsafe-eval`, no `unsafe-inline` in built manifest
- [ ] Sensitive URL blocklist: default skip `chrome-extension://`, `devtools://`, `localhost`, `127.0.0.1`; user-configurable
- [ ] Client-side encryption (AES-GCM with user-derived key) for sync payload — behind feature flag
- [ ] Store listing: 5 screenshots (captured via Playwright on demo tree), 1 promo tile (440x280), description with keywords
- [ ] Privacy policy page at `gettrail.net/privacy` (content already drafted in repo root)
- [ ] Terms page at `gettrail.net/terms` (content already drafted in repo root)
- [ ] Beta channel: separate Web Store listing `trail-beta` with pre-release builds
- [ ] `CHANGELOG.md` v1.0.0 entry

## Deferred (v1.1+)

Nothing — user chose Aggressive scope. Items that won't fit in this session will stay in this plan with status.

---

## Session log

### 2026-04-16 — Session kickoff

- Audit completed; transport migration (prev todo) confirmed shipped.
- User interview: Aggressive scope, LWW+conflict UI, Sentry+PostHog free, hosted Supabase exists (org `trail`, project likely `prod` which is paused or `dev` which wasn't linkable — will proceed with env placeholders).
- Kicking off Wave 1.
