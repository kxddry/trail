---
phase: 03-ux-polish
plan: 01
subsystem: ui

tags: [nextjs, react, tailwindcss, loading-states, error-pages]

# Dependency graph
requires: []
provides:
  - Branded error.tsx (500 page) with animated TrailLogo
  - Branded root not-found.tsx (404 page) with animated TrailLogo and "go home" CTA
  - Branded app-scoped (app)/not-found.tsx with animated TrailLogo
  - Staggered pulse animation on trails skeleton cards (75ms per card)
  - Root loading.tsx confirmed already using branded TrailLogo
affects: [03-ux-polish]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Error pages always feature animated TrailLogo above content stack"
    - "Skeleton card lists use per-item animationDelay (i * 75ms) for stagger effect"

key-files:
  created: []
  modified:
    - apps/account/app/error.tsx
    - apps/account/app/not-found.tsx
    - apps/account/app/(app)/not-found.tsx
    - apps/account/app/(app)/trails/loading.tsx

key-decisions:
  - "Root not-found.tsx gets a secondary 'go home' CTA (/) in addition to 'go to trails' — provides escape hatch to app root"
  - "settings/loading.tsx kept unchanged — plan confirmed it accurately represents settings layout; no structural changes needed"
  - "animationDelay applied to card container div (not individual Skeleton children) — cascades correctly since Tailwind pulse animates the skeleton children"

patterns-established:
  - "Trail-branded error pages: TrailLogo animated above content, existing CTAs preserved"
  - "Skeleton stagger: Array.from().map with style={{ animationDelay: i * N + 'ms' }} on the card wrapper"

requirements-completed: [UX-01, UX-02, UX-03, UX-05]

# Metrics
duration: 2min
completed: 2026-02-28
---

# Phase 3 Plan 01: Brand Error Pages and Polish Loading States Summary

**Animated TrailLogo added to all three error/404 pages and staggered pulse animation added to trails skeleton cards, replacing plain-text error states with Trail-branded identity.**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-02-28T16:10:58Z
- **Completed:** 2026-02-28T16:12:40Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- All three error/404 pages (error.tsx, root not-found.tsx, app-scoped not-found.tsx) now display animated TrailLogo above existing copy
- Root loading.tsx confirmed correct with branded TrailLogo — no changes needed
- Trails skeleton cards now stagger their pulse animation (75ms per card) for a more refined loading feel
- TypeScript compiles cleanly after all changes

## Task Commits

Each task was committed atomically:

1. **Task 1: Brand error pages with animated TrailLogo** - `d789bb6f` (feat)
2. **Task 2: Verify root loading and polish skeleton loaders** - `8a8caed6` (feat)

**Plan metadata:** committed after summary creation (docs)

## Files Created/Modified
- `apps/account/app/error.tsx` - Added TrailLogo import and animated logo above error content
- `apps/account/app/not-found.tsx` - Added TrailLogo import, animated logo, and secondary "go home" CTA
- `apps/account/app/(app)/not-found.tsx` - Added TrailLogo import and animated logo above 404 content
- `apps/account/app/(app)/trails/loading.tsx` - Added animationDelay (i * 75ms) to skeleton card containers for stagger effect

## Decisions Made
- Root not-found.tsx gets a secondary "go home" CTA as specified in plan — provides a clean escape route to the app root
- settings/loading.tsx kept unchanged — plan explicitly confirmed the existing structure accurately represents the settings layout
- animationDelay placed on card container div — correct level since Tailwind's animate-pulse applies to children via inheritance

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- `npx tsc` not available in this environment; resolved by using the pnpm-managed tsc binary at `node_modules/.pnpm/typescript@5.9.3/node_modules/typescript/bin/tsc` directly.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- All UX-01, UX-02, UX-03, UX-05 requirements satisfied
- Error pages are now fully on-brand — ready for next polish tasks in Phase 3

---
*Phase: 03-ux-polish*
*Completed: 2026-02-28*

## Self-Check: PASSED

- FOUND: apps/account/app/error.tsx
- FOUND: apps/account/app/not-found.tsx
- FOUND: apps/account/app/(app)/not-found.tsx
- FOUND: apps/account/app/(app)/trails/loading.tsx
- FOUND: .planning/phases/03-ux-polish/03-01-SUMMARY.md
- FOUND: commit d789bb6f
- FOUND: commit 8a8caed6
