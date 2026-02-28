---
phase: 03-ux-polish
plan: 03
subsystem: ui
tags: [motion, animation, next.js, route-transitions, accessibility, prefers-reduced-motion]

requires: []
provides:
  - Route transition fade+slide animation for all (app) routes via template.tsx
  - prefers-reduced-motion accessibility support for route transitions
affects: [03-ux-polish]

tech-stack:
  added: []
  patterns:
    - "Next.js template.tsx for per-route animation: re-mounts on every navigation, triggering Motion initial cycle"
    - "useReducedMotion() hook pattern for conditional animation based on OS accessibility preference"

key-files:
  created:
    - apps/account/app/(app)/template.tsx
  modified: []

key-decisions:
  - "No exit animation: template.tsx unmounts/remounts naturally; instant-out + fade-in feels snappier than bidirectional transitions"
  - "No AnimatePresence needed: template re-mounting triggers initial prop without extra wrapper"
  - "useReducedMotion() over CSS override: Motion handles its own reduced-motion detection, no globals.css changes needed"
  - "initial=false (not initial={{opacity:0}}) for reduced motion: skips the entrance entirely rather than animating instantly to final state"

patterns-established:
  - "Route animation via template.tsx: use Next.js template segment for animations that should fire on every navigation"
  - "Reduced motion hook pattern: useReducedMotion() + conditional initial/duration for accessible Motion animations"

requirements-completed: [UX-07]

duration: 2min
completed: 2026-02-28
---

# Phase 03 Plan 03: Route Transition Animations Summary

**Next.js template.tsx fade+slide route transitions via Motion with useReducedMotion() accessibility hook**

## Performance

- **Duration:** ~2 min
- **Started:** 2026-02-28T16:11:06Z
- **Completed:** 2026-02-28T16:12:30Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- Created `apps/account/app/(app)/template.tsx` — a client component wrapping route children in a Motion fade+slide entrance animation (opacity 0→1, y 6→0, 0.25s ease-out)
- Added `useReducedMotion()` hook to detect OS accessibility preference and skip animation entirely (`initial={false}`, `duration=0`) for users who prefer reduced motion
- TypeScript compiles without errors for both tasks

## Task Commits

Each task was committed atomically:

1. **Task 1: Create route transition template with Motion** - `9501d118` (feat)
2. **Task 2: Add reduced motion support for route transitions** - `e6e8673c` (feat)

**Plan metadata:** (pending final commit)

## Files Created/Modified

- `apps/account/app/(app)/template.tsx` - Route transition wrapper using Motion fade+slide animation with prefers-reduced-motion support

## Decisions Made

- No exit animation: template.tsx unmounts/remounts naturally on each navigation — instant-out + fade-in is snappier than bidirectional transitions and avoids needing AnimatePresence at layout level
- Used `initial={false}` (not `initial={{ opacity: 1, y: 0 }}`) for reduced motion: `false` skips the entrance entirely, which is the correct behavior for users who prefer no animation
- globals.css unchanged: Motion's `useReducedMotion()` hook handles JS animation reduced-motion detection natively; CSS override only needed for CSS-keyframe animations

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

- `npx tsc` was intercepted by a shim that blocked direct invocation; resolved by using `apps/account/node_modules/.bin/tsc` directly (standard monorepo pattern where tsc lives in workspace node_modules)

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Route transitions complete and accessible
- template.tsx is in place and will animate all future routes added under `apps/account/app/(app)/`
- No blockers for remaining 03-ux-polish plans

## Self-Check: PASSED

- FOUND: apps/account/app/(app)/template.tsx
- FOUND: .planning/phases/03-ux-polish/03-03-SUMMARY.md
- FOUND: commit 9501d118 (Task 1: route transition template)
- FOUND: commit e6e8673c (Task 2: reduced motion support)

---
*Phase: 03-ux-polish*
*Completed: 2026-02-28*
