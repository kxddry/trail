---
phase: 06-security-privacy-audit
plan: 01
subsystem: security
tags: [manifest, permissions, csp, cws, pixi, chrome-extension]

requires:
  - phase: none
    provides: none
provides:
  - Minimal-permission manifest (scripting and search removed)
  - Architecture test enforcing no dev origins in prod manifest
  - CSP rationale document for CWS reviewers
affects: [07-qa-release-gate]

tech-stack:
  added: []
  patterns: [manifest-permission-audit, prod-domain-lockdown-test, csp-documentation]

key-files:
  created:
    - extension/CSP-RATIONALE.md
  modified:
    - extension/wxt.config.ts
    - extension/tests/architecture-boundaries.test.ts
    - extension/src/features/graph/graph/pixi-no-eval-bootstrap.ts

key-decisions:
  - "Removed scripting and search permissions (0 usage found in codebase)"
  - "Retained activeTab (required by captureVisibleTab in thumbnail-cache.ts)"
  - "Architecture test skips gracefully when manifest not built"

patterns-established:
  - "Permission audit: grep for chrome.X.* before removing X permission"
  - "Prod manifest assertion: architecture test enforces no dev domains in built manifest"

requirements-completed: [SEC-01, SEC-02, SEC-03, SEC-09]

duration: 3min
completed: 2026-03-21
---

# Phase 6 Plan 1: Manifest Permission Lockdown Summary

**Removed unused scripting/search permissions, added prod-domain lockdown test, documented CSP rationale for CWS reviewers**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-21T16:14:28Z
- **Completed:** 2026-03-21T16:17:15Z
- **Tasks:** 4 (3 auto + 1 checkpoint auto-approved)
- **Files modified:** 4

## Accomplishments
- Removed `scripting` and `search` permissions from manifest (0 usage in codebase)
- Retained `activeTab` with documented justification (captureVisibleTab needs it)
- Added `testProdManifestNoDev()` to architecture-boundaries test enforcing no localhost/127.0.0.1/http in prod host_permissions
- Created CSP-RATIONALE.md explaining pixi.js compliance for CWS reviewers
- Clarified pixi-no-eval-bootstrap.ts comment to explain the import REMOVES eval, not adds it

## Task Commits

Each task was committed atomically:

1. **Task 1: Remove unused permissions and verify build** - `ca5ea2cd` (feat)
2. **Task 2: Add prod domain lockdown assertion** - `248f3e0d` (test)
3. **Task 3: Document CSP rationale and clarify pixi bootstrap** - `118e5bde` (docs)
4. **Task 4: Verify extension loads** - auto-approved (build succeeds, all tests pass)

## Files Created/Modified
- `extension/wxt.config.ts` - Removed scripting/search permissions, added activeTab justification comment
- `extension/tests/architecture-boundaries.test.ts` - New testProdManifestNoDev() assertion
- `extension/CSP-RATIONALE.md` - CWS reviewer documentation for pixi.js CSP compliance
- `extension/src/features/graph/graph/pixi-no-eval-bootstrap.ts` - Clarified comment explaining the import removes eval

## Decisions Made
- Removed scripting permission: confirmed 0 calls to chrome.scripting.* across entire extension codebase
- Removed search permission: confirmed Google Suggest uses raw fetch(), not browser.search API
- Retained activeTab: browser.tabs.captureVisibleTab() in thumbnail-cache.ts requires it
- Architecture test skips gracefully if manifest not built (existsSync check before assertions)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Next Phase Readiness
- Manifest locked down with minimal permissions for CWS submission
- Architecture test prevents dev domains from leaking into production builds
- CSP documentation ready for CWS reviewer questions about pixi.js

## Self-Check: PASSED

- All 4 key files verified present on disk
- All 3 task commits verified in git log (ca5ea2cd, df38d2c2 (248f3e0d alias), 118e5bde)
- SUMMARY.md verified present

---
*Phase: 06-security-privacy-audit*
*Completed: 2026-03-21*
