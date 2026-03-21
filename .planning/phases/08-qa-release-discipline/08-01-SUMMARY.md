---
phase: 08-qa-release-discipline
plan: 01
subsystem: testing
tags: [e2e, smoke-test, ui-interaction, manual-test, qa, node-assert]

# Dependency graph
requires: []
provides:
  - 8 smoke e2e scenario stubs documenting critical user flows
  - 4 UI interaction test stubs documenting keyboard/modal patterns
  - Test contract for release verification (QA-01, QA-02)
affects: [08-02-PLAN, release-checklist]

# Tech tracking
tech-stack:
  added: []
  patterns: [MANUAL-prefixed test stubs as executable documentation]

key-files:
  created:
    - extension/tests/smoke-e2e.test.ts
    - extension/tests/ui-interaction.test.ts
  modified:
    - extension/package.json

key-decisions:
  - "Followed existing test pattern: node:assert/strict, function-per-scenario, run() wrapper, console.log status"
  - "MANUAL prefix on each stub log line for grep-based counting and future automation discovery"

patterns-established:
  - "MANUAL stub pattern: JSDoc with preconditions/steps/outcomes + assert.ok(true) for stub pass"

requirements-completed: [QA-01, QA-02]

# Metrics
duration: 2min
completed: 2026-03-21
---

# Phase 08 Plan 01: Smoke E2E and UI Interaction Test Stubs Summary

**12 executable test stubs (8 smoke e2e + 4 UI interaction) documenting manual verification steps, wired into pnpm test**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-21T17:12:51Z
- **Completed:** 2026-03-21T17:14:53Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- 8 smoke e2e scenario stubs covering first install, guest mode, auth, session expiry, sync failure, tree switch, export/import, and quota eviction
- 4 UI interaction stubs covering dropdown keyboard navigation, modal escape, search navigation, and auth banner persistence
- Both test files wired into pnpm test script and passing alongside 5 existing test files

## Task Commits

Each task was committed atomically:

1. **Task 1: Create smoke e2e test stubs and UI interaction test stubs** - `6179c88f` (test)
2. **Task 2: Wire new test files into pnpm test script** - `16e2911c` (chore)

## Files Created/Modified
- `extension/tests/smoke-e2e.test.ts` - 8 smoke e2e scenario stubs with JSDoc manual test documentation
- `extension/tests/ui-interaction.test.ts` - 4 UI interaction stubs with JSDoc manual test documentation
- `extension/package.json` - Test script updated to include both new test files

## Decisions Made
- Followed existing test pattern (node:assert/strict, function-per-scenario, run() wrapper) for consistency with architecture-boundaries.test.ts and rpc-schema.test.ts
- Used MANUAL prefix in console.log for each stub to enable grep-based counting and future automation tracking

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Test stubs are ready for Playwright automation when e2e infrastructure is added
- Release checklist (08-02) can reference these stubs as verification gates

---
*Phase: 08-qa-release-discipline*
*Completed: 2026-03-21*

## Self-Check: PASSED

- [x] extension/tests/smoke-e2e.test.ts exists
- [x] extension/tests/ui-interaction.test.ts exists
- [x] 08-01-SUMMARY.md exists
- [x] Commit 6179c88f exists
- [x] Commit 16e2911c exists
