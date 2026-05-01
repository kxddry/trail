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

### UI-001: TreeDropdown UX issues
File: `extension/src/apps/sidepanel/ui/components/TreeDropdown.tsx`

**Critical**
- [ ] Delete archived tree без confirm dialog — destructive, ставит серверный delete в очередь (line 241, `handleDeleteArchived`)
- [ ] Action-кнопки невидимы на touch — `opacity-0 group-hover:opacity-100` ломает мобильный/тач UX (line 479)
- [ ] Sync state не показывается — `_syncing` помечен unused, нет визуального индикатора (line 158)

**UX patterns**
- [ ] Rename доступен только через double-click, не discoverable — добавить кнопку или tooltip-подсказку (lines 337, 469)
- [ ] Слово "archived" дублируется в meta каждого элемента, хотя они уже в секции "saved" (line 415)
- [ ] Заменить кастомный `data-tooltip` на shadcn `<Tooltip>` для консистентности (lines 297, 357, и далее)

**Polish**
- [ ] Header "trees" lowercase vs "saved" uppercase tracking — стилевое несоответствие (line 306)
- [ ] Empty state CTA указывает на крошечную `+` иконку — заменить на кликабельную кнопку прямо в empty state (lines 402-406)
- [ ] `confirmNewTree` setting меняет только title диалога, не поведение — упростить или удалить (line 568)

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
