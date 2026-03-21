---
phase: quick
plan: 01
subsystem: spotlight, newtab
tags: [ui-bug, loading-state, layout-shift, navigation]
dependency_graph:
  requires: []
  provides: [spotlight-progress-bar, newtab-fixed-panel, bento-loading-animation, open-url-only]
  affects: [spotlight-ux, newtab-ux]
tech_stack:
  added: []
  patterns: [css-progress-bar, css-grid-transition, callback-override]
key_files:
  created: []
  modified:
    - src/spotlight/SpotlightRoot.tsx
    - src/entrypoints/spotlight.content/style.css
    - src/entrypoints/newtab/ui/NewTabApp.tsx
    - src/entrypoints/newtab/ui/DashboardView.tsx
    - src/entrypoints/newtab/ui/newtab.css
decisions:
  - Used absolute-positioned CSS-only progress bar instead of React loading component for zero-JS overhead
  - Override handleActivate at NewTabApp level rather than modifying shared useSpotlightActions hook
  - Fixed height 340px for search results panel matches approximate bento idle height
metrics:
  duration: 4m30s
  completed: 2026-03-18T10:29:14Z
  tasks_completed: 2
  tasks_total: 2
---

# Quick Task 260318-iio: Fix UI Bugs in Spotlight and New Tab Summary

Thin CSS progress bar replaces Loading... flash in Spotlight; New Tab results panel fixed at 340px; bento bookmarks stretch during load; old-tree clicks open URL only.

## Tasks Completed

| # | Task | Commit | Key Changes |
|---|------|--------|-------------|
| 1 | Spotlight progress bar + fixed panel + spacing | 934afe44 | Replaced loading branch with progress bar overlay, fixed panel height, uniform spacing |
| 2 | Bento loading animation + old-tree click | 8a81f493 | BookmarksCard stretch, CSS transitions, handleActivateNewTab wrapper, graph onNavigate fix |

## Bug Fixes Applied

### Bug 1: Spotlight Loading Flash
Removed the `search.loading` conditional branch that showed "Loading..." text. Added a `<div className="spotlight-loading-bar" />` as the first child of `.spotlight-left`, rendered whenever `search.loading` is true. Existing results stay visible while the progress bar signals activity. Added `position: relative` to `.spotlight-left` for proper anchoring.

### Bug 2: New Tab Fixed-Height Results Panel
Changed `.newtab-list` from `max-height: 420px; min-height: 280px` to `height: 340px`. Added `.newtab-list .spotlight-sections { height: 100%; overflow-y: auto; }` for proper scroll within fixed container.

### Bug 3: Uniform Result Spacing
Added `gap: 0` to `.newtab-search-defaults` and zeroed margin/padding on `.newtab-list .spotlight-section-heading` to eliminate inconsistent gaps between results.

### Bug 4: Smooth Bento Loading
Added `loading` prop to `DashboardView`. When loading, only BookmarksCard renders with `.newtab-bento-card--stretch` class (spans full grid width, max-height 400px). CSS transitions on `.newtab-bento` and `.newtab-bento-card` provide smooth animation when continue/recent cards appear. Fixed continue card bottom padding with `margin-bottom: -4px`.

### Bug 5: Old-Tree Click Opens URL Only
Created `handleActivateNewTab` wrapper in NewTabApp that intercepts node items from non-active trees and calls `handleExecuteAction('open', ...)` instead of `handleActivate` (which would use `'open-node-in-tree'`). Applied to DashboardView onActivate, SpotlightResults onActivate, useSpotlightKeyboard handleActivate, and graph onNavigate.

## Deviations from Plan

None - plan executed exactly as written.

## Verification

- Build: PASSED (5.29 MB, 5.4s)
- TypeScript: PASSED (no errors)

## Self-Check: PASSED

All 5 modified files exist on disk. Both task commits (934afe44, 8a81f493) verified in git log.
