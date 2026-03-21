# Roadmap: Trail

## Milestones

- ✅ **v1.0 Initial Build** - Pre-GSD (shipped)
- ✅ **v1.1 Adultify** - Phases 1-4 (shipped 2026-03-19)
- ✅ **Post-v1.1** - Phase 01 (budgeted rich-content restoration)
- 🚧 **v1.2 Release Readiness** - Phases 2-8 (in progress)

## Phases

<details>
<summary>✅ v1.0 Initial Build — SHIPPED (pre-GSD)</summary>

Pre-GSD milestone. Extension core, tree visualization, auth, sync, dashboard, marketing site, CMS, video generation.

</details>

<details>
<summary>✅ v1.1 Adultify (Phases 1-4) — SHIPPED 2026-03-19</summary>

- [x] Phase 1: Data Integrity & Auth Cleanup (2/2 plans) — completed 2026-02-28
- [x] Phase 2: CI/CD (1/1 plans) — completed 2026-02-28
- [x] Phase 3: UX Polish (3/3 plans) — completed 2026-02-28
- [x] Phase 4: Graph Startup Optimization (3/3 plans) — completed 2026-03-19

Full details: [milestones/v1.1-ROADMAP.md](milestones/v1.1-ROADMAP.md)

</details>

<details>
<summary>✅ Post-v1.1 — Phase 01 (budgeted rich-content restoration)</summary>

- [x] Phase 01: Budgeted Rich-Content Restoration After Pan/Zoom (3/3 plans)

</details>

### 🚧 v1.2 Release Readiness (Phases 2-8)

**Milestone Goal:** Harden Trail extension for first public Chrome Web Store 1.0.0 release.

- [x] **Phase 2: Hygiene & Dead Code Cleanup** - Remove dead code, enforce artifact cleanliness, audit orphaned surfaces — completed 2026-03-20
- [ ] **Phase 3: Error Handling & Recovery** - Unified error layer, graceful degradation on every failure path
- [ ] **Phase 4: Stability & Concurrency** - Eliminate races, double-submits, and stale state across all surfaces
- [ ] **Phase 5: UX Polish** - Consistent interaction patterns, better information density, onboarding hints
- [ ] **Phase 6: Security & Privacy Audit** - Manifest lockdown, structured logging, payload redaction, protocol hardening
- [ ] **Phase 7: Performance Budgets** - Measurable performance targets, adaptive degradation, skeleton loading
- [ ] **Phase 8: QA & Release Discipline** - Smoke tests, interaction tests, release checklist, profile testing

## Phase Details

### Phase 2: Hygiene & Dead Code Cleanup
**Goal**: Every file in the codebase is either wired and working or removed; no orphaned artifacts ship in the release
**Depends on**: Phase 01 (post-v1.1)
**Requirements**: HYG-01, HYG-02, SEC-06, QA-04, QA-06
**Success Criteria** (what must be TRUE):
  1. No `logs/` directory or stale dev artifacts exist in the package root, and a CI test enforces this
  2. AuthGate/WelcomeGate components are either visibly active in the sidepanel flow or deleted from source
  3. emitRuntimeLog is either called on critical failure paths or removed entirely
  4. A dead code audit has been completed and orphaned UX surfaces are removed or wired in
**Plans:** 2 plans

Plans:
- [x] 02-01-PLAN.md — Delete dead code (AuthGate, WelcomeGate, runtime-logger)
- [x] 02-02-PLAN.md — Remove logs/ artifacts, harden hygiene test, dead code audit

### Phase 3: Error Handling & Recovery
**Goal**: Every failure the user can encounter produces a clear, actionable UI state instead of a broken or half-mounted screen
**Depends on**: Phase 2
**Requirements**: HYG-03, HYG-05, HYG-06, STAB-01, STAB-04, STAB-05, STAB-07, STAB-09
**Success Criteria** (what must be TRUE):
  1. Errors from rename, export, open, sync, and auth operations surface as toast or banner notifications
  2. ErrorBoundary crash screen offers "Copy diagnostics" and "Reload in safe mode" actions
  3. Bootstrap critical-fetch failure shows a degraded-but-usable state with retry, not a blank or half-mounted panel
  4. Corrupted localStorage or layout cache auto-resets with a toast explaining what happened
  5. Quota eviction and stub archives show user-visible explanations of what happened and what to do
**Plans:** 3 plans

Plans:
- [x] 03-01-PLAN.md — Unified error-to-toast layer with showOperationError helper
- [x] 03-02-PLAN.md — ErrorBoundary crash diagnostics and bootstrap recovery
- [ ] 03-03-PLAN.md — Cache corruption recovery, offscreen fallback, quota eviction notice

### Phase 4: Stability & Concurrency
**Goal**: Rapid user actions (quick open/close, double-clicks, panel restarts) never produce duplicate requests, stale UI, or silent auth failures
**Depends on**: Phase 3
**Requirements**: STAB-02, STAB-03, STAB-06, STAB-08, HYG-04
**Success Criteria** (what must be TRUE):
  1. Opening and closing the sidepanel rapidly does not produce duplicate auth/bootstrap/search requests
  2. Double-clicking any mutating button (create tree, rename, export, auth submit) produces exactly one operation
  3. SESSION_EXPIRED is handled in spotlight and newtab surfaces, not just the account flow
  4. editorMode state survives panel close and service worker restart
  5. A sync status indicator (syncing / offline / degraded / error) is visible in the sidepanel
**Plans**: TBD

### Phase 5: UX Polish
**Goal**: Extension interactions feel consistent and self-documenting: every dropdown, modal, search box, and onboarding surface behaves predictably
**Depends on**: Phase 4
**Requirements**: UXP-01, UXP-02, UXP-03, UXP-04, UXP-05, UXP-06, UXP-07, UXP-08, UXP-09, UXP-10
**Success Criteria** (what must be TRUE):
  1. All dropdowns and modals dismiss on Esc and click-outside, return focus to trigger, and apply inert to background
  2. Sidepanel search shows keyboard shortcut hints inline and preserves draft text on accidental blur
  3. TreeDropdown shows last synced time, node count, and archived/stub status for each tree
  4. First-run experience shows micro-hints for key gestures, and settings includes a "Privacy & data" section
  5. Destructive action confirmations state what will be lost and how to recover
**Plans**: TBD

### Phase 6: Security & Privacy Audit
**Goal**: Extension manifest, logging, and cross-boundary communication are locked down for public Chrome Web Store submission
**Depends on**: Phase 4
**Requirements**: SEC-01, SEC-02, SEC-03, SEC-04, SEC-05, SEC-07, SEC-08, SEC-09
**Success Criteria** (what must be TRUE):
  1. Manifest contains only permissions the extension actually uses; chrome.scripting and browser.search are removed if unused
  2. Dev-only domains are confirmed excluded from release builds
  3. Structured logger replaces raw console.* on auth/sync/storage/search paths, with URL/title/token redaction
  4. Protocol messages between site and extension validate payloads beyond envelope level
  5. CSP requirement for pixi.js/unsafe-eval is documented with rationale for CWS reviewers
**Plans**: TBD

### Phase 7: Performance Budgets
**Goal**: Extension has measurable, enforced performance targets and degrades gracefully on constrained devices
**Depends on**: Phase 5, Phase 6
**Requirements**: PERF-01, PERF-02, PERF-03, PERF-04, PERF-05
**Success Criteria** (what must be TRUE):
  1. Three budget metrics are tracked in telemetry: first sidepanel paint, first graph interactive, spotlight query latency
  2. Blur/LOD/animation quality degrades automatically on weak machines and large trees
  3. Long lists (trees, tags, search results) use virtualization or chunked rendering when item count exceeds threshold
  4. Loading states show skeleton placeholders instead of empty canvas or null suspense fallback
**Plans**: TBD

### Phase 8: QA & Release Discipline
**Goal**: A repeatable release process exists that catches regressions before Chrome Web Store submission
**Depends on**: Phase 7
**Requirements**: QA-01, QA-02, QA-03, QA-05
**Success Criteria** (what must be TRUE):
  1. Smoke e2e tests pass for all 8 scenarios: first install, guest mode, auth, session expired, sync fail, tree switch, export/import, quota eviction
  2. UI interaction tests cover dropdown keyboard nav, modal escape, search navigation, and auth banner behavior
  3. A release checklist document covers permissions, offline mode, empty states, corrupted cache, and worker restart
  4. Cold profile (first install) and dirty returning user (existing data) are tested as separate paths
**Plans**: TBD

## Progress

**Execution Order:** Phases 2-8 execute sequentially. Phase 6 can run in parallel with Phase 5 (no dependency between them). Phase 7 depends on both 5 and 6.

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Data Integrity & Auth Cleanup | v1.1 | 2/2 | Complete | 2026-02-28 |
| 2. CI/CD | v1.1 | 1/1 | Complete | 2026-02-28 |
| 3. UX Polish | v1.1 | 3/3 | Complete | 2026-02-28 |
| 4. Graph Startup Optimization | v1.1 | 3/3 | Complete | 2026-03-19 |
| 01. Budgeted Rich-Content Restoration | post-v1.1 | 3/3 | Complete | 2026-03-20 |
| 2. Hygiene & Dead Code Cleanup | v1.2 | 2/2 | Complete | 2026-03-20 |
| 3. Error Handling & Recovery | v1.2 | 0/3 | Planned | - |
| 4. Stability & Concurrency | v1.2 | 0/? | Not started | - |
| 5. UX Polish | v1.2 | 0/? | Not started | - |
| 6. Security & Privacy Audit | v1.2 | 0/? | Not started | - |
| 7. Performance Budgets | v1.2 | 0/? | Not started | - |
| 8. QA & Release Discipline | v1.2 | 0/? | Not started | - |
