# Trail - Adultify: Production-Grade Product

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
