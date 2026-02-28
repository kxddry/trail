# Requirements: Trail

**Defined:** 2026-02-28
**Core Value:** Users can see and understand their browsing patterns through a visual tree

## v1.1 Requirements

Requirements for Adultify milestone. Each maps to roadmap phases.

### Security & Auth

- [x] **AUTH-01**: User session persists across browser sleep — extension uses chrome.alarms for proactive token refresh instead of setTimeout *(already implemented)*
- [x] **AUTH-02**: User sees "session expired" UI with re-login option instead of silent logout when token cannot be refreshed *(already implemented)*
- [x] **AUTH-03**: Production secrets (.env.prod, .env.e2e) are removed from git tracking and added to .gitignore *(already protected)*
- [x] **AUTH-04**: Auth storage key is a single shared constant instead of 6 duplicate string literals *(already centralized in storage-keys.ts)*
- [x] **AUTH-05**: ACCOUNT_AUTH_BYPASS is completely removed from the codebase — env variable, function, middleware check, all references

### Data Integrity

- [x] **DATA-01**: Trail upsert operations are wrapped in a database transaction to prevent race conditions *(pre-existing, verified 2026-02-28)*
- [x] **DATA-02**: Import endpoint correctly updates device userId on ownership collision instead of no-op *(pre-existing, verified 2026-02-28)*
- [x] **DATA-03**: Device sync logs device ownership reassignment when a device appears under a different user *(logging added 2026-02-28)*
- [x] **DATA-04**: Webhook handler uses database transaction for atomic processing *(pre-existing, verified 2026-02-28)*
- [x] **DATA-05**: Sync engine has a retry limit to prevent infinite retry loops *(pre-existing 6-step backoff, verified 2026-02-28)*
- [x] **DATA-06**: Navigation handler logs errors instead of silently swallowing them *(logging added 2026-02-28)*

### CI/CD

- [x] **CICD-01**: Web CI pipeline (ci-web.yml) runs lint and tests on pull requests
- [x] **CICD-02**: Extension CI pipeline (ci-extension.yml) runs typecheck on pull requests
- [x] **CICD-03**: Dependabot is configured for automated vulnerability scanning across all workspaces
- [x] **CICD-04**: PR template guides contributors through required information and checks
- [x] **CICD-05**: Scheduled security audit workflow scans dependencies for known vulnerabilities
- [x] **CICD-06**: PR auto-labeler categorizes changes by area (extension, web, packages, CI)
- [x] **CICD-07**: Extension release workflow automates Chrome Web Store publishing

### UX Polish

- [ ] **UX-01**: App displays branded error page (error.tsx) instead of default Next.js error
- [ ] **UX-02**: App displays branded not-found page (not-found.tsx) instead of default
- [ ] **UX-03**: Root loading state shows proper loading component instead of plain "loading" text
- [ ] **UX-04**: Destructive actions in extension context menu require user confirmation before executing
- [ ] **UX-05**: /trails and /settings pages show loading states while data loads
- [ ] **UX-06**: Extension context menus include proper ARIA roles for accessibility
- [ ] **UX-07**: Web app has page transition animations between routes

## Future Requirements

Deferred to v1.2+. Tracked but not in current roadmap.

### Hardening

- **HARD-01**: Rate limiting on API endpoints
- **HARD-02**: Refresh token replay detection

### UX

- **FUX-01**: Focus trapping in modals
- **FUX-02**: Button system unification across apps
- **FUX-03**: Icon system unification across apps
- **FUX-04**: Empty state improvements for list views
- **FUX-05**: Toast notification system in web app

## Out of Scope

| Feature | Reason |
|---------|--------|
| Mobile app | Web-first approach, mobile later |
| Real-time collaboration | Single-user product |
| Git history scrubbing for secrets | User must rotate secrets separately; .gitignore prevents future commits |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| AUTH-01 | — | Complete (pre-existing) |
| AUTH-02 | — | Complete (pre-existing) |
| AUTH-03 | — | Complete (pre-existing) |
| AUTH-04 | — | Complete (pre-existing) |
| AUTH-05 | Phase 1 | Complete |
| DATA-01 | Phase 1 | Complete |
| DATA-02 | Phase 1 | Complete |
| DATA-03 | Phase 1 | Complete |
| DATA-04 | Phase 1 | Complete |
| DATA-05 | Phase 1 | Complete |
| DATA-06 | Phase 1 | Complete |
| CICD-01 | Phase 2 | Complete |
| CICD-02 | Phase 2 | Complete |
| CICD-03 | Phase 2 | Complete |
| CICD-04 | Phase 2 | Complete |
| CICD-05 | Phase 2 | Complete |
| CICD-06 | Phase 2 | Complete |
| CICD-07 | Phase 2 | Complete |
| UX-01 | Phase 3 | Pending |
| UX-02 | Phase 3 | Pending |
| UX-03 | Phase 3 | Pending |
| UX-04 | Phase 3 | Pending |
| UX-05 | Phase 3 | Pending |
| UX-06 | Phase 3 | Pending |
| UX-07 | Phase 3 | Pending |

**Coverage:**
- v1.1 requirements: 25 total (4 pre-existing, 21 active)
- Mapped to phases: 21
- Complete (pre-existing): 4
- Unmapped: 0 ✓

---
*Requirements defined: 2026-02-28*
*Last updated: 2026-02-28 after 01-02 executed — DATA-01 through DATA-06 all complete (verified or logging added)*
