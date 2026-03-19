---
phase: 08-shared-graph-big-tree-performance-pass
plan: 01
subsystem: ui
tags: [graph, layout-cache, bootstrap, feature-flags, offscreen-document]

# Dependency graph
requires:
  - phase: 07-state-architecture-graph-snapshot
    provides: Layout cache signature system with collapseSignature and recencyOrdering fields
provides:
  - Flags fetched on critical path before first GraphCanvas render
  - Offscreen layout precomputer uses real recencyOrdering flag from feature flags
  - Layout signature parity between offscreen precomputer and sidepanel consumer
affects: [08-02, 08-03, graph-startup, layout-cache]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Critical path parallel fetch: flags alongside settings and tree state"
    - "Offscreen document caches both settings and flags for layout computation"

key-files:
  created: []
  modified:
    - src/entrypoints/sidepanel/ui/hooks/useBootstrap.ts
    - src/entrypoints/offscreen-graph/main.ts

key-decisions:
  - "Used ResolvedFlags type instead of plan-suggested FeatureFlags (which does not exist)"
  - "Flags refetched on SAVE_SETTINGS rather than adding new FLAGS_CHANGED broadcast (no such message type exists in codebase)"

patterns-established:
  - "Offscreen document fetches flags alongside settings at bootstrap and on settings change"

requirements-completed: [BOOT-01, BOOT-02]

# Metrics
duration: 7min
completed: 2026-03-19
---

# Phase 08 Plan 01: Bootstrap Cache Accuracy Summary

**Flags fetched on critical path in useBootstrap; offscreen precomputer reads real recencyOrderingV2 flag for layout signature parity**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-19T14:49:19Z
- **Completed:** 2026-03-19T14:56:42Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Moved getFlags() from deferred section to critical path Promise.all in useBootstrap, ensuring flags are available in store before first GraphCanvas render
- Added cachedFlags state and fetchFlags() RPC call to offscreen-graph/main.ts, replacing hardcoded `false` with real `recencyOrderingV2` flag value
- Flags now fetched at offscreen bootstrap and refreshed on SAVE_SETTINGS messages

## Task Commits

Each task was committed atomically:

1. **Task 1: Move flags fetch to critical path in useBootstrap** - `0ac254eb` (feat)
2. **Task 2: Pass real recencyOrdering to offscreen layout computation** - `cabea97c` (feat)

## Files Created/Modified
- `src/entrypoints/sidepanel/ui/hooks/useBootstrap.ts` - getFlags() moved to critical path Promise.all; setFlags(flags) called after bootstrapGraph() before applyTheme()
- `src/entrypoints/offscreen-graph/main.ts` - Added cachedFlags, fetchFlags(), and recencyOrdering derivation from flags instead of hardcoded false

## Decisions Made
- Used `ResolvedFlags` type (the actual exported type from flags.ts) instead of plan-suggested `FeatureFlags` which does not exist in the codebase
- Flags are refetched alongside settings on SAVE_SETTINGS message rather than adding a new FLAGS_CHANGED broadcast, since no such message type exists in the RPC contracts
- Used `Promise.all([fetchSettings(), fetchFlags()])` for parallel initialization in both bootstrap and settings-change handler

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected type name from FeatureFlags to ResolvedFlags**
- **Found during:** Task 2 (offscreen layout computation)
- **Issue:** Plan suggested importing `FeatureFlags` type but the actual exported type in `src/shared/types/flags.ts` is `ResolvedFlags`
- **Fix:** Used `ResolvedFlags` for the `cachedFlags` type and response cast
- **Files modified:** src/entrypoints/offscreen-graph/main.ts
- **Verification:** TypeScript check passes with zero errors
- **Committed in:** cabea97c (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Type name correction necessary for compilation. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Bootstrap cache accuracy fixed; sidepanel and offscreen now compute identical layout signatures
- Ready for Plan 08-02 (next performance pass tasks)
- No blockers or concerns

---
*Phase: 08-shared-graph-big-tree-performance-pass*
*Completed: 2026-03-19*
