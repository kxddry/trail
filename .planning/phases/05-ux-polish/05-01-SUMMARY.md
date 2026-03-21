---
phase: 05-ux-polish
plan: 01
subsystem: ui
tags: [react, hooks, accessibility, dropdown, overlay, keyboard-hints]

requires: []
provides:
  - "useOverlayBehavior shared hook for Esc/click-outside/focus-return/inert"
  - "Unified overlay behavior across all dropdown components"
  - "Keyboard hints bar in FloatingSearch"
affects: [05-ux-polish, any-new-dropdown-components]

tech-stack:
  added: []
  patterns: [shared-overlay-hook, inert-sibling-management, inline-keyboard-hints]

key-files:
  created:
    - extension/src/apps/sidepanel/ui/hooks/useOverlayBehavior.ts
  modified:
    - extension/src/apps/sidepanel/ui/components/SettingsPopover.tsx
    - extension/src/apps/sidepanel/ui/components/TreeDropdown.tsx
    - extension/src/apps/sidepanel/ui/components/tags/TagFilterDropdown.tsx
    - extension/src/apps/sidepanel/ui/components/FloatingSearch.tsx

key-decisions:
  - "Inert management scoped to .floating-island siblings within .floating-controls"
  - "skipEscWhenEditing option for dropdowns with input fields (Trees, Tags)"
  - "Keyboard hints use inline styles matching existing pattern (ErrorBoundary)"
  - "UXP-03 confirmed working by code inspection -- no changes needed"

patterns-established:
  - "useOverlayBehavior: all new dropdowns must use this hook instead of inline Esc/click-outside handlers"
  - "Focus return on close: triggerRef receives focus when dropdown transitions open->closed"

requirements-completed: [UXP-01, UXP-02, UXP-03]

duration: 4min
completed: 2026-03-21
---

# Phase 05 Plan 01: Overlay Behavior Unification Summary

**Shared useOverlayBehavior hook with Esc/click-outside/focus-return/inert, retrofitted across Settings/Trees/Tags dropdowns, keyboard hints in search**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-21T16:14:18Z
- **Completed:** 2026-03-21T16:18:42Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- Created `useOverlayBehavior` hook extracting duplicated overlay logic from three dropdown components
- All dropdowns now have consistent Esc dismiss, click-outside close, focus return to trigger, and inert sibling management
- FloatingSearch shows inline keyboard hints (Enter/arrows/Esc) when expanded and focused
- UXP-03 verified: blur preserves draft text, only explicit Esc clears it

## Task Commits

Each task was committed atomically:

1. **Task 1: Create useOverlayBehavior hook and retrofit all dropdowns** - `996b7537` (feat)
2. **Task 2: Add keyboard hints to FloatingSearch and verify UXP-03** - `e70bd193` (feat)

Note: SettingsPopover changes were captured in `248f3e0d` by a parallel executor that also modified the file.

## Files Created/Modified
- `extension/src/apps/sidepanel/ui/hooks/useOverlayBehavior.ts` - Shared hook: Esc handler, click-outside, focus return, inert sibling management
- `extension/src/apps/sidepanel/ui/components/SettingsPopover.tsx` - Replaced inline effects with useOverlayBehavior
- `extension/src/apps/sidepanel/ui/components/TreeDropdown.tsx` - Replaced inline effects with useOverlayBehavior (skipEscWhenEditing)
- `extension/src/apps/sidepanel/ui/components/tags/TagFilterDropdown.tsx` - Replaced inline effects with useOverlayBehavior, kept Enter handler as separate effect
- `extension/src/apps/sidepanel/ui/components/FloatingSearch.tsx` - Added keyboard hints bar (Enter next, arrows navigate, Esc close)

## Decisions Made
- Inert management targets `.floating-island` siblings within `.floating-controls` rather than arbitrary DOM siblings -- scoped to the correct UI region
- `skipEscWhenEditing` defaults to false; enabled for TreeDropdown and TagFilterDropdown which contain input fields for rename/filter
- Keyboard hints use inline styles matching the established pattern (ErrorBoundary, DegradedBootstrap)
- UXP-03 (blur preserves draft) confirmed as pre-existing correct behavior by code inspection -- no changes needed

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- SettingsPopover changes were already committed by a parallel executor (plan 06-03) that touched the same file. My commit captured TreeDropdown, TagFilterDropdown, and the new hook. The final state is correct across all files.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None - all functionality is fully wired.

## Next Phase Readiness
- All dropdown components now use a single shared overlay hook
- Any new dropdown/popover components should import `useOverlayBehavior` for consistent behavior
- Search keyboard hints are visible and auto-hide correctly

## Self-Check: PASSED

- useOverlayBehavior.ts: FOUND
- 05-01-SUMMARY.md: FOUND
- Commit 996b7537: FOUND
- Commit e70bd193: FOUND

---
*Phase: 05-ux-polish*
*Completed: 2026-03-21*
