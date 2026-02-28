# Roadmap: Trail

## Milestones

- ✅ **v1.0 Initial Build** - Pre-GSD (shipped)
- 🚧 **v1.1 Adultify** - Phases 1-3 (in progress)

## Overview

v1.1 Adultify hardens Trail from a working prototype to a production-grade product. Auth/security requirements (AUTH-01–04) were already satisfied in the codebase; the remaining auth cleanup (AUTH-05) is folded into Phase 1 alongside data integrity work. Then CI/CD automation, and finally UX polish.

## Phases

- [x] **Phase 1: Data Integrity & Auth Cleanup** - Remove auth bypass, wrap sync in transactions, fix ownership collisions, add retry limits (completed 2026-02-28)
- [ ] **Phase 2: CI/CD** - Add lint/test/typecheck to pipelines, configure Dependabot, automate extension releases
- [ ] **Phase 3: UX Polish** - Add branded error pages, loading states, destructive action confirmations, accessibility

## Phase Details

### Phase 1: Data Integrity & Auth Cleanup
**Goal**: Trail data is written atomically, device ownership conflicts are handled correctly, and auth bypass is fully removed
**Depends on**: Nothing (first phase)
**Requirements**: AUTH-05, DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, DATA-06
**Success Criteria** (what must be TRUE):
  1. ACCOUNT_AUTH_BYPASS is completely removed — env variable, function, middleware check, all references gone
  2. Concurrent trail upserts complete without partial writes — operations are wrapped in database transactions
  3. Importing a trail on a device that belongs to a different user correctly updates the device ownership rather than silently no-op'ing
  4. A device claimed by user A cannot be silently reassigned to user B during sync — the conflict is rejected and surfaced
  5. Webhook processing is atomic — a failure mid-handler does not leave the database in a partial state
  6. A sync loop that keeps failing terminates after a bounded number of retries rather than running forever
  7. Navigation errors are written to logs so developers can diagnose failures
**Plans**: 2 plans
Plans:
- [x] 01-01-PLAN.md — Remove ACCOUNT_AUTH_BYPASS mechanism entirely (AUTH-05)
- [x] 01-02-PLAN.md — Add logging for device reassignment and nav errors; verify pre-existing data integrity (DATA-01–06)

### Phase 2: CI/CD
**Goal**: Every pull request is automatically validated and dependency vulnerabilities are surfaced without manual effort
**Depends on**: Nothing
**Requirements**: CICD-01, CICD-02, CICD-03, CICD-04, CICD-05, CICD-06, CICD-07
**Success Criteria** (what must be TRUE):
  1. Opening a PR against the web apps triggers lint and tests in CI — a failing lint or test blocks merge
  2. Opening a PR against the extension triggers typecheck in CI — a type error blocks merge
  3. Dependabot opens automated PRs for dependency updates across all workspaces
  4. New PRs are pre-populated with a template that prompts contributors for required information
  5. A weekly scheduled job scans all dependencies and reports known vulnerabilities
  6. PRs are automatically labeled by area (extension, web, packages, CI) without manual tagging
  7. Merging an extension release commit triggers automated publishing to the Chrome Web Store
**Plans**: TBD

### Phase 3: UX Polish
**Goal**: Users encounter branded, helpful UI for every error and loading state instead of raw Next.js defaults or blank screens
**Depends on**: Nothing
**Requirements**: UX-01, UX-02, UX-03, UX-04, UX-05, UX-06, UX-07
**Success Criteria** (what must be TRUE):
  1. Navigating to a URL that throws a server error shows a Trail-branded error page, not the Next.js default
  2. Navigating to a URL that does not exist shows a Trail-branded 404 page, not the Next.js default
  3. The app root displays a proper loading component while hydrating instead of plain "loading" text
  4. Clicking a destructive action in the extension context menu presents a confirmation dialog before executing
  5. The /trails and /settings pages show skeleton or spinner states while their data loads
  6. Extension context menu items expose correct ARIA roles so screen readers announce them properly
  7. Navigating between app routes plays a smooth transition animation
**Plans**: 3 plans
Plans:
- [x] 03-01-PLAN.md — Brand error pages with TrailLogo and polish loading states (UX-01, UX-02, UX-03, UX-05)
- [x] 03-02-PLAN.md — Add destructive action confirmations and ARIA roles to extension context menus (UX-04, UX-06)
- [ ] 03-03-PLAN.md — Add route transition animations with Motion library (UX-07)

## Progress

**Execution Order:** 1 → 2 → 3

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Data Integrity & Auth Cleanup | 2/2 | Complete   | 2026-02-28 | - |
| 2. CI/CD | v1.1 | 0/TBD | Not started | - |
| 3. UX Polish | 2/3 | In Progress | 2026-02-28 | - |
