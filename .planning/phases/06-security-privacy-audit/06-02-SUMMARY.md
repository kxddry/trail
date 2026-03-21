---
phase: 06-security-privacy-audit
plan: 02
subsystem: logging
tags: [structured-logging, redaction, privacy, security, console-migration]

requires:
  - phase: none
    provides: existing createLogger in shared/lib/logger.ts (0 adoption)
provides:
  - "redactSensitive utility for field-name-based PII redaction"
  - "All 28 background files using structured createLogger"
  - "Zero raw console.* calls in extension/src/background/"
affects: [07-performance-budgets, future-error-reporting]

tech-stack:
  added: []
  patterns: [structured-logging-with-redaction, namespace-per-file-logger]

key-files:
  created: []
  modified:
    - extension/src/shared/lib/logger.ts
    - extension/src/background/services/tree-storage.ts
    - extension/src/background/services/auth-orchestrator.ts
    - extension/src/background/services/auth-policy-keeper.ts
    - extension/src/background/services/account-keeper.ts
    - extension/src/background/services/sync/migration.ts
    - extension/src/background/services/tree-loader.ts
    - extension/src/background/services/search-suggestions.ts
    - extension/src/background/services/settings.ts
    - extension/src/background/services/quota-manager.ts
    - extension/src/background/services/tag-storage.ts
    - extension/src/background/services/temporary-selection.ts
    - extension/src/background/services/spotlight-live-index.ts
    - extension/src/background/services/flags.ts
    - extension/src/background/services/editor-sync.ts
    - extension/src/background/services/offscreen-graph-manager.ts
    - extension/src/background/messaging/router.ts
    - extension/src/background/messaging/send-message.ts
    - extension/src/background/messaging/handlers/editor-handlers.ts
    - extension/src/background/messaging/handlers/panel-handlers.ts
    - extension/src/background/messaging/handlers/tree-handlers.ts
    - extension/src/background/messaging/handlers/site-message-handlers.ts
    - extension/src/background/messaging/handlers/tab-handlers.ts
    - extension/src/background/navigation/navigation-handler.ts
    - extension/src/background/state/tab-manager.ts
    - extension/src/background/state/tab-index.ts
    - extension/src/background/tabs/sync-open-tabs.ts
    - extension/src/background/tabs/lifecycle.ts
    - extension/src/background/service-worker.ts

key-decisions:
  - "Field-name matching for redaction (not regex on values) for predictability"
  - "Case-insensitive key comparison via toLowerCase()"
  - "domainOnly extracts hostname via URL constructor, falls back to [invalid-url]"
  - "auth-orchestrator logAuth converted to log.debug (dev-only, was intentionally silent)"
  - "account-keeper log helper replaced with createLogger instance"

patterns-established:
  - "Structured logging: import { createLogger } from '@shared/lib/logger.js'; const log = createLogger('namespace');"
  - "Error payload pattern: { error: e instanceof Error ? e.message : String(e) }"
  - "Auto-redaction on warn/error: tokens -> [redacted], URLs -> domain-only, titles -> [title omitted]"

requirements-completed: [SEC-05, SEC-07]

duration: 11min
completed: 2026-03-21
---

# Phase 06 Plan 02: Structured Logger with Redaction Summary

**redactSensitive utility auto-redacts tokens/URLs/titles on warn/error, all 28 background files migrated from raw console.* to namespaced createLogger**

## Performance

- **Duration:** 11 min
- **Started:** 2026-03-21T16:14:24Z
- **Completed:** 2026-03-21T16:25:52Z
- **Tasks:** 2
- **Files modified:** 29

## Accomplishments
- Added redactSensitive utility with field-name-based matching (sensitive keys, URL keys, title keys)
- Auto-applied redaction on warn/error output in createLogger
- Migrated all 64 raw console.* calls across 28 background files to structured createLogger
- Each file has a descriptive namespace (e.g., "tree-storage", "auth-orchestrator", "rpc-router")
- Extension build passes with zero regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Add redaction utility to logger** - `f433d709` (feat)
2. **Task 2: Migrate all background files from raw console.* to createLogger** - `7de3a5b1` (feat)

## Files Created/Modified
- `extension/src/shared/lib/logger.ts` - Added redactSensitive, domainOnly, SENSITIVE_KEYS/URL_KEYS/TITLE_KEYS sets; auto-redact on warn/error
- `extension/src/background/services/tree-storage.ts` - 24 console calls migrated (highest call count)
- `extension/src/background/services/auth-orchestrator.ts` - logAuth helper converted to log.debug
- `extension/src/background/services/account-keeper.ts` - log helper replaced with createLogger instance
- `extension/src/background/services/quota-manager.ts` - 3 console.warn migrated
- `extension/src/background/services/tag-storage.ts` - 3 console calls migrated
- 23 other background files - 1-2 console calls each migrated

## Decisions Made
- Field-name matching (not regex on values) for redaction -- predictable, no false positives
- Case-insensitive key comparison via toLowerCase() to catch camelCase variants
- domainOnly helper extracts hostname via URL constructor, "[invalid-url]" fallback
- auth-orchestrator's intentionally-silent logAuth converted to log.debug (visible in dev, silent in production)
- account-keeper's intentionally-silent log helper replaced with createLogger -- same dev-only visibility via debug level

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Known Stubs
None - all functionality is fully wired.

## Next Phase Readiness
- Structured logging foundation established for all background code
- Future files in background/ should follow the pattern: `const log = createLogger("namespace")`
- Error payloads should use `{ error: e instanceof Error ? e.message : String(e) }` pattern

## Self-Check: PASSED

- All key files exist (logger.ts, tree-storage.ts, service-worker.ts, SUMMARY.md)
- Both task commits found (f433d709, 7de3a5b1)
- 0 raw console calls in background/ (expected: 0)
- 28 files with createLogger (expected: 28)

---
*Phase: 06-security-privacy-audit*
*Completed: 2026-03-21*
