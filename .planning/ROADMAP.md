# Roadmap: Trail

## Milestones

- ✅ **v1.0 Initial Build** - Pre-GSD (shipped)
- 🚧 **v1.1 Adultify** - Phases 1-4 (in progress)

## Overview

v1.1 Adultify hardens Trail from a working prototype to a production-grade product. The work falls into four natural delivery boundaries: fixing the auth/security surface first, then correcting data integrity in the API, then wiring up CI/CD automation, and finally polishing the user-facing error states and loading experiences.

## Phases

- [ ] **Phase 1: Security & Auth** - Fix session persistence, remove secrets, eliminate auth code duplication
- [ ] **Phase 2: Data Integrity** - Wrap sync operations in transactions, fix ownership collisions, add retry limits
- [ ] **Phase 3: CI/CD** - Add lint/test/typecheck to pipelines, configure Dependabot, automate extension releases
- [ ] **Phase 4: UX Polish** - Add branded error pages, loading states, destructive action confirmations, accessibility

## Phase Details

### Phase 1: Security & Auth
**Goal**: Users stay logged in reliably and production secrets are no longer in the repository
**Depends on**: Nothing (first phase)
**Requirements**: AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05
**Success Criteria** (what must be TRUE):
  1. User remains logged in after their laptop sleeps and wakes, with the extension maintaining the session via chrome.alarms
  2. User sees a clear "session expired" message with a re-login button instead of silent logout when token refresh fails
  3. Production environment files (.env.prod, .env.e2e) are absent from git history tracking and protected by .gitignore
  4. The auth storage key is defined once and referenced everywhere — no scattered string duplicates
  5. Building for production fails or strips the ACCOUNT_AUTH_BYPASS flag so it cannot reach production
**Plans**: TBD

### Phase 2: Data Integrity
**Goal**: Trail data is written atomically and device ownership conflicts are handled correctly instead of silently
**Depends on**: Phase 1
**Requirements**: DATA-01, DATA-02, DATA-03, DATA-04, DATA-05, DATA-06
**Success Criteria** (what must be TRUE):
  1. Concurrent trail upserts complete without partial writes — operations are wrapped in database transactions
  2. Importing a trail on a device that belongs to a different user correctly updates the device ownership rather than silently no-op'ing
  3. A device claimed by user A cannot be silently reassigned to user B during sync — the conflict is rejected and surfaced
  4. Webhook processing is atomic — a failure mid-handler does not leave the database in a partial state
  5. A sync loop that keeps failing terminates after a bounded number of retries rather than running forever
  6. Navigation errors are written to logs so developers can diagnose failures
**Plans**: TBD

### Phase 3: CI/CD
**Goal**: Every pull request is automatically validated and dependency vulnerabilities are surfaced without manual effort
**Depends on**: Phase 1
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

### Phase 4: UX Polish
**Goal**: Users encounter branded, helpful UI for every error and loading state instead of raw Next.js defaults or blank screens
**Depends on**: Phase 1
**Requirements**: UX-01, UX-02, UX-03, UX-04, UX-05, UX-06, UX-07
**Success Criteria** (what must be TRUE):
  1. Navigating to a URL that throws a server error shows a Trail-branded error page, not the Next.js default
  2. Navigating to a URL that does not exist shows a Trail-branded 404 page, not the Next.js default
  3. The app root displays a proper loading component while hydrating instead of plain "loading" text
  4. Clicking a destructive action in the extension context menu presents a confirmation dialog before executing
  5. The /trails and /settings pages show skeleton or spinner states while their data loads
  6. Extension context menu items expose correct ARIA roles so screen readers announce them properly
  7. Navigating between app routes plays a smooth transition animation
**Plans**: TBD

## Progress

**Execution Order:** 1 → 2 → 3 → 4

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Security & Auth | v1.1 | 0/TBD | Not started | - |
| 2. Data Integrity | v1.1 | 0/TBD | Not started | - |
| 3. CI/CD | v1.1 | 0/TBD | Not started | - |
| 4. UX Polish | v1.1 | 0/TBD | Not started | - |
