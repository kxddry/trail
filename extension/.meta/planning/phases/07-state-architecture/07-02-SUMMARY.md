---
phase: 07-state-architecture
plan: 02
subsystem: graph-rendering
tags: [cache, layout, pixi, chrome-storage, performance]

# Dependency graph
requires:
  - phase: 07-state-architecture
    provides: "GraphSnapshot type and static/dynamic split from plan 01"
provides:
  - "Enriched CachedLayoutResult with collapseSignature and recencyOrdering fields"
  - "computeCollapseSignature helper for deterministic state hashing"
  - "Enriched storage keys incorporating layout mode, collapse state, recency flag"
  - "Dual-write cache strategy (enriched + base key) for backward compatibility"
  - "Collapse-aware offscreen layout computation"
  - "State-validated cache hydration in GraphCanvas"
affects: [graph-rendering, layout-cache, offscreen-graph]

# Tech tracking
tech-stack:
  added: []
  patterns: ["enriched cache key with state signature", "dual-write storage for backward compat", "getVisibleChildren wrapper for collapse filtering"]

key-files:
  created: []
  modified:
    - src/shared/graph-layout-cache/types.ts
    - src/shared/graph-layout-cache/cache.ts
    - src/shared/graph-layout-cache/compute-layout.ts
    - src/entrypoints/offscreen-graph/main.ts
    - src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx

key-decisions:
  - "Dual-write to both enriched and base storage keys for backward compatibility"
  - "recencyOrdering always false in offscreen doc (no access to live tab recency data)"
  - "spotlight-graph unchanged -- uses base key fallback, lets hydrateFromCache 80% threshold handle stale data"
  - "Collapse filtering via getVisibleChildren wrapper passed to existing layout calculator APIs"

patterns-established:
  - "Enriched cache key: treeId:layoutMode:collapseSignature:recencyFlag"
  - "computeCollapseSignature: sorted comma-joined node IDs for deterministic hashing"
  - "Backward compat via ?? defaults: collapseSignature ?? '' and recencyOrdering ?? false"

requirements-completed: [ARCH-03]

# Metrics
duration: 4min
completed: 2026-03-18
---

# Phase 7 Plan 2: Layout Cache Enrichment Summary

**Enriched offscreen layout cache with collapse state signature and recency ordering flag for >90% warm-open cache hit rate**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-18T19:11:35Z
- **Completed:** 2026-03-18T19:16:03Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- CachedLayoutResult now includes collapseSignature and recencyOrdering fields for precise cache matching
- Storage key enriched with layout mode, collapse state hash, and recency flag -- dual-write ensures backward compatibility
- Offscreen document passes optional collapsed node IDs to layout computation, filtering via getVisibleChildren
- GraphCanvas validates collapse + recency state match before cache hydration, discarding stale cache on mismatch

## Task Commits

Each task was committed atomically:

1. **Task 1: Enrich CachedLayoutResult type and cache key with state signature** - `5af360f9` (feat)
2. **Task 2: Wire offscreen document and consumers to use enriched cache keys** - `50a78567` (feat)

**Plan metadata:** `01cfcf31` (docs: complete plan)

## Files Created/Modified
- `src/shared/graph-layout-cache/types.ts` - Added collapseSignature, recencyOrdering fields and computeCollapseSignature helper
- `src/shared/graph-layout-cache/cache.ts` - Enriched storageKey, dual-write, enriched-first read with base key fallback
- `src/shared/graph-layout-cache/compute-layout.ts` - Accept collapsedNodeIds/recencyOrdering, filter via getVisibleChildren, include new fields in result
- `src/entrypoints/offscreen-graph/main.ts` - Extract collapsedNodeIds from TREE_UPDATED, pass to computeLayoutFromTree
- `src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx` - Validate collapseSignature + recencyOrdering before cache hydration

## Decisions Made
- Dual-write to both enriched and base storage keys: enriched key for exact match lookups, base key for consumers that don't know state yet (spotlight-graph)
- recencyOrdering always false in offscreen doc since it cannot access live tab recency data
- spotlight-graph unchanged -- reads base key, lets hydrateFromCache 80% threshold handle minor mismatches
- Collapse filtering via getVisibleChildren wrapper reusing existing layout calculator optional parameter

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 7 (state architecture) is now complete with both plans executed
- Layout cache properly keyed by collapse state and recency ordering
- Ready for production use with improved warm-open cache hit rates

## Self-Check: PASSED

- All 5 modified files exist on disk
- Commit 5af360f9 (Task 1) found in git log
- Commit 50a78567 (Task 2) found in git log
- TypeScript compiles without errors

---
*Phase: 07-state-architecture*
*Completed: 2026-03-18*
