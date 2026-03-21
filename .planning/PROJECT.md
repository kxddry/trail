# Trail

## What This Is

A browser extension + SaaS platform that visualizes browsing history as an interactive navigation tree. Users install the Chrome/Brave extension which records their browsing as a tree structure, viewable in the extension sidepanel, fullview, and Spotlight overlay (rendered with Pixi.js). A web dashboard at app.gettrail.net provides account management, settings, and cross-device sync. Marketing site at gettrail.net handles acquisition.

## Core Value

Users can see and understand their browsing patterns through a visual tree — making navigation history intuitive and useful instead of a flat, unsearchable list.

## Requirements

### Validated

<!-- Shipped and confirmed valuable. -->

- ✓ **EXT-CORE**: Extension records browsing history as tree structure — v1.0
- ✓ **EXT-VIZ**: Interactive tree visualization in sidepanel (Pixi.js) — v1.0
- ✓ **EXT-NAV**: Context menu actions for tree navigation — v1.0
- ✓ **AUTH**: User authentication via Better Auth (email/password, Google OAuth) — v1.0
- ✓ **SYNC**: Cross-device trail sync via account app API — v1.0
- ✓ **DASH**: Web dashboard with trail viewer and settings — v1.0
- ✓ **MKTG**: Marketing site with landing, pricing, legal pages — v1.0
- ✓ **CMS**: Sanity-powered content management — v1.0
- ✓ **VIDEO**: Remotion-based promotional video generation — v1.0
- ✓ **AUTH-05**: Auth bypass completely removed — v1.1
- ✓ **DATA-01–06**: Data integrity (transactions, device ownership logging, retry limits, nav error logging) — v1.1
- ✓ **CICD-01–07**: CI/CD pipeline (lint, test, typecheck, Dependabot, security audit, labeler, CWS release) — v1.1
- ✓ **UX-01–07**: UX polish (branded error/404/loading pages, destructive confirmations, ARIA roles, route transitions) — v1.1
- ✓ **PERF-01–06**: Graph startup optimization (bootstrap split, layout signature cache, settings-change recompute, startup instrumentation) — v1.1

### Active

<!-- Current scope. Building toward these. -->

## Current Milestone: v1.2 Release Readiness

**Goal:** Harden Trail extension for first public Chrome Web Store 1.0.0 release — fix failing tests, wire dead auth/onboarding code, unify error handling, add sync status, improve UI consistency, eliminate stability bugs, audit permissions/privacy, add performance budgets, and establish QA discipline.

**Target features:**
- Hygiene fixes (logs cleanup, auth gate wiring, unified error layer)
- UI consistency (dropdown/modal behavior, search UX, onboarding hints)
- Stability hardening (bootstrap recovery, dedup, double-submit prevention)
- Privacy & security (manifest audit, structured logging, redaction)
- Performance budgets (sidepanel paint, graph interactive, spotlight latency)
- QA foundation (smoke e2e, UI interaction tests, release checklist)

### Out of Scope

<!-- Explicit boundaries. Includes reasoning to prevent re-adding. -->

- Rate limiting on API endpoints — defer to future milestone
- Refresh token replay detection — defer to future milestone
- Mobile app — web-first approach, mobile later
- Real-time collaboration — single-user product

## Context

- Monorepo: `apps/` (marketing, account, video, support-bot), `packages/` (ui, content, db, trpc, config), `extension/`, `sanity/`
- Tech: Next.js 16, React 19, TypeScript, Tailwind CSS 4, WXT, Pixi.js, Better Auth, tRPC, Prisma, PostgreSQL
- Package manager: pnpm 10
- Production domains: gettrail.net (marketing), app.gettrail.net (account/API)
- v1.1 shipped: auth bypass removed, CI/CD automated, UX branded, graph startup optimized
- All known critical bugs from v1.0 resolved (auth persistence, sync race conditions, device ownership)

## Constraints

- **Extension runtime**: Chrome service workers die after ~30s idle — must use chrome.alarms, not setTimeout
- **Auth tokens**: 5-minute access token lifespan — proactive refresh is essential
- **Monorepo**: Changes must respect workspace boundaries (extension is separate pnpm workspace)
- **Deployment**: Vercel for web apps, Chrome Web Store for extension

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| WXT for extension framework | Modern, TypeScript-first, handles service worker lifecycle | ✓ Good |
| Better Auth over NextAuth | More flexible, better TypeScript support, self-hosted | ✓ Good |
| Pixi.js for tree visualization | WebGL performance for large trees, interactive canvas | ✓ Good |
| Monorepo with pnpm workspaces | Shared code across apps, single version control | ✓ Good |
| Separate extension workspace | Different build tooling, isolated dependencies | ✓ Good |
| Remove auth bypass entirely | Always use real auth in dev — no guard, no env var | ✓ Good (v1.1) |
| chrome.alarms for token refresh | Service workers die after 30s — setTimeout unreliable | ✓ Good (v1.1) |
| console.warn for device reassignment | Valid expected behavior, not error — needs audit visibility | ✓ Good (v1.1) |
| Bootstrap split critical/deferred | Graph surfaces render first frame without waiting on tags/trees/commands | ✓ Good (v1.1) |
| Layout signature in cache | Exact-match cache prevents stale positions after settings change | ✓ Good (v1.1) |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd:transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd:complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-03-20 after v1.2 Release Readiness milestone start*
