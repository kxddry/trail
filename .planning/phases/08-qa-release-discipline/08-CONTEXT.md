# Phase 8: QA & Release Discipline - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

A repeatable release process exists that catches regressions before Chrome Web Store submission. Covers: smoke e2e test stubs, UI interaction test stubs, release checklist document, cold/dirty profile test documentation.

Note: Full e2e automation requires a browser automation framework. For v1.2, we create test stubs/skeletons and manual test scripts that can be automated later. The release checklist is a document.

</domain>

<decisions>
## Implementation Decisions

### Smoke E2E Tests (QA-01)
- Create test file with 8 scenario stubs: first install, guest mode, auth, session expired, sync fail, tree switch, export/import, quota eviction
- Each stub describes the manual test steps and expected outcomes
- Use the existing test runner (tsx-based, in extension/tests/)
- These are documentation-as-tests: they define WHAT to verify, not automated HOW
- Later milestone can automate with Playwright/Puppeteer

### UI Interaction Tests (QA-02)
- Create test file with interaction test stubs: dropdown keyboard nav, modal escape, search navigation, auth banner
- Same approach: define scenarios, expected behaviors, manual verification steps
- Focus on the patterns we built in Phase 5 (useOverlayBehavior, keyboard hints)

### Release Checklist (QA-03)
- Create `extension/RELEASE-CHECKLIST.md` — step-by-step document
- Sections: Pre-release verification, Permissions check, Offline mode, Empty states, Corrupted cache recovery, Worker restart, Build verification
- Include commands to run for each check
- Reference architecture-boundaries test for automated checks

### Cold vs Dirty Profile Testing (QA-05)
- Add section in release checklist for profile testing
- Cold profile: fresh Chrome profile, install extension, verify first-run experience
- Dirty profile: existing data, multiple trees, tags, archives — verify migration, cache, state restoration
- Document key differences to check between profiles

### Claude's Discretion
- Exact test file naming and organization
- Level of detail in test stubs
- Whether to add a simple test runner script

</decisions>

<code_context>
## Existing Code Insights

### Test Infrastructure
- `extension/tests/` — existing test files: basic.test.ts, architecture-boundaries.test.ts, spotlight-search.test.ts, rpc-schema.test.ts, layout-signature.test.ts
- Test runner: tsx-based, runs via `pnpm test` in extension workspace
- Architecture-boundaries test already validates build output

### Key Test Targets
- useOverlayBehavior hook (Phase 5)
- showOperationError (Phase 3)
- Bootstrap degraded state (Phase 3)
- SessionExpiredBanner persistence (Phase 5)
- Sync status indicator (Phase 4)
- Search suggestions toggle (Phase 6)
- Performance budget metrics (Phase 7)

</code_context>

<deferred>
## Deferred Ideas

None

</deferred>
