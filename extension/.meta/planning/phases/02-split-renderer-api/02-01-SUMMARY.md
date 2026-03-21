---
phase: 02-split-renderer-api
plan: 01
subsystem: ui
tags: [pixi, renderer, spatial-index, graph, performance]

requires:
  - phase: 01-profiling-infrastructure
    provides: graphProfiler with record() and ProfilePhase types
provides:
  - setStaticGraph() method for topology changes with SpatialIndex rebuild
  - setDynamicState() method for lightweight node patching without index rebuild
  - setParticles() method for independent particle layer updates
  - StaticGraphData and DynamicGraphState type definitions
affects: [02-split-renderer-api, 03-bypass-react-animation]

tech-stack:
  added: []
  patterns: [granular-renderer-api, static-vs-dynamic-split]

key-files:
  created: []
  modified:
    - src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts
    - src/entrypoints/sidepanel/ui/graph/render/graph-profiler.ts

key-decisions:
  - "Keep setData() deprecated but functional for backward compat until Plan 02 updates consumers"
  - "setDynamicState does not clear cachedCullingRect since viewport unchanged"
  - "setStaticGraph preserves existing particles via spread into this.data"

patterns-established:
  - "Static/dynamic split: topology changes go through setStaticGraph (heavy), UI state changes go through setDynamicState (lightweight)"
  - "SpatialIndex rebuild isolated to setStaticGraph only, never during dynamic updates"

requirements-completed: [RCYC-02, RCYC-03]

duration: 1min
completed: 2026-03-18
---

# Phase 2 Plan 1: Granular Renderer API Summary

**Granular GraphPixiRenderer API splitting static topology (setStaticGraph with SpatialIndex rebuild) from dynamic UI state (setDynamicState without index rebuild) and independent particle updates (setParticles)**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-18T15:35:08Z
- **Completed:** 2026-03-18T15:36:28Z
- **Tasks:** 1
- **Files modified:** 2

## Accomplishments
- Implemented setStaticGraph() that rebuilds SpatialIndex on topology change
- Implemented setDynamicState() for lightweight node data patching without index rebuild
- Implemented setParticles() for independent particle layer updates
- Added StaticGraphData and DynamicGraphState types
- Updated graph-profiler with setStaticGraph and setDynamicState phases
- Marked old setData() as deprecated while maintaining backward compatibility

## Task Commits

Each task was committed atomically:

1. **Task 1: Define types and implement setStaticGraph / setDynamicState / setParticles** - `88294c6e` (feat)

## Files Created/Modified
- `src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts` - Added StaticGraphData, DynamicGraphState types; implemented setStaticGraph, setDynamicState, setParticles methods; deprecated setData
- `src/entrypoints/sidepanel/ui/graph/render/graph-profiler.ts` - Added setStaticGraph and setDynamicState to ProfilePhase union and ALL_PHASES array

## Decisions Made
- Kept setData() deprecated but functional: GraphCanvas still calls it until Plan 02 updates the consumer side
- setDynamicState does not clear cachedCullingRect: viewport position is unchanged during dynamic updates, so the culling rect remains valid
- setStaticGraph preserves existing particles via `{ ...data, particles: this.particles }` spread

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Granular API is in place, ready for Plan 02 to update GraphCanvas consumer to use the new methods
- Old setData() still works, so no breaking change introduced
- Profiler phases ready to track performance of new API paths

## Self-Check: PASSED

All files exist, all commits verified.

---
*Phase: 02-split-renderer-api*
*Completed: 2026-03-18*
