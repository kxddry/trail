---
phase: 04-graph-startup-optimization-without-blocking-first-paint
plan: 01
subsystem: graph-layout
tags: [layout-cache, signature, offscreen-worker, chrome-extension, session-storage]

requires:
  - phase: 03-ux-polish
    provides: settings UI and graph density controls
provides:
  - layoutSignature field on CachedLayoutResult for stale-cache prevention
  - computeLayoutSignature function for deterministic param encoding
  - Signature-validated cache reads that reject mismatched entries
  - Offscreen worker settings-change recomputation
affects: [04-02, 04-03, graph-startup]

tech-stack:
  added: []
  patterns: [signature-based cache invalidation, deterministic string keys from config params]

key-files:
  created:
    - extension/tests/layout-signature.test.ts
  modified:
    - extension/src/shared/graph-layout-cache/types.ts
    - extension/src/shared/graph-layout-cache/cache.ts
    - extension/src/shared/graph-layout-cache/compute-layout.ts
    - extension/src/entrypoints/offscreen-graph/main.ts

key-decisions:
  - "Simplified storageKey to use layoutSignature string instead of individual mode/collapse/recency params -- cleaner and extensible"
  - "Base-key fallback validates layoutSignature match before returning -- prevents serving stale positions from different settings"
  - "cachedTreeJSON stored in offscreen worker to enable recomputation on SAVE_SETTINGS without re-fetching tree"

patterns-established:
  - "Layout signature pattern: concatenate all position-affecting params into deterministic pipe-delimited string"
  - "Dual-key cache write: exact signature key + base fallback key for consumers that don't know state yet"

requirements-completed: [PERF-02, PERF-03]

duration: 5min
completed: 2026-03-19
---

# Phase 04 Plan 01: Layout Signature Cache Summary

**Deterministic layout signature on CachedLayoutResult with signature-validated reads and offscreen worker settings-change recomputation**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-19T07:15:22Z
- **Completed:** 2026-03-19T07:21:06Z
- **Tasks:** 2
- **Files modified:** 4 (+ 1 test file created)

## Accomplishments
- Layout cache entries now include a layoutSignature encoding mode, density, gap scales, radial params, collapse state, and recency ordering
- Cache reads with a signature parameter reject entries whose signature does not match, preventing stale position delivery
- Offscreen worker immediately recomputes layout when settings change (not just on next TREE_UPDATED)
- 6 passing tests for computeLayoutSignature determinism and differentiation

## Task Commits

Each task was committed atomically:

1. **Task 1 (RED): Failing tests for layout signature** - `0237df82` (test)
2. **Task 1 (GREEN): Layout signature implementation** - `a2f987c0` (feat)
3. **Task 2: Offscreen worker recompute on settings change** - `ad47bfc8` (feat)

_Note: Task 1 followed TDD with RED/GREEN commits._

## Files Created/Modified
- `extension/tests/layout-signature.test.ts` - 6 tests for computeLayoutSignature determinism and differentiation
- `extension/src/shared/graph-layout-cache/types.ts` - Added layoutSignature field to CachedLayoutResult, exported computeLayoutSignature function
- `extension/src/shared/graph-layout-cache/cache.ts` - Simplified storageKey to use signature, added signature validation on fallback reads
- `extension/src/shared/graph-layout-cache/compute-layout.ts` - Computes layoutSignature from settings and includes in return object
- `extension/src/entrypoints/offscreen-graph/main.ts` - Caches tree JSON, recomputes layout on SAVE_SETTINGS

## Decisions Made
- Simplified storageKey to use the full layoutSignature string instead of individual mode/collapse/recency params. This is cleaner and automatically extends when new settings are added to the signature.
- Base-key fallback validates layoutSignature match before returning, ensuring stale positions from different settings are never served.
- cachedTreeJSON stored in offscreen worker state so SAVE_SETTINGS can trigger immediate recomputation without re-fetching the tree from background.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Layout signature infrastructure ready for plans 04-02 and 04-03 to consume
- readLayoutCache callers can now optionally pass layoutSignature for precise cache hits
- Offscreen worker keeps cache fresh across settings changes

---
*Phase: 04-graph-startup-optimization-without-blocking-first-paint*
*Completed: 2026-03-19*
