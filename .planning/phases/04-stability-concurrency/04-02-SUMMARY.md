---
phase: 04-stability-concurrency
plan: 02
subsystem: ui
tags: [session-expired, sync-status, newtab, spotlight, sidepanel, auth, zustand]

# Dependency graph
requires:
  - phase: 03-ux-polish
    provides: error-to-toast layer and bootstrap recovery patterns
provides:
  - SESSION_EXPIRED banner in newtab with sign-in and dismiss
  - sessionExpiredFinal flag in useSpotlightSearch after recovery exhaustion
  - Sign-in link in spotlight (popup and embedded) when session expired
  - Sync status indicator in sidepanel header (syncing/offline/error)
  - Removed dead "degraded" NetworkStatus variant
affects: [05-privacy-logging, 06-perf-budgets]

# Tech tracking
tech-stack:
  added: []
  patterns: [authSessionItem.watch for cross-context session detection, inline styles for isolated UI surfaces]

key-files:
  created: []
  modified:
    - extension/src/apps/newtab/ui/NewTabApp.tsx
    - extension/src/features/spotlight/ui/useSpotlightSearch.ts
    - extension/src/features/spotlight/ui/SpotlightRoot.tsx
    - extension/src/apps/sidepanel/ui/components/Header.tsx
    - extension/src/apps/sidepanel/ui/state/store.ts
    - extension/src/apps/sidepanel/ui/styles/base.css

key-decisions:
  - "Newtab uses direct authSessionItem.watch instead of useAuthPortalFlow (not portable due to sidepanel store/QueryClient deps)"
  - "Sign-in opens account page in new tab rather than inline OAuth flow for newtab/spotlight"
  - "Sync indicator uses inline styles + CSS keyframes rather than adding new CSS class system"
  - "Removed 'degraded' from NetworkStatus since it was never assigned anywhere in the codebase"

patterns-established:
  - "authSessionItem.watch pattern for detecting session expiry in non-sidepanel contexts"
  - "Dynamic import of backend config for lazy initialization in UI event handlers"

requirements-completed: [STAB-06, HYG-04]

# Metrics
duration: 6min
completed: 2026-03-21
---

# Phase 04 Plan 02: Session Expired Surfaces + Sync Status Summary

**SESSION_EXPIRED banners in newtab and spotlight with sign-in actions, plus sync status indicator in sidepanel header showing syncing/offline/error state**

## Performance

- **Duration:** 6 min
- **Started:** 2026-03-21T15:38:53Z
- **Completed:** 2026-03-21T15:45:04Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Newtab shows a compact session-expired banner with sign-in button and dismiss when auth session is missing or expired
- Spotlight surfaces "Session expired" with sign-in link after all 3 recovery retries exhaust (both popup and embedded)
- Sidepanel header shows sync status indicator (Loader2 spinner for syncing, CloudOff for offline, AlertTriangle for error) next to settings gear
- Removed dead "degraded" variant from NetworkStatus type

## Task Commits

Each task was committed atomically:

1. **Task 1: SESSION_EXPIRED handling in newtab and spotlight** - `8603bb89` (feat)
2. **Task 2: Sync status indicator in sidepanel header** - `7cae4683` (feat)

## Files Created/Modified
- `extension/src/apps/newtab/ui/NewTabApp.tsx` - Added session expired banner with authSessionItem.watch, sign-in handler, and session expired state in search results
- `extension/src/features/spotlight/ui/useSpotlightSearch.ts` - Added sessionExpiredFinal flag set after recovery retries exhaust on SESSION_EXPIRED error
- `extension/src/features/spotlight/ui/SpotlightRoot.tsx` - Added sign-in link when sessionExpiredFinal is true, imported browser for tabs.create
- `extension/src/apps/sidepanel/ui/components/Header.tsx` - Added sync status indicator with computed state from syncStatus + network
- `extension/src/apps/sidepanel/ui/state/store.ts` - Removed "degraded" from NetworkStatus type
- `extension/src/apps/sidepanel/ui/styles/base.css` - Added sync-indicator-spin keyframes animation

## Decisions Made
- Newtab uses direct authSessionItem.watch instead of useAuthPortalFlow (the hook depends on sidepanel-specific Zustand store and QueryClient, not portable)
- Sign-in action opens account page in a new tab via dynamic import of backend config (lazy init avoids loading backend module at startup)
- Sync indicator uses inline styles on the span element, with CSS keyframes for the spin animation in base.css
- Removed "degraded" from NetworkStatus type -- confirmed no code anywhere assigns network to "degraded"

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added spin keyframes for sync indicator**
- **Found during:** Task 2
- **Issue:** The existing `.spin` class is scoped to `.trees-dropdown-item .spin` and does not apply to the header sync indicator
- **Fix:** Added `@keyframes sync-indicator-spin` in base.css and referenced it via inline style on the Loader2 icon
- **Files modified:** extension/src/apps/sidepanel/ui/styles/base.css
- **Verification:** Typecheck passes, animation rule is present
- **Committed in:** 7cae4683

**2. [Rule 2 - Missing Critical] Reset sessionExpiredFinal on retryBootstrap and close**
- **Found during:** Task 1
- **Issue:** Plan only specified resetting sessionExpiredFinal on successful bootstrap, but it should also reset when user explicitly retries or when spotlight closes
- **Fix:** Added setSessionExpiredFinal(false) in retryBootstrap callback and dispose-on-close effect
- **Files modified:** extension/src/features/spotlight/ui/useSpotlightSearch.ts
- **Verification:** State resets properly, no stale expired flag after retry/close
- **Committed in:** 8603bb89

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 missing critical)
**Impact on plan:** Both auto-fixes necessary for correctness. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All session expired surfaces wired for newtab, spotlight popup, and embedded spotlight
- Sync status indicator ready for sidepanel header
- Phase 04 complete -- ready for Phase 05 (privacy-logging)

## Self-Check: PASSED

All files exist, all commits verified.

---
*Phase: 04-stability-concurrency*
*Completed: 2026-03-21*
