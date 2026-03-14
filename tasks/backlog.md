# Trail - Prioritized Backlog

## P0 - Critical (Must Fix Now)

(none - all P0 items resolved)

## P1 - High Priority

### ARCH-001: GraphCanvas.tsx decomposition (in progress)
- **Current: 2,173 lines (down from 2,728)**
- Phase 1: Types extraction — DONE
- Phase 2: useGraphSelection — DONE
- Phase 3: useGraphAnimation — DONE
- Phase 4: useGraphView — TODO (tightly coupled to renderer and layout)
- Phase 5: useGraphLayout — TODO (tightly coupled to animation and drag)
- Phase 6: useGraphDrag — TODO (tightly coupled to positions and view)
- Phase 7: useGraphRenderer — TODO (depends on all other hooks)
- **Note**: Phases 4-7 have circular dependencies; may need a different
  decomposition approach (e.g. useGraphInteraction combining view+drag)

### TEST-001: Extension test coverage critically low
- 37K lines of code, 3 test files
- **Fix**: TDD approach — write tests for RPC, auth, sync, navigation, spotlight

### ARCH-002: 4 files over 800 lines (besides GraphCanvas)
- GraphPixiRenderer.ts (1,682), spotlight.ts (1,193), ContextMenus.tsx (976), ThemePalette.tsx (885)
- contracts.ts (884) — split plan available

## P2 - Medium Priority

### LOG-001: Structured logging — logger created, migration ongoing
- `extension/src/shared/lib/logger.ts` created
- TODO: Gradually migrate console.* calls to use `createLogger()`

## P3 - Nice to Have

- Refresh token replay detection
- Focus trapping in modals
- Button system unification
- Empty state improvements
- Toast system in web app
- Page transitions in web app

## Resolved (2026-03-14)

- All 25+ items from previous audit
- ~~UI-001: Close tab confirmation~~ — two-step confirmation added
- ~~RATE-001: In-memory rate limiting~~ — extracted to reusable module with cleanup
- ~~TEST-002: Marketing tests~~ — 18 tests (feedback API + SectionRenderer)
