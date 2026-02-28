# Trail

## What This Is

A browser extension + SaaS platform that visualizes browsing history as an interactive navigation tree. Users install the Chrome/Brave extension which records their browsing as a tree structure, viewable in the extension sidepanel (rendered with Pixi.js). A web dashboard at app.gettrail.net provides account management, settings, and cross-device sync. Marketing site at gettrail.net handles acquisition.

## Core Value

Users can see and understand their browsing patterns through a visual tree — making navigation history intuitive and useful instead of a flat, unsearchable list.

## Current Milestone: v1.1 Adultify

**Goal:** Harden Trail to production-grade quality — fix critical bugs, add CI/CD, polish UX error states.

**Target features:**
- Fix auth session persistence (critical user-reported bug)
- Fix sync race conditions and data integrity issues
- Add CI/CD pipelines (lint, test, typecheck)
- Add error pages, loading states, destructive action confirmations
- Remove production secrets from repo

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

### Active

<!-- Current scope. Building toward these. -->

- [ ] Production hardening (auth, sync, error handling)
- [ ] CI/CD pipeline improvements
- [ ] UX polish (error states, loading states, confirmations)

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
- Known critical bug: auth session persistence — service worker dies, token refresh timer lost
- Known data integrity issues: race conditions in sync, device ownership collisions
- CI/CD gaps: no lint/test in web CI, no typecheck in extension CI

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

---
*Last updated: 2026-02-28 after milestone v1.1 Adultify started*
