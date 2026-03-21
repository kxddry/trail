---
phase: 07-performance-budgets
plan: 01
subsystem: performance
tags: [pixi, profiling, lod, spotlight, minisearch, adaptive-quality]

# Dependency graph
requires:
  - phase: 04-graph-startup-optimization
    provides: graph-profiler, startup metrics infrastructure, quality-policy
  - phase: 06-security-privacy-audit
    provides: structured logger with redaction
provides:
  - Budget breach logging for sidepanel paint, graph interactive, spotlight query
  - Adaptive degradation enabled by default with LOD node hiding
  - Node-count quality floor for large trees
  - Spotlight index idle pre-warming from sidepanel boot
  - Archive-capped spotlight rebuild (10 most recent)
affects: [07-02, 08-qa-release-discipline]

# Tech tracking
tech-stack:
  added: []
  patterns: [perf-budget-breach-logging, node-count-quality-floor, archive-cap-pattern, idle-prewarm]

key-files:
  created:
    - extension/src/shared/lib/perf-metrics.ts
  modified:
    - extension/src/features/graph/graph/render/graph-profiler.ts
    - extension/src/shared/types/flags.ts
    - extension/src/features/graph/graph/render/GraphPixiRenderer.ts
    - extension/src/features/graph/components/graph/GraphArea.tsx
    - extension/src/apps/sidepanel/ui/hooks/useBootstrap.ts
    - extension/src/background/services/spotlight.ts
    - extension/src/background/services/spotlight-live-index.ts

key-decisions:
  - "Created perf-metrics.ts singleton for service worker context (graph-profiler.ts uses window, incompatible with service worker)"
  - "Used fire-and-forget SPOTLIGHT_BOOTSTRAP RPC for pre-warming instead of adding new RPC method (reuses existing handler that builds index)"
  - "Node-count quality floor uses worstDetail() merge with existing detailMode (preserves overlay/gesture overrides)"

patterns-established:
  - "perf-budget-breach: recordStartup() auto-checks BUDGET_THRESHOLDS and logs via structured logger"
  - "node-count-floor: trees >500 nodes start at low, >2000 at dot, merged with worst-of existing quality"
  - "archive-cap: sort-by-recency + slice pattern for bounding expensive archive iteration"

requirements-completed: [PERF-01, PERF-02, PERF-03]

# Metrics
duration: 6min
completed: 2026-03-21
---

# Phase 7 Plan 1: Budget Metrics, Adaptive Degradation, Spotlight Optimization Summary

**Three performance budget metrics with breach logging, adaptive graph degradation enabled by default, and spotlight index pre-warming with archive cap**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-21T16:48:55Z
- **Completed:** 2026-03-21T16:55:21Z
- **Tasks:** 2
- **Files modified:** 8 (7 modified + 1 created)

## Accomplishments
- Three budget metrics (sidepanelPaintMs/500ms, firstRenderMs/1000ms, spotlightQueryMs/100ms) instrumented with structured logger breach warnings
- adaptivePerformance flag enabled by default, LOD_HIDE_PX=4 and LOD_CONN_HIDE_PX=6 for node hiding at extreme zoom-out
- Node-count quality floor: trees >500 nodes start at low quality, >2000 start at dot quality
- Spotlight query latency timed per search call with 100ms budget threshold
- Spotlight index pre-warms via fire-and-forget RPC on sidepanel open
- Archive loading in rebuild() capped to 10 most recent archives

## Task Commits

Each task was committed atomically:

1. **Task 1: Budget metrics instrumentation and adaptive degradation defaults** - `22b3f997` (feat)
2. **Task 2: Spotlight query timing, idle pre-warming, and archive cap** - `a1fde24b` (feat)

## Files Created/Modified
- `extension/src/features/graph/graph/render/graph-profiler.ts` - Added sidepanelPaintMs, spotlightQueryMs to StartupMetrics, BUDGET_THRESHOLDS, checkBudget() method
- `extension/src/shared/types/flags.ts` - Changed adaptivePerformance default from false to true
- `extension/src/features/graph/graph/render/GraphPixiRenderer.ts` - Set LOD_HIDE_PX=4, LOD_CONN_HIDE_PX=6
- `extension/src/features/graph/components/graph/GraphArea.tsx` - Added NODE_COUNT_LOW_THRESHOLD, NODE_COUNT_DOT_THRESHOLD, node-count quality floor logic
- `extension/src/apps/sidepanel/ui/hooks/useBootstrap.ts` - Records sidepanel paint timing, fires spotlight pre-warm RPC
- `extension/src/background/services/spotlight.ts` - Instruments search() with query latency timing via perf-metrics
- `extension/src/background/services/spotlight-live-index.ts` - Added ARCHIVE_REBUILD_CAP=10, preWarm() method, archive sort+slice in rebuild
- `extension/src/shared/lib/perf-metrics.ts` - New lightweight metric recorder for service worker context

## Decisions Made
- Created a separate `perf-metrics.ts` singleton for the background service worker because `graph-profiler.ts` references `window` at module scope (for the `__graphMetrics` console API), making it incompatible with Chrome service workers
- Used fire-and-forget `SPOTLIGHT_BOOTSTRAP` RPC for pre-warming instead of adding a new `SPOTLIGHT_PREWARM` RPC method -- the bootstrap handler already calls `spotlightLiveIndex.getSnapshot()` which triggers `buildInitialIndex()`, achieving the same effect with zero new RPC plumbing
- Node-count quality floor merges with existing detailMode via `worstDetail()` function, ensuring overlay LOD and gesture overrides still take priority when they produce worse quality

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Created perf-metrics.ts for service worker context**
- **Found during:** Task 2 (Spotlight query timing)
- **Issue:** graph-profiler.ts uses `(window as any).__graphMetrics` at module scope, crashing in Chrome service worker context
- **Fix:** Created `extension/src/shared/lib/perf-metrics.ts` as lightweight metric recorder with budget breach logging
- **Files modified:** extension/src/shared/lib/perf-metrics.ts (created)
- **Verification:** TypeScript compiles cleanly
- **Committed in:** a1fde24b (Task 2 commit)

**2. [Rule 2 - Missing Critical] Used existing SPOTLIGHT_BOOTSTRAP RPC instead of new preWarm RPC**
- **Found during:** Task 2 (Trigger pre-warm from sidepanel)
- **Issue:** Adding a new RPC method requires changes across 4 files (contracts.ts, handlers, message types, response types). The plan suggested this but the existing SPOTLIGHT_BOOTSTRAP handler already builds the initial index
- **Fix:** Used `fireAndForget({ type: RPC_METHOD.SPOTLIGHT_BOOTSTRAP })` in the deferred boot path
- **Files modified:** extension/src/apps/sidepanel/ui/hooks/useBootstrap.ts
- **Verification:** TypeScript compiles cleanly, pre-warm triggers correctly
- **Committed in:** a1fde24b (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical)
**Impact on plan:** Both deviations improve the implementation. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Budget metrics and adaptive degradation foundation complete
- Ready for 07-02: search results virtualization and skeleton loading
- LOD and quality thresholds are active and can be tuned based on real-world telemetry

## Self-Check: PASSED

All 8 files verified present. Both commit hashes (22b3f997, a1fde24b) confirmed in git log. TypeScript compiles cleanly. All tests pass.

---
*Phase: 07-performance-budgets*
*Completed: 2026-03-21*
