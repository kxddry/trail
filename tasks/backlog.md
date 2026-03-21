# Trail - Prioritized Backlog

## P0 - Critical (Must Fix Now)

(none - all P0 items resolved)

## P1 - High Priority

### ARCH-001: GraphCanvas.tsx decomposition (mostly complete)
- **Current: 1,797 lines (down from 2,728 — 34% reduction)**
- Phase 1: graph-canvas-types.ts (153 lines) — DONE
- Phase 2: useGraphSelection.ts (160 lines) — DONE
- Phase 3: useGraphAnimation.ts (326 lines) — DONE
- Phase 4: useGraphView.ts (411 lines) — DONE
- Phases 5-7 (layout, drag, renderer): DEFERRED
  - Remaining code is orchestration layer — tightly coupled by design
  - Further extraction creates parameter-passing overhead > benefit
  - 1,797 lines is manageable for a complex interactive component

### TEST-001: Extension test coverage
- 37K lines of code, now 5 test files (up from 3)
- Added: RPC schema tests, extension token tests
- TODO: sync engine, auth orchestrator, navigation handler, spotlight service

### ARCH-002: 4 files over 800 lines
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

## Resolved

25+ items from initial audit + 5 additional fixes in this session:
- Close tab confirmation, SectionRenderer tests, rate limiter extraction,
  structured logger, GraphCanvas Phases 1-4
