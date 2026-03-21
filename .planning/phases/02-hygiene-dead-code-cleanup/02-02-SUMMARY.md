---
phase: 02-hygiene-dead-code-cleanup
plan: 02
subsystem: testing
tags: [architecture-boundaries, dead-code, hygiene, cleanup]

requires:
  - phase: 02-hygiene-dead-code-cleanup
    provides: "Dead code deletion from plan 01 (AuthGate, WelcomeGate, runtime-logger)"
provides:
  - "Architecture-boundaries test hardened with 10 new FORBIDDEN_PATHS entries"
  - "Dead code audit confirming zero remaining orphaned UX surfaces"
  - "7 orphaned .tsx/.ts components removed (682 lines deleted)"
affects: [03-ui-consistency, 04-stability-hardening]

tech-stack:
  added: []
  patterns: ["FORBIDDEN_PATHS regression guard for deleted code"]

key-files:
  created: []
  modified:
    - "extension/tests/architecture-boundaries.test.ts"

key-decisions:
  - "Deleted src/shared/debug/runtime-logger.ts inline (0 callers, blocking test) even though 02-01 plan also targeted it"
  - "Deleted 7 orphaned UX surfaces found by audit rather than deferring to future phase"
  - "Left orphaned exports in entitlements.ts, logger.ts, navigation.ts undisturbed (utility/type files, low runtime cost)"

patterns-established:
  - "FORBIDDEN_PATHS: Every deleted code path gets added to prevent regression"

requirements-completed: [HYG-01, QA-04, QA-06]

duration: 5min
completed: 2026-03-20
---

# Phase 02 Plan 02: Hygiene & Dead Code Cleanup Summary

**Deleted dev artifact dirs (logs/), hardened architecture-boundaries test with 10 new forbidden paths, and removed 7 orphaned UX components (682 lines) via dead code audit**

## Performance

- **Duration:** 5 min
- **Started:** 2026-03-20T18:11:26Z
- **Completed:** 2026-03-20T18:16:35Z
- **Tasks:** 2
- **Files modified:** 8

## Accomplishments
- Deleted extension/logs/ and logs/ dev artifact directories
- Added AuthGate.tsx, WelcomeGate.tsx, src/shared/debug to FORBIDDEN_PATHS to guard against regression of 02-01 deletions
- Dead code audit found and removed 7 orphaned UX surfaces: BookmarksBar, SearchBar, TabInfo, demo, sidebar, sidebar-utils, liquid-glass
- All 10 new FORBIDDEN_PATHS entries prevent deleted code from reappearing
- Architecture-boundaries test passes cleanly (root hygiene, thin entrypoints, import boundaries)

## Task Commits

Each task was committed atomically:

1. **Task 1: Delete logs/ directories and harden architecture-boundaries test** - `9fe5cd94` (chore)
2. **Task 2: Dead code audit -- remove 7 orphaned UX surfaces** - `239cdef5` (chore)

## Files Created/Modified
- `extension/tests/architecture-boundaries.test.ts` - Added 10 entries to FORBIDDEN_PATHS array
- `extension/src/apps/newtab/ui/BookmarksBar.tsx` - DELETED (superseded by DashboardView BookmarksCard)
- `extension/src/apps/sidepanel/ui/components/SearchBar.tsx` - DELETED (replaced by FloatingSearch)
- `extension/src/apps/sidepanel/ui/components/TabInfo.tsx` - DELETED (0 importers)
- `extension/src/apps/sidepanel/ui/components/ui/demo.tsx` - DELETED (Aceternity UI demo, never wired)
- `extension/src/apps/sidepanel/ui/components/ui/sidebar.tsx` - DELETED (only used by demo.tsx)
- `extension/src/apps/sidepanel/ui/components/ui/sidebar-utils.ts` - DELETED (only used by sidebar.tsx)
- `extension/src/ui/components/liquid-glass.tsx` - DELETED (experimental, 0 importers)

## Decisions Made
- Deleted `src/shared/debug/runtime-logger.ts` inline because it was blocking the architecture-boundaries test (0 callers confirmed). Plan 02-01 also targets this file but runs in parallel.
- Deleted 7 orphaned UX surfaces found during audit (all with 0 importers, confirmed dead) rather than deferring.
- Left orphaned exports in `entitlements.ts` (billing utils), `logger.ts` (createLogger), and `navigation.ts` (SidebarNavigationKey utils) undisturbed -- these are utility/type modules with low runtime cost and potential future use.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Deleted extension/src/shared/debug/runtime-logger.ts**
- **Found during:** Task 1 (architecture-boundaries test run)
- **Issue:** Adding `src/shared/debug` to FORBIDDEN_PATHS caused test failure because the directory still existed with runtime-logger.ts (0 callers)
- **Fix:** Deleted the directory and file (confirmed dead code with zero imports anywhere in codebase)
- **Files modified:** extension/src/shared/debug/runtime-logger.ts (deleted)
- **Verification:** Architecture-boundaries test passes
- **Committed in:** 9fe5cd94 (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary to unblock test passage. File was confirmed dead code targeted by parallel plan 02-01.

## Issues Encountered
None.

## Dead Code Audit Findings

### Component Audit (extension/src/apps/, features/, ui/)

| File | Status | Reason |
|------|--------|--------|
| BookmarksBar.tsx | DELETED | Superseded by inline BookmarksCard in DashboardView.tsx |
| SearchBar.tsx | DELETED | Replaced by FloatingSearch.tsx, 0 importers |
| TabInfo.tsx | DELETED | 0 importers anywhere in codebase |
| demo.tsx | DELETED | Aceternity UI sidebar demo, never wired into app |
| sidebar.tsx | DELETED | Only consumer was demo.tsx |
| sidebar-utils.ts | DELETED | Only consumer was sidebar.tsx |
| liquid-glass.tsx | DELETED | Experimental glassmorphism component, 0 importers |

### Shared Module Audit (extension/src/shared/)

| Export | File | Status | Reason |
|--------|------|--------|--------|
| hasTierAccess, resolveCurrentTier, getFeatureMinTier, getFeatureAccess | entitlements.ts | KEPT | Billing utilities, potential future use |
| createLogger | logger.ts | KEPT | Logging utility, potential future use |
| newSidebarNavigationKey, parseSidebarNavigationKey | navigation.ts | KEPT | Type/utility file, low runtime cost |

### Entrypoint Root Components (Confirmed Active)

All entrypoint-mounted root components verified as actively wired:
- AccountApp.tsx (account/main.tsx)
- NewTabApp.tsx (newtab/main.tsx)
- ErrorBoundary.tsx (fullview/main.tsx, spotlight-graph/main.tsx)
- SpotlightGraphApp.tsx (spotlight-graph/main.tsx)
- sidepanel/ui/main.tsx (sidepanel/main.tsx)
- content-ui/mount.tsx (content.ts)

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Architecture-boundaries test is hardened with comprehensive FORBIDDEN_PATHS coverage
- All orphaned UX surfaces removed, release package is clean
- Ready for phase 03 (UI consistency) and beyond

## Self-Check: PASSED

All files verified (8 created/modified/deleted as claimed). Both commits (9fe5cd94, 239cdef5) confirmed in git log. All directories confirmed deleted.

---
*Phase: 02-hygiene-dead-code-cleanup*
*Completed: 2026-03-20*
