---
phase: 01-budgeted-rich-content-restoration-after-pan-zoom
plan: 02
subsystem: ui
tags: [pixi, favicon, lru-cache, performance, requestAnimationFrame, measureText]

requires:
  - phase: 01-budgeted-rich-content-restoration-after-pan-zoom
    provides: "RestoreScoringModel, budgeted restore queue, priority-based idle hydration"
provides:
  - "LRU favicon cache with dynamic limit scaled to visible node count"
  - "Batched favicon invalidation via requestAnimationFrame coalescing"
  - "Badge measureText width cache eliminating redundant CanvasTextMetrics calls"
affects: [01-03]

tech-stack:
  added: []
  patterns: [LRU-via-Map-delete-reset, requestAnimationFrame-batching, module-level-metrics-cache]

key-files:
  created: []
  modified:
    - extension/src/features/graph/graph/render/GraphPixiRenderer.ts

key-decisions:
  - "LRU via native Map delete+re-set pattern -- no external LRU library needed"
  - "Dynamic favicon cache limit at 1.5x visible node count with 256 floor"
  - "Batched favicon flush via single requestAnimationFrame per frame, not per icon"
  - "Badge metrics cache keyed on text alone since style is constant (fontSize=9, fontWeight=700)"

patterns-established:
  - "LRU cache via Map delete+re-set: delete key on access, re-set to move to end"
  - "Batched invalidation: queue IDs, schedule single rAF, flush all in one pass"

requirements-completed: []

duration: 7min
completed: 2026-03-20
---

# Phase 01 Plan 02: Favicon & Badge Cache Optimization Summary

**LRU favicon cache with dynamic limit, batched favicon invalidation via rAF coalescing, and cached badge measureText widths**

## Performance

- **Duration:** 7 min
- **Started:** 2026-03-20T11:56:40Z
- **Completed:** 2026-03-20T12:03:24Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- Favicon cache converted from FIFO to LRU eviction (delete+re-set on access, evict from front)
- Cache limit scales dynamically to 1.5x visible node count (minimum 256)
- Favicon texture loads batched into single render pass via requestAnimationFrame coalescing
- Per-icon invalidate() calls eliminated -- NodeVisual uses onFaviconReady callback routed to renderer queue
- Badge measureText widths cached per unique text string, avoiding repeated CanvasTextMetrics.measureText calls

## Task Commits

Each task was committed atomically:

1. **Task 1: Convert favicon cache from FIFO to LRU with dynamic limit and batched invalidation** - `9dbbffb0` (feat)
2. **Task 2: Cache tab-count badge measureText widths** - `2d1bd43b` (feat)

## Files Created/Modified
- `extension/src/features/graph/graph/render/GraphPixiRenderer.ts` - LRU favicon cache, batched favicon invalidation, badge width cache

## Decisions Made
- LRU via native Map delete+re-set pattern -- no external library needed, Map iteration order is insertion order
- Dynamic favicon cache limit at 1.5x visible nodes with 256 floor -- provides scrolling headroom without unbounded growth
- Batched favicon flush via single requestAnimationFrame -- coalesces N icon-ready callbacks into one visual update pass
- Badge metrics cache keyed on text alone -- style is constant (fontSize=9, fontWeight=700), cache naturally bounded by tab count range

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Favicon and badge caching complete, ready for Plan 03 (remaining optimizations)
- TypeScript compiles cleanly

---
*Phase: 01-budgeted-rich-content-restoration-after-pan-zoom*
*Completed: 2026-03-20*
