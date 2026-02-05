# Account App Rewrite Design

**Date:** 2026-02-01
**Project:** `apps/account` (app.gettrail.net)

## Context
The account app currently delivers core pages (dashboard, extension, settings, billing) with a lightweight shell. It already uses `@trail/ui` tokens, Auth0, and tRPC. The goal is a from-scratch UI rewrite that keeps routes and data contracts stable while making the product feel intentional, premium, and more legible. The rewrite also adds three product-facing pages to complete activation and access workflows: `/getting-started`, `/activity`, and `/sessions`.

## Assumptions (no questions requested)
- Keep all existing routes and server actions working (Auth0, tRPC, v1 routes).
- Focus on UI/UX and component architecture, not adding new backend features.
- Preserve the Trail brand's warm neutral palette and lowercase typographic voice.
- Avoid breaking extension or external clients that may still rely on `/v1` routes.

## Approaches Considered
1. **Minimal refresh**: adjust spacing and colors only. Low risk, but does not feel like a rewrite.
2. **Full visual/structural rewrite (recommended)**: rebuild the shell, navigation, and page layout while keeping data flow intact. Strong differentiation without backend risk.
3. **Hard pivot to new design system**: replace `@trail/ui` with a brand new kit. High risk, large scope, and conflicts with repo patterns.

**Chosen:** Full visual/structural rewrite (2). It delivers a new experience while respecting existing contracts and the shared UI system.

## Design Direction
**Concept:** Trail Atlas. A guided, map-like workspace with strong hierarchy and clear wayfinding.
- **Typography:** Distinct display font for headlines + readable sans for body (no generic system stacks). Lowercase voice remains.
- **Color:** Keep warm neutrals and gold accent; deepen contrast and add soft gradients for atmosphere.
- **Layout:** Command center layout with a refined rail, a slim top header, and modular content panels.
- **Motion:** One strong page-load reveal and subtle hover transitions (no micro-motion spam).

## Information Architecture
- Keep existing core routes and add three new ones.
- Routes:
  - `/dashboard`
  - `/activity`
  - `/getting-started`
  - `/sessions`
  - `/extension`
  - `/settings`
  - `/billing`
- Navigation grouping:
  - **Core:** dashboard, activity, getting started
  - **Access:** sessions, extension
  - **Account:** settings, billing
- Add consistent page header pattern with title, subtitle, and contextual actions.
- Group page content into 2-3 visual zones per page to reduce scan fatigue.

## Page Patterns
- **Getting Started:** checklist-first layout (progress + steps) with a secondary panel for “what happens next.”
- **Activity:** timeline/stream (empty state for now) plus two supporting panels for usage/coverage cues.
- **Sessions:** device access list + security posture panel, with revoke guidance.
- **Dashboard:** status cockpit (health, quick actions, onboarding).
- **Extension/Settings/Billing:** keep functional intent, adopt new layout + header.

## Component Architecture
- `AppShell`: new shell with top header + nav rail + content grid.
- `Sidebar`: updated nav rail with active state, section grouping, and compact mode.
- `PageHeader`: shared header component for all pages.
- `Panel`, `StatCluster`, `Callout`: light-weight view components in account scope.

The app keeps `@trail/ui` components for shared primitives (`Button`, `Badge`, `StatCard`, `EmptyState`).

## Data & Rendering
- Server components remain default for pages.
- Client components only where required (`Sidebar`, `DashboardClient`).
- tRPC queries remain in `DashboardClient`.
- New pages use placeholder/empty states (no new backend data).
- No changes to Auth0 or API contracts.

## Error Handling
- Keep existing redirect patterns.
- No new error boundaries required; existing app-level handling is sufficient.

## Testing
- Add component tests for new shell and header patterns.
- Add page-level tests where rendering is deterministic (billing, settings, getting-started, activity, sessions with mocks).
- Keep tests minimal but explicit to satisfy TDD while avoiding brittle snapshots.

## Non-Goals
- No backend feature additions.
- No data model changes.
- No redesign of the browser extension UI.

## Rollout
- Single branch rewrite in `agent/account-rewrite`.
- Verify `pnpm -C apps/account test`, `typecheck`, and `build` before completion.
