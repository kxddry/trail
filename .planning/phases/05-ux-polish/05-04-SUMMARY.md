---
phase: 05-ux-polish
plan: 04
subsystem: ui
tags: [react, chrome-extension, onboarding, privacy, settings, storage]

# Dependency graph
requires:
  - phase: 05-01
    provides: "useOverlayBehavior hook and unified overlay patterns"
  - phase: 05-03
    provides: "Session banner storage pattern and App.tsx structure"
provides:
  - "Collapsible 'Your data' privacy section in Settings"
  - "First-run onboarding hints with 3 coach marks"
  - "hasSeenOnboardingItem storage flag for onboarding persistence"
affects: [sidepanel, settings]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Collapsible accordion section in settings with chevron rotation"
    - "First-run overlay with storage-backed dismiss persistence"

key-files:
  created:
    - "extension/src/apps/sidepanel/ui/components/OnboardingHints.tsx"
  modified:
    - "extension/src/apps/sidepanel/ui/components/SettingsPopover.tsx"
    - "extension/src/apps/sidepanel/ui/App.tsx"
    - "extension/src/shared/config/storage-items.ts"

key-decisions:
  - "Your data section uses expandable accordion with chevron rotation (matches existing theme studio pattern)"
  - "OnboardingHints positions via getBoundingClientRect with 300ms delay for FloatingControls render"
  - "Click-anywhere or Got it button dismisses all hints simultaneously"
  - "Graceful degradation: hints with missing target elements simply don't render"

patterns-established:
  - "Settings accordion: collapsible sections with Icons.ChevronRight rotation and inline styles"
  - "First-run overlay: storage flag check on mount, fixed position hints, single dismiss action"

requirements-completed: [UXP-07, UXP-08]

# Metrics
duration: 2min
completed: 2026-03-21
---

# Phase 05 Plan 04: Settings Privacy & Onboarding Hints Summary

**Collapsible 'Your data' privacy section in settings showing cloud vs local breakdown, plus first-run onboarding overlay with 3 coach marks (search, tree switch, tag filter)**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-21T16:29:10Z
- **Completed:** 2026-03-21T16:31:17Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- Settings popover has a collapsible "Your data" section explaining synced-to-cloud (trees, tags, settings) vs stays-local (layout cache, theme, search history)
- First-run sidepanel shows 3 tooltip-style coach marks pointing at search orb, tree switch, and tag filter
- Single dismiss action (Got it button or click-anywhere) sets persistent storage flag so hints never reappear

## Task Commits

Each task was committed atomically:

1. **Task 1: Add "Your data" privacy section to Settings** - `0788fa73` (feat)
2. **Task 2: Create first-run onboarding hints** - `892d5199` (feat)

## Files Created/Modified
- `extension/src/apps/sidepanel/ui/components/SettingsPopover.tsx` - Added collapsible "your data" accordion after dashboard section with cloud/local data breakdown
- `extension/src/apps/sidepanel/ui/components/OnboardingHints.tsx` - New component: first-run overlay with 3 positioned coach marks and Got it dismiss button
- `extension/src/apps/sidepanel/ui/App.tsx` - Wired OnboardingHints after FloatingControls
- `extension/src/shared/config/storage-items.ts` - Added hasSeenOnboardingItem (local boolean, fallback false)

## Decisions Made
- Your data section placed after dashboard and before experiments -- logically groups user-facing info before dev tools
- OnboardingHints uses 300ms setTimeout in useLayoutEffect to ensure FloatingControls buttons are rendered before measuring positions
- Hints with width === 0 (target not found) gracefully skip rendering instead of showing broken tooltips
- Click-anywhere dismiss via container onClick keeps UX simple -- no need to dismiss individually

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all functionality is fully wired.

## Next Phase Readiness
- Phase 05 (ux-polish) is fully complete with all 4 plans executed
- Settings privacy section and onboarding hints are self-contained UI additions
- No blockers for subsequent phases

## Self-Check: PASSED

- SettingsPopover.tsx: FOUND
- OnboardingHints.tsx: FOUND
- App.tsx: FOUND
- storage-items.ts: FOUND
- 05-04-SUMMARY.md: FOUND
- Commit 0788fa73: FOUND
- Commit 892d5199: FOUND

---
*Phase: 05-ux-polish*
*Completed: 2026-03-21*
