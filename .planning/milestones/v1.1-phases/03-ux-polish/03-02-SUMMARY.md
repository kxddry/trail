---
phase: 03-ux-polish
plan: 02
subsystem: extension-ui
tags: [accessibility, aria, ux, context-menu, keyboard-navigation]
dependency_graph:
  requires: []
  provides: [accessible-context-menus, destructive-action-confirmations]
  affects: [extension/src/sidepanel/ui/components/ContextMenus.tsx, extension/src/sidepanel/ui/styles/context-menus.css]
tech_stack:
  added: []
  patterns: [two-click-confirm, aria-menuitemcheckbox, focus-visible, prefers-reduced-motion]
key_files:
  created: []
  modified:
    - extension/src/sidepanel/ui/components/ContextMenus.tsx
    - extension/src/sidepanel/ui/styles/context-menus.css
decisions:
  - "Inline confirmation pattern (two-click) kept over AlertDialog — stays in flow for context menu UX"
  - "aria-checked='mixed' used for partial tag selection in BulkContextMenu"
  - "Tab items get role=menuitem not role=option — they are actions, not selections"
metrics:
  duration: ~4 min
  completed: 2026-02-28
  tasks_completed: 2
  files_modified: 2
---

# Phase 3 Plan 02: Context Menu Accessibility Summary

**One-liner:** Inline two-click destructive confirmations for BulkContextMenu plus full ARIA role coverage (menuitem, separator, presentation, menu, menuitemcheckbox) and keyboard focus-visible styles across all context menu elements.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Add confirmation pattern to BulkContextMenu destructive actions | 29b19559 | ContextMenus.tsx |
| 2 | Add comprehensive ARIA roles and keyboard focus styles | 39112b68 | ContextMenus.tsx, context-menus.css |

## What Was Built

### Task 1: BulkContextMenu Confirmation Pattern (UX-04)

Extended the existing inline two-click confirmation pattern from `NodeContextMenu` to `BulkContextMenu`:

- Added `pendingDelete` state to `BulkContextMenu`
- "Delete nodes" now requires a first click (shows "Confirm delete?") before executing
- "Delete nodes recursively" likewise requires a confirmation click
- Used the existing `.danger.is-confirming` CSS class — no new styles needed
- Added `role="menuitem"` and `tabIndex={-1}` to all destructive items
- Added `role="separator"` to the divider above delete actions

### Task 2: ARIA Roles + Focus Styles (UX-06)

**NodeContextMenu:**
- `role="separator"` on all three dividers (tabs section, main divider, delete section)
- `role="presentation"` on the tabs count header
- `role="menuitem"` + `tabIndex={-1}` on tab list items, "Close tab/Close all tabs", "Collapse node", "Expand node", "Duplicate at..."
- Tags submenu: parent item gets `role="menuitem"`, submenu container gets `role="menu"`, tag items get `role="menuitemcheckbox"` + `aria-checked={Boolean(hasTag)}`
- "New Tag..." item gets `role="menuitem"` + `tabIndex={-1}`

**BulkContextMenu:**
- `role="presentation"` on "{N} nodes selected" header
- `role="separator"` on dividers
- `role="menuitem"` + `tabIndex={-1}` on Pin selected, Unpin selected, Collapse selected, Expand selected, Close selected tabs
- Tags submenu: parent item gets `role="menuitem"`, submenu gets `role="menu"`, tag items get `role="menuitemcheckbox"` + `aria-checked` (supports `true`, `false`, and `"mixed"` for partial selection)

**CSS — Focus styles:**
```css
.graph-context-menu-item:focus-visible { outline: 2px solid var(--ring); ... }
.graph-context-tab-item:focus-visible  { outline: 2px solid var(--ring); ... }
.graph-context-tab-action:focus-visible { outline: 2px solid var(--ring); ... }

@media (prefers-reduced-motion: reduce) {
  .graph-context-menu { animation: none; }
  .graph-context-submenu { transition: none; }
}
```

## Verification Results

1. `tsc -p tsconfig.app.json --noEmit` — PASS (0 errors)
2. `role="menuitem"` in ContextMenus.tsx — 28 matches (all actionable items covered)
3. `role="separator"` in ContextMenus.tsx — 5 matches (all dividers covered)
4. `pendingDelete` state in BulkContextMenu — confirmed at line 750
5. `:focus-visible` in context-menus.css — 3 rules present

## Decisions Made

1. **Inline confirm over AlertDialog**: The plan's interfaces section clarified this — the existing two-click inline confirm is superior for context menus (stays in flow, no modal popup). Used that pattern consistently.

2. **aria-checked="mixed" for partial tag selection**: BulkContextMenu tags can be in three states (all selected, some selected, none selected). Used the ARIA-standard `"mixed"` value for partial state.

3. **Tab items as menuitem not option**: Tab items in the node context menu are actions (click to switch to tab) not selection items, so `role="menuitem"` is the correct ARIA role.

## Deviations from Plan

None — plan executed exactly as written.

## Self-Check: PASSED

Files confirmed present:
- extension/src/sidepanel/ui/components/ContextMenus.tsx — FOUND
- extension/src/sidepanel/ui/styles/context-menus.css — FOUND

Commits confirmed:
- 29b19559 — FOUND
- 39112b68 — FOUND
