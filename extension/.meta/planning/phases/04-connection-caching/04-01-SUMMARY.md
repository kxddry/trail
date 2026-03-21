---
phase: 04-connection-caching
plan: 01
subsystem: ui
tags: [pixi, react, connection-geometry, caching, animation]

# Dependency graph
requires:
  - phase: 03-bypass-react-for-animation
    provides: "Imperative tick render path via handleTickRenderRef, staticVersion counter"
  - phase: 02-granular-renderer-api
    provides: "setStaticGraph/setDynamicState split, StaticGraphData/DynamicGraphState types"
provides:
  - "Cached base connections keyed to staticVersion (cachedBaseConnectionsRef)"
  - "applyPathHighlight helper for flag-toggle on cached segments"
  - "buildConnections signature without pathNodeIds (pure topology output)"
affects: [04-connection-caching, 05-interaction-optimization]

# Tech tracking
tech-stack:
  added: []
  patterns: [connection-caching-by-topology-signature, path-highlight-as-overlay, preview-edge-as-overlay]

key-files:
  created: []
  modified:
    - src/entrypoints/sidepanel/ui/components/graph/graph-utils.ts
    - src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx

key-decisions:
  - "Base connections use layout positions (not animated positions) since geometry is topology-dependent"
  - "Path highlight separated as flag toggle on cached segments via applyPathHighlight"
  - "Imperative tick render reads cached ref instead of rebuilding connections per frame"
  - "connPositions Map removed from imperative path since drag and animation are mutually exclusive"
  - "Static useEffect passes baseConnections (no path overlay) since path is ephemeral"

patterns-established:
  - "cachedBaseConnectionsRef pattern: cache expensive computation in ref, update only on staticVersion change"
  - "Overlay pattern: base data cached, overlays (path highlight, preview edge) applied as separate lightweight steps"

requirements-completed: [CONN-01, CONN-02]

# Metrics
duration: 3min
completed: 2026-03-18
---

# Phase 4 Plan 01: Connection Caching Summary

**Cached connection geometry by staticVersion with path highlight and preview edge as lightweight overlays, eliminating per-frame buildConnections calls**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-18T16:59:17Z
- **Completed:** 2026-03-18T17:02:45Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Eliminated per-animation-frame `buildConnections()` calls from the imperative tick render path
- Cached base connections in `cachedBaseConnectionsRef`, keyed to `staticVersion` (only rebuilds on topology/layout changes)
- Separated path highlight as a pure flag-toggle operation via `applyPathHighlight` helper
- Removed `connPositions` Map construction from imperative tick path (was building a new Map of ~N entries per frame)

## Task Commits

Each task was committed atomically:

1. **Task 1: Cache base connections by staticVersion and separate path/preview overlays** - `e9ce0d2d` (feat)
2. **Task 2: Verify connection caching correctness across all interaction modes** - verification only, no code changes

## Files Created/Modified
- `src/entrypoints/sidepanel/ui/components/graph/graph-utils.ts` - Added `applyPathHighlight` helper, removed `pathNodeIds` param from `buildConnections`
- `src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx` - Added `cachedBaseConnectionsRef`, restructured baseConnections/connections useMemos, updated imperative tick path and static useEffect

## Decisions Made
- **Base connections use layout positions, not animated positions:** Connection geometry is defined by topology/layout, not animation state. Using `positions` (base layout) instead of `connectionPositions` (animated) for cache correctness.
- **Path highlight as overlay, not embedded in buildConnections:** Separating `onPath` flag toggling from geometry computation enables caching the expensive geometry while keeping path highlight responsive to navigation changes.
- **Remove connPositions from imperative path entirely:** Drag reparent preview is mutually exclusive with animation (established in Phase 3), so no animated positions needed for connections during animation ticks.
- **Static useEffect passes baseConnections (without path overlay):** Path highlight is ephemeral state handled by the dynamic useEffect, keeping the static graph snapshot purely topology-based.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Connection caching foundation complete
- Phase 4 Plan 02 (connection topology signature) can build on this caching layer
- Phases 5-6 (interaction optimization, object pooling) can proceed in parallel

## Self-Check: PASSED

All files and commits verified:
- graph-utils.ts: FOUND
- GraphCanvas.tsx: FOUND
- 04-01-SUMMARY.md: FOUND
- Commit e9ce0d2d: FOUND

---
*Phase: 04-connection-caching*
*Completed: 2026-03-18*
