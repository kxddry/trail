---
phase: 03-error-handling-recovery
plan: 03
subsystem: ui
tags: [sonner, toast, cache, offscreen, quota, error-handling, recovery]

# Dependency graph
requires:
  - phase: 03-01
    provides: "showOperationError helper for centralized error-to-toast conversion"
provides:
  - "Cache corruption recovery with surgical invalidation and toast"
  - "Offscreen layout fallback notification via notifyUi"
  - "Quota eviction toast with evicted tree name"
  - "Stub tree unavailable state (CloudOff icon, non-clickable, unavailable label)"
affects: [03-error-handling-recovery]

# Tech tracking
tech-stack:
  added: []
  patterns: ["try/catch around hydrateFromCache with surgical invalidateLayoutCache", "notifyUi for background-to-UI toast notifications", "unavailableTreeIds state for failed stub tree loads"]

key-files:
  created: []
  modified:
    - "extension/src/features/graph/components/graph/GraphCanvas.tsx"
    - "extension/src/background/services/offscreen-graph-manager.ts"
    - "extension/src/background/services/quota-manager.ts"
    - "extension/src/apps/sidepanel/ui/components/TreeDropdown.tsx"
    - "extension/src/apps/sidepanel/ui/components/Icon.ts"

key-decisions:
  - "Used existing notifyUi/rpc.notify pattern for background-to-UI toasts rather than new RPC method"
  - "Offscreen failure toast fires once per session via offscreenFailNotified flag"
  - "Unavailable stub trees prevent click rather than showing error on repeated attempts"

patterns-established:
  - "notifyUi({ message, icon, durationMs }) for background service -> sidepanel toast notifications"
  - "unavailableTreeIds Set state for tracking failed stub loads in TreeDropdown"

requirements-completed: [STAB-04, STAB-05, STAB-09, HYG-06]

# Metrics
duration: 6min
completed: 2026-03-21
---

# Phase 03 Plan 03: Bootstrap Recovery Summary

**Cache corruption auto-reset with surgical invalidation, offscreen fallback toast, quota eviction notification with tree name, and stub-tree unavailable state with CloudOff icon**

## Performance

- **Duration:** 6 min 15s
- **Started:** 2026-03-21T09:47:22Z
- **Completed:** 2026-03-21T09:53:37Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Wrapped both `hydrateFromCache` call sites in try/catch with `toast.warning` and surgical `invalidateLayoutCache` cleanup
- Added one-time offscreen fallback toast via `notifyUi` when offscreen document creation fails in background
- Added quota eviction notification using existing `notifyUi`/`rpc.notify` pattern with evicted tree label
- Implemented `unavailableTreeIds` state in TreeDropdown for stub trees that fail to load from cloud
- Unavailable stubs render CloudOff icon, "unavailable" meta label, and are non-clickable

## Task Commits

Each task was committed atomically:

1. **Task 1: Add cache corruption recovery and offscreen fallback toast** - `05864954` (feat)
2. **Task 2: Add quota eviction toast and stub-tree error handling** - `804d91c1` (feat)

## Files Created/Modified
- `extension/src/features/graph/components/graph/GraphCanvas.tsx` - try/catch around hydrateFromCache with toast + invalidateLayoutCache
- `extension/src/background/services/offscreen-graph-manager.ts` - notifyUi warning on offscreen document creation failure
- `extension/src/background/services/quota-manager.ts` - notifyUi toast after archive eviction with tree label
- `extension/src/apps/sidepanel/ui/components/TreeDropdown.tsx` - unavailableTreeIds state, ensureTreeLoaded catch, CloudOff icon, non-clickable unavailable stubs
- `extension/src/apps/sidepanel/ui/components/Icon.ts` - Added CloudOff to lucide-react icon exports

## Decisions Made
- Used existing `notifyUi`/`rpc.notify` pattern for background-to-UI toasts (quota eviction and offscreen failure) rather than creating a new RPC notification type
- Offscreen failure notification fires only once per session via `offscreenFailNotified` flag to avoid toast spam on repeated attempts
- Unavailable stub trees prevent click entirely rather than allowing repeated failed attempts — the error is shown once via `showOperationError` and the tree is marked unavailable

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Added optional chaining for _prefetchedLayout after catch block**
- **Found during:** Task 1 (Cache corruption recovery)
- **Issue:** After the first try/catch could set `_prefetchedLayout = null`, the second `if` block accessed `_prefetchedLayout.layoutMode` which could NPE
- **Fix:** Changed to `_prefetchedLayout?.layoutMode` for safety
- **Files modified:** extension/src/features/graph/components/graph/GraphCanvas.tsx
- **Verification:** TypeScript compiles cleanly
- **Committed in:** 05864954 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Essential for correctness when cache corruption sets _prefetchedLayout to null. No scope creep.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 03 (error-handling-recovery) fully complete: error-to-toast layer, sync retry, and bootstrap recovery all implemented
- All catch blocks wired to user-visible notifications
- Background-to-UI notification pattern established for future use

## Self-Check: PASSED

All files and commits verified.

---
*Phase: 03-error-handling-recovery*
*Completed: 2026-03-21*
