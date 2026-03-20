# Phase 2: Hygiene & Dead Code Cleanup - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Remove all dead code and orphaned artifacts from the extension codebase so nothing ships that isn't actively wired.

</domain>

<decisions>
## Implementation Decisions

### Dead Code Resolution
- AuthGate.tsx: DELETE — 0 references in codebase, never mounted in App.tsx
- WelcomeGate.tsx: DELETE — 0 references in codebase, never mounted in App.tsx
- runtime-logger.ts (emitRuntimeLog): DELETE — exported but 0 callers anywhere in src/
- TrailLogo: check if orphaned after AuthGate/WelcomeGate removal (may have other refs)
- guestWelcomeDismissedItem: check if orphaned after WelcomeGate removal

### Artifact Cleanup
- Delete /logs/ and /extension/logs/ directories (dev artifacts, already .gitignored)
- Ensure architecture-boundaries.test.ts hygiene check passes after cleanup

### Claude's Discretion
- Any additional orphaned exports discovered during dead code audit — remove at discretion

</decisions>

<code_context>
## Existing Code Insights

### Key Files
- `extension/src/apps/sidepanel/ui/components/AuthGate.tsx` (64 lines) — dead
- `extension/src/apps/sidepanel/ui/components/WelcomeGate.tsx` (55 lines) — dead
- `extension/src/shared/debug/runtime-logger.ts` (82 lines) — dead
- `extension/src/apps/sidepanel/ui/App.tsx` (50 lines) — active, no gate mounting
- `extension/tests/architecture-boundaries.test.ts` (158 lines) — hygiene test

### Established Patterns
- Architecture boundaries test already forbids logs/ and legacy paths
- .gitignore already excludes logs/ patterns

### Integration Points
- After deleting AuthGate/WelcomeGate, verify no broken imports in barrel exports
- After deleting runtime-logger.ts, verify no broken imports in shared/debug/

</code_context>

<specifics>
## Specific Ideas

User explicitly stated: "either wire or delete" for AuthGate/WelcomeGate and emitRuntimeLog.
Codebase confirms nothing is wired → delete all.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>
