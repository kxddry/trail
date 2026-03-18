---
phase: 02-split-renderer-api
plan: 02
subsystem: ui
tags: [pixi, renderer, react, graph, performance, spatial-index]

requires:
  - phase: 02-split-renderer-api
    provides: setStaticGraph, setDynamicState, setParticles methods on GraphPixiRenderer
provides:
  - GraphCanvas consumer migrated from setData to granular API (setStaticGraph / setDynamicState / setParticles)
  - Old setData() and RenderData type removed from GraphPixiRenderer
  - SpatialIndex rebuilds isolated to topology/layout changes only
affects: [03-bypass-react-animation]

tech-stack:
  added: []
  patterns: [static-version-counter, split-useeffect-by-concern]

key-files:
  created: []
  modified:
    - src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx
    - src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts
    - src/entrypoints/sidepanel/ui/graph/render/graph-profiler.ts

key-decisions:
  - "staticVersion ref counter to discriminate topology changes from animation-only changes in React dependency arrays"
  - "setDynamicState reconciles nodeData map to clean up stale exit animation nodes"
  - "setDynamicState updates spatial index positions for drag without full rebuild"
  - "Exit animation nodes inserted into spatial index via setDynamicState for correct hit testing"

patterns-established:
  - "Static version counter: useMemo tracks basePositions/layoutMode/dimensions changes, useEffect depends on counter instead of derived data"
  - "Three-way useEffect split: static topology, dynamic state, particles — each with minimal dependency arrays"

requirements-completed: [RCYC-02, RCYC-03]

duration: 25min
completed: 2026-03-18
---

# Phase 2 Plan 2: GraphCanvas Granular API Migration Summary

**GraphCanvas migrated from monolithic setData to three split useEffects calling setStaticGraph (topology), setDynamicState (animation/hover/search), and setParticles, with spatial index fixes for drag and exit animations**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-03-18T15:38:00Z
- **Completed:** 2026-03-18T16:03:00Z
- **Tasks:** 2 (1 auto + 1 checkpoint)
- **Files modified:** 3

## Accomplishments
- Replaced single setData useEffect with three granular useEffects (setStaticGraph, setDynamicState, setParticles)
- Added staticVersion ref counter to detect topology/layout changes vs animation-only changes
- Removed deprecated setData() method and RenderData type from GraphPixiRenderer
- Cleaned graph-profiler of 'setData' phase, replaced with 'setStaticGraph' and 'setDynamicState'
- Fixed spatial index position updates for drag operations in setDynamicState
- Fixed exit animation nodes being excluded from spatial index
- Fixed stale exit nodes accumulating in nodeData map via reconciliation in setDynamicState

## Task Commits

Each task was committed atomically:

1. **Task 1: Split GraphCanvas useEffect into granular renderer API calls** - `2280debf` (feat)
   - Post-checkpoint fixes:
   - `1cc5cf28` (fix) - Update spatial index in setDynamicState when positions change (drag)
   - `9efaa6c7` (fix) - Insert exit animation nodes into spatial index via setDynamicState
   - `86e313ba` (fix) - Reconcile nodeData in setDynamicState to clean up stale exit nodes
2. **Task 2: Visual regression check** - Checkpoint approved by user

## Files Created/Modified
- `src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx` - Replaced single setData useEffect with three split useEffects (setStaticGraph, setDynamicState, setParticles); added staticVersion ref counter and prevStaticDepsRef
- `src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts` - Removed deprecated setData() method and RenderData type; fixed setDynamicState to update spatial index positions, handle exit nodes, and reconcile stale nodeData entries
- `src/entrypoints/sidepanel/ui/graph/render/graph-profiler.ts` - Removed 'setData' from ProfilePhase union and ALL_PHASES array

## Decisions Made
- Used a staticVersion ref counter (incremented in useMemo) to detect topology/layout changes: this allows the static useEffect to fire only when basePositions, layoutMode, nodeWidth, or nodeHeight change, even though renderNodes and connections are recomputed on every animation frame
- setDynamicState reconciles the nodeData map against incoming nodes to remove stale exit animation entries that no longer exist in the current render model
- setDynamicState updates spatial index positions (without full rebuild) when node positions change during drag operations, maintaining correct hit testing
- Exit animation nodes are inserted into the spatial index during setDynamicState to ensure they remain interactive during fade-out animations

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Spatial index stale during drag operations**
- **Found during:** Post-checkpoint testing (Task 2)
- **Issue:** setDynamicState did not update spatial index positions, so drag-to-reparent hit testing used stale positions from the last setStaticGraph call
- **Fix:** Added position comparison in setDynamicState that updates spatial index entries when node positions change, without triggering a full index rebuild
- **Files modified:** src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts
- **Verification:** Drag reparent works correctly with updated positions
- **Committed in:** 1cc5cf28

**2. [Rule 1 - Bug] Exit animation nodes excluded from spatial index**
- **Found during:** Post-checkpoint testing (Task 2)
- **Issue:** Nodes animating out (exit animation) were not inserted into the spatial index by setDynamicState, causing them to be untargetable during their fade-out animation
- **Fix:** Added logic in setDynamicState to detect new nodes not present in nodeData and insert them into both nodeData map and spatial index
- **Files modified:** src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts
- **Verification:** Exit animation nodes visible and interactive during fade-out
- **Committed in:** 9efaa6c7

**3. [Rule 1 - Bug] Stale exit nodes accumulating in nodeData map**
- **Found during:** Post-checkpoint testing (Task 2)
- **Issue:** After exit animations completed and nodes were removed from renderNodes, their entries persisted in nodeData map indefinitely, causing phantom state
- **Fix:** Added reconciliation step in setDynamicState that removes nodeData entries for nodes no longer present in the incoming render model
- **Files modified:** src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts
- **Verification:** nodeData map stays in sync with current render model
- **Committed in:** 86e313ba

---

**Total deviations:** 3 auto-fixed (3 bugs via Rule 1)
**Impact on plan:** All fixes necessary for correct drag and animation behavior. No scope creep.

## Issues Encountered
None beyond the auto-fixed bugs above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 2 complete: monolithic setData fully replaced with granular API
- SpatialIndex rebuilds now isolated to topology/layout changes only (RCYC-03 verified)
- Ready for Phase 3: bypass React for animation (animateTick calling setDynamicState imperatively via ref)
- Profiler tracks setStaticGraph and setDynamicState phases separately for performance measurement

## Self-Check: PASSED

All files exist, all commits verified.

---
*Phase: 02-split-renderer-api*
*Completed: 2026-03-18*
