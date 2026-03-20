---
phase: 04-graph-startup-optimization-without-blocking-first-paint
plan: 03
subsystem: ui
tags: [pixi, performance, profiling, cache-validation, layout-signature]

requires:
  - phase: 04-01
    provides: "layoutSignature field on CachedLayoutResult, computeLayoutSignature function"
  - phase: 04-02
    provides: "bootstrapGraph store action, prefetched layout cache infrastructure"
provides:
  - "Startup instrumentation with 6 metrics: bootstrapMs, firstRenderMs, layoutMs, cacheHitType, nodeCount, layoutMode"
  - "Signature-validated cache hydration in GraphCanvas (replaces field-by-field validation)"
  - "STARTUP_T0 timing origin for graph startup measurements"
  - "window.__graphMetrics() console API with startup metrics table"
affects: [graph-rendering, performance-monitoring]

tech-stack:
  added: []
  patterns: ["one-shot startup metrics alongside sliding-window phase metrics", "module-level timing origin for startup measurement"]

key-files:
  created: []
  modified:
    - "extension/src/entrypoints/sidepanel/ui/graph/render/graph-profiler.ts"
    - "extension/src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx"

key-decisions:
  - "STARTUP_T0 captured at module load before class definition for earliest possible timing"
  - "EMPTY_STARTUP constant shared between constructor and reset() to avoid duplication"
  - "Fallback path preserved for old cache entries without layoutSignature field"
  - "settings added to layout useMemo dependency array since signature computation reads settings.layout and settings.graphDensity"

patterns-established:
  - "One-shot startup metrics pattern: record once per graph surface open, separate from sliding-window phase metrics"
  - "Module-level boolean flags for one-shot recording (_bootstrapRecorded, firstRenderRecordedRef)"

requirements-completed: [PERF-05]

duration: 4min
completed: 2026-03-19
---

# Phase 04 Plan 03: Startup Instrumentation and Signature Cache Validation Summary

**Graph profiler extended with 6 startup metrics and GraphCanvas cache hydration now validates against layoutSignature with fallback for old format**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-19T07:25:57Z
- **Completed:** 2026-03-19T07:30:10Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Extended GraphProfiler with one-shot startup metrics (bootstrapMs, firstRenderMs, layoutMs, cacheHitType, nodeCount, layoutMode)
- Replaced field-by-field cache validation in GraphCanvas with full layoutSignature comparison
- Added backward-compatible fallback path for old cache entries without layoutSignature
- window.__graphMetrics() now reports both per-phase stats and startup metrics tables

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend graph-profiler with startup metrics** - `d8c84b19` (feat)
2. **Task 2: Update GraphCanvas cache hydration to use layoutSignature and record startup timing** - `108c5bf0` (feat)

## Files Created/Modified
- `extension/src/entrypoints/sidepanel/ui/graph/render/graph-profiler.ts` - Added STARTUP_T0, StartupMetrics/CacheHitType types, recordStartup/getStartupMetrics methods, updated console API
- `extension/src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx` - Signature-validated cache hydration, bootstrap/firstRender/layout timing, startup metric recording on all paths

## Decisions Made
- STARTUP_T0 placed before class definition for earliest possible timing capture
- EMPTY_STARTUP constant shared between constructor init and reset() to prevent object shape drift
- Fallback path preserved for old cache entries that lack layoutSignature (graceful migration)
- Added `settings` to layout useMemo deps since we now read `settings.layout` and `settings.graphDensity` for signature computation

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 04 fully complete: all 3 plans executed
- Graph startup optimization pipeline complete: cache prefetch (01), storage/retrieval (02), and instrumentation/validation (03)
- Startup metrics accessible via window.__graphMetrics() for ongoing performance monitoring

## Self-Check: PASSED

All files and commits verified:
- graph-profiler.ts: FOUND
- GraphCanvas.tsx: FOUND
- 04-03-SUMMARY.md: FOUND
- Commit d8c84b19: FOUND
- Commit 108c5bf0: FOUND

---
*Phase: 04-graph-startup-optimization-without-blocking-first-paint*
*Completed: 2026-03-19*
