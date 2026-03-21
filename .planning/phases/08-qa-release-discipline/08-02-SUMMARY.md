---
phase: 08-qa-release-discipline
plan: 02
subsystem: testing
tags: [release-process, qa, checklist, chrome-web-store, manual-testing]

requires:
  - phase: 03-error-resilience-layer
    provides: "Cache corruption recovery, bootstrap degraded state, toast layer"
  - phase: 04-sync-session-awareness
    provides: "Sync indicator, session expiry handling, editor mode persistence"
  - phase: 05-ui-consistency-pass
    provides: "Onboarding hints, empty states, export/import, session banner"
  - phase: 06-security-privacy-audit
    provides: "Manifest permission audit, structured logging"
provides:
  - "Comprehensive release checklist for Chrome Web Store submission"
  - "Cold profile (first install) verification path"
  - "Dirty returning user verification path"
  - "54 actionable checkbox items across 9 verification sections"
affects: [release-process, qa-automation]

tech-stack:
  added: []
  patterns: ["release-checklist-as-document"]

key-files:
  created:
    - "extension/RELEASE-CHECKLIST.md"
  modified: []

key-decisions:
  - "Documented actual manifest permissions (9 total) matching wxt.config.ts"
  - "Split pre-submission into separate Cold Profile and Dirty profile signoff lines"

patterns-established:
  - "Release checklist pattern: markdown checkboxes with CLI verify commands"

requirements-completed: [QA-03, QA-05]

duration: 1min
completed: 2026-03-21
---

# Phase 08 Plan 02: Release Checklist Summary

**54-item release checklist covering build, permissions, offline, cache corruption, worker restart, and separate cold/dirty profile test paths for CWS submission**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-21T17:12:50Z
- **Completed:** 2026-03-21T17:14:24Z
- **Tasks:** 1
- **Files created:** 1

## Accomplishments

- Created 9-section release checklist with 54 actionable checkbox items
- Documented cold profile (first install) and dirty returning user as separate verification paths
- Included CLI commands for automated checks (pnpm build/test/typecheck/lint, jq manifest, grep dev origins)
- Referenced architecture-boundaries.test.ts for manifest verification

## Task Commits

Each task was committed atomically:

1. **Task 1: Create release checklist document** - `33cd06c3` (docs)

## Files Created/Modified

- `extension/RELEASE-CHECKLIST.md` - Step-by-step release verification checklist for Chrome Web Store submission

## Decisions Made

- Documented actual manifest permissions (sidePanel, storage, tabs, webNavigation, favicon, alarms, activeTab, bookmarks, offscreen) matching real wxt.config.ts rather than the abbreviated list in the plan
- Split final pre-submission section into separate Cold Profile and Dirty profile signoff lines for explicit dual-path coverage

## Deviations from Plan

None - plan executed exactly as written.

## Known Stubs

None - this is a documentation-only plan with no code stubs.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Release checklist ready for use in pre-submission verification
- Combined with 08-01 smoke/UI test stubs, the QA foundation is complete
- Future milestone can automate manual checklist items with Playwright/Puppeteer

## Self-Check: PASSED

- extension/RELEASE-CHECKLIST.md: FOUND
- 08-02-SUMMARY.md: FOUND
- Commit 33cd06c3: FOUND

---
*Phase: 08-qa-release-discipline*
*Completed: 2026-03-21*
