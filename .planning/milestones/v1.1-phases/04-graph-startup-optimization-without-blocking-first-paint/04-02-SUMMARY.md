---
phase: 04-graph-startup-optimization-without-blocking-first-paint
plan: 02
subsystem: ui
tags: [zustand, react, bootstrap, cache, performance, chrome-extension]

requires:
  - phase: 04-graph-startup-optimization-without-blocking-first-paint
    provides: graph layout cache infrastructure (plan 01)
provides:
  - bootstrapGraph store action (settings + tree only, no platform meta)
  - setPlatformMeta store action (deferred platform info)
  - Split useBootstrap with critical + deferred phases
  - Pre-mount cache fetch in sidepanel and fullview entrypoints
  - Centralized __trailCachedLayout global declaration in bootstrap.tsx
affects: [04-graph-startup-optimization-without-blocking-first-paint]

tech-stack:
  added: []
  patterns: [critical-deferred-bootstrap, pre-mount-cache-fetch, independent-error-handling]

key-files:
  created: []
  modified:
    - extension/src/entrypoints/sidepanel/ui/state/store.ts
    - extension/src/entrypoints/sidepanel/ui/hooks/useBootstrap.ts
    - extension/src/ui-core/panel/bootstrap.tsx
    - extension/src/entrypoints/sidepanel/ui/main.tsx
    - extension/src/entrypoints/fullview/ui/main.tsx
    - extension/src/entrypoints/spotlight-graph/main.tsx

key-decisions:
  - "bootstrapGraph does NOT set metaKey or isMac -- platform meta is deferred to avoid blocking first paint"
  - "Each deferred fetch has independent .catch() -- one failure does not block others"
  - "Critical path failure returns early, letting React mount show loading state until TREE_UPDATED arrives"
  - "Global __trailCachedLayout declaration centralized in bootstrap.tsx, removed from spotlight-graph"

patterns-established:
  - "Critical-deferred bootstrap: critical fetches block mount, deferred fetches run after first paint with Promise.allSettled"
  - "Pre-mount cache fetch: readLayoutCache at module load, await before createRoot, stash on globalThis"

requirements-completed: [PERF-01, PERF-04, PERF-06]

duration: 3min
completed: 2026-03-19
---

# Phase 04 Plan 02: Bootstrap Split Summary

**Split graph bootstrap to paint from settings+tree only (2 RPCs), deferring tags/flags/trees/platform/commands after first paint with pre-mount layout cache in all entrypoints**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-19T07:15:24Z
- **Completed:** 2026-03-19T07:18:31Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Graph first paint now depends only on settings + tree state (2 RPC calls instead of 6)
- Tag definitions, flags, trees list, platform meta, and command state load after first paint as deferred fetches
- Sidepanel and fullview entrypoints pre-fetch layout cache before React mounts (matching existing spotlight-graph pattern)
- Each deferred fetch has independent error handling -- one failure does not block others

## Task Commits

Each task was committed atomically:

1. **Task 1: Add bootstrapGraph store action and setPlatformMeta, split useBootstrap** - `0237df82` (feat)
2. **Task 2: Add pre-mount cache fetch to sidepanel and fullview entrypoints** - `1d0f4f88` (feat)

## Files Created/Modified
- `extension/src/entrypoints/sidepanel/ui/state/store.ts` - Added bootstrapGraph (settings+tree only) and setPlatformMeta actions
- `extension/src/entrypoints/sidepanel/ui/hooks/useBootstrap.ts` - Split into critical (settings+tree) and deferred (flags, tags, trees, platform, commands) phases
- `extension/src/ui-core/panel/bootstrap.tsx` - Accept optional cachedLayout, declare global __trailCachedLayout type
- `extension/src/entrypoints/sidepanel/ui/main.tsx` - Pre-fetch layout cache before React mount
- `extension/src/entrypoints/fullview/ui/main.tsx` - Pre-fetch layout cache before React mount
- `extension/src/entrypoints/spotlight-graph/main.tsx` - Removed duplicate declare global (now in bootstrap.tsx)

## Decisions Made
- bootstrapGraph does NOT set metaKey or isMac -- deferred to setPlatformMeta to avoid blocking first paint on platform info RPC
- Each deferred fetch has independent .catch() handler -- one failing fetch does not prevent others from completing
- Critical path failure logs error and returns early, allowing React to mount and show loading state until TREE_UPDATED event arrives from background
- Centralized __trailCachedLayout global type declaration in bootstrap.tsx rather than duplicating across entrypoints

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Bootstrap split complete, graph can paint from minimal critical data
- Pre-mount cache available in all three surfaces (sidepanel, fullview, spotlight)
- Ready for plan 03 (any remaining optimization tasks in phase 04)

## Self-Check: PASSED

All 6 modified files verified on disk. Both task commits (0237df82, 1d0f4f88) verified in git log.

---
*Phase: 04-graph-startup-optimization-without-blocking-first-paint*
*Completed: 2026-03-19*
