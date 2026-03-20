---
phase: 01-budgeted-rich-content-restoration-after-pan-zoom
plan: 01
subsystem: graph-renderer
tags: [pixi, restore-queue, priority-scoring, batch-budget, text-resolution-freeze]

requires:
  - phase: 04-graph-startup-optimization
    provides: cached layout and deferred hydration foundation

provides:
  - restore-policy.ts with priority scoring and batch budget calculator
  - prioritized budgeted restore queue in GraphPixiRenderer
  - textResolution freeze during gestures

affects: [01-02, 01-03]

tech-stack:
  added: []
  patterns: [priority-sorted restore queue, frame-budgeted idle callbacks, gesture-aware resolution freeze]

key-files:
  created:
    - extension/src/features/graph/graph/render/restore-policy.ts
  modified:
    - extension/src/features/graph/graph/render/GraphPixiRenderer.ts

key-decisions:
  - "RestoreScoringModel interface instead of full NodeRenderModel import keeps restore-policy lightweight"
  - "Median-based distance split for tier 5/6 adapts to any viewport size without tuning"
  - "All tree sizes use budgeted path — removed small-tree immediate bypass for consistency"

patterns-established:
  - "Priority restore queue: score at creation, sort before scheduling, shift during idle"
  - "Gesture freeze pattern: set frozen=true on gesture start, unfreeze after queue drains"

requirements-completed: []

duration: 4min
completed: 2026-03-20
---

# Phase 01 Plan 01: Prioritized Budgeted Restore Queue Summary

**Priority-sorted restore queue with 7-tier scoring, dynamic batch budgets by tree size, and textResolution freeze during gestures**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-20T11:47:45Z
- **Completed:** 2026-03-20T11:52:10Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Created restore-policy.ts: standalone module with priority scoring (current > hover > selected > search > path > near > far), immutable queue sort with median-based viewport distance split, and tree-size-aware batch budgets (60/30/15)
- Replaced flat FIFO hydrationQueue in GraphPixiRenderer with prioritized RestoreEntry[] queue -- all tree sizes now use the budgeted path uniformly
- Added textResolution freeze during gestures to prevent expensive re-rasterization during zoom/pinch, with automatic unfreeze after restore queue drains

## Task Commits

Each task was committed atomically:

1. **Task 1: Create restore-policy.ts** - `10bdea5f` (feat)
2. **Task 2: Rewire GraphPixiRenderer hydration** - `3d82337c` (feat)

## Files Created/Modified

- `extension/src/features/graph/graph/render/restore-policy.ts` - Priority scoring, queue sort, batch budget calculator
- `extension/src/features/graph/graph/render/GraphPixiRenderer.ts` - Replaced hydration system with prioritized budgeted restore

## Decisions Made

- Used a minimal `RestoreScoringModel` interface instead of importing full `NodeRenderModel` to keep restore-policy.ts lightweight and decoupled
- Used median distance of all tier-5 entries as the split threshold for near/far -- adapts to any viewport without hardcoded pixel values
- Removed the small-tree immediate hydration bypass entirely -- all trees use budgeted path for consistent progressive restoration

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- restore-policy.ts exports are ready for import by Plan 02 (integration testing) and Plan 03 (refinement)
- textResolution freeze/unfreeze lifecycle is complete and self-contained
- No blockers for subsequent plans

---
*Phase: 01-budgeted-rich-content-restoration-after-pan-zoom*
*Completed: 2026-03-20*

## Self-Check: PASSED
