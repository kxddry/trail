---
phase: 05-ux-polish
plan: 03
subsystem: ui
tags: [react, chrome-extension, session-storage, empty-state, sidepanel]

# Dependency graph
requires: []
provides:
  - "New tab empty state with sidepanel CTA"
  - "Persistent session banner dismiss via chrome.storage.session"
affects: [newtab, sidepanel]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Session-scoped storage for ephemeral UI dismiss state"
    - "Empty state pattern for dashboard with CTA fallback"

key-files:
  created: []
  modified:
    - "extension/src/apps/newtab/ui/DashboardView.tsx"
    - "extension/src/apps/sidepanel/ui/components/SessionExpiredBanner.tsx"
    - "extension/src/apps/sidepanel/ui/App.tsx"
    - "extension/src/shared/config/storage-items.ts"

key-decisions:
  - "Empty state uses inline styles matching existing pattern in DashboardView"
  - "SessionExpiredBanner uses session-scoped storage (auto-clears on browser restart)"
  - "App.tsx clears dismiss flag when auth restored for proper re-display on next expiry"

patterns-established:
  - "Session-scoped storage for UI dismiss persistence: define item with session: prefix, load on mount, watch for cross-instance sync"

requirements-completed: [UXP-06, UXP-09]

# Metrics
duration: 4min
completed: 2026-03-21
---

# Phase 05 Plan 03: Empty State & Banner Persistence Summary

**New tab empty state with layers icon and sidepanel CTA; session banner dismiss persisted to chrome.storage.session with auth-restoration reset**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-21T16:14:18Z
- **Completed:** 2026-03-21T16:18:34Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- New tab dashboard shows centered empty state (icon, text, CTA) when all cards return empty data
- SessionExpiredBanner dismiss persists across panel close/reopen within a browser session
- Banner reappears on next session expiry after auth is restored (dismiss flag cleared in App.tsx)

## Task Commits

Each task was committed atomically:

1. **Task 1: Add new tab empty state** - `38228d19` (feat)
2. **Task 2: Make SessionExpiredBanner dismiss persistent** - `a88df1fd` (feat)
3. **Task 2 fix: Move useEffect before early return** - `6a6c4099` (fix)

## Files Created/Modified
- `extension/src/apps/newtab/ui/DashboardView.tsx` - Added EmptyState component with layers icon SVG, explanatory text, and Open Sidepanel CTA button
- `extension/src/shared/config/storage-items.ts` - Added sessionBannerDismissedItem (session-scoped boolean)
- `extension/src/apps/sidepanel/ui/components/SessionExpiredBanner.tsx` - Replaced in-memory useState with session storage-backed dismiss with load, watch, and persist
- `extension/src/apps/sidepanel/ui/App.tsx` - Added useEffect to clear dismiss flag when auth is restored

## Decisions Made
- Used inline styles for empty state, matching existing DashboardView and DegradedBootstrap patterns
- Session-scoped storage auto-clears on browser restart -- no manual cleanup needed
- Auth-restoration reset lives in App.tsx (parent) rather than SessionExpiredBanner because the banner unmounts when session is valid

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] useEffect called after early return in App.tsx**
- **Found during:** Task 2 (verification - lint check)
- **Issue:** The useEffect for clearing session banner dismiss was placed after the `bootstrapStatus === "degraded"` early return, violating React hooks rules
- **Fix:** Moved useEffect above the early return so hooks are called unconditionally
- **Files modified:** extension/src/apps/sidepanel/ui/App.tsx
- **Verification:** `npm run lint` passes with 0 errors
- **Committed in:** `6a6c4099`

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Essential fix for React hooks rules compliance. No scope creep.

## Issues Encountered
- sessionBannerDismissedItem in storage-items.ts was already present from a parallel plan execution -- no duplicate definition needed

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Empty state and banner persistence are self-contained UI improvements
- No blockers for subsequent plans

## Self-Check: PASSED

All 5 files verified present. All 3 commits verified in history.

---
*Phase: 05-ux-polish*
*Completed: 2026-03-21*
