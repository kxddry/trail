---
phase: 05-ux-polish
verified: 2026-03-21T17:00:00Z
status: passed
score: 5/5 must-haves verified
re_verification: false
---

# Phase 5: UX Polish Verification Report

**Phase Goal:** Extension interactions feel consistent and self-documenting: every dropdown, modal, search box, and onboarding surface behaves predictably
**Verified:** 2026-03-21T17:00:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | All dropdowns and modals dismiss on Esc and click-outside, return focus to trigger, and apply inert to background | VERIFIED | `useOverlayBehavior` hook at `hooks/useOverlayBehavior.ts` implements Esc (L24-31), click-outside (L34-39), focus return (L51-57), inert management (L61-85). Imported and called in SettingsPopover (L169), TreeDropdown (L113), TagFilterDropdown (L32). |
| 2 | Sidepanel search shows keyboard shortcut hints inline and preserves draft text on accidental blur | VERIFIED | `FloatingSearch.tsx` L146-161: hint bar with Enter/arrows/Esc shown when `expanded && focused`. Blur handler (L95-99) only sets `focused=false`, never clears draft. Draft cleared only on explicit Esc via `handleCollapse`. |
| 3 | TreeDropdown shows last synced time, node count, and archived/stub status for each tree | VERIFIED | `TreeDropdown.tsx`: `lastSyncedAt` selector (L105), `formatRelativeTime` helper (L61-77), active tree meta includes `synced {time}` (L356). Archived trees have `"archived"` as first meta item (L422). Node count displayed in both active and archived. |
| 4 | First-run experience shows micro-hints for key gestures, and settings includes a "Privacy & data" section | VERIFIED | `OnboardingHints.tsx`: 3 coach marks (search/tree/tag) with backdrop + Got it button. Storage-backed via `hasSeenOnboardingItem` (local). `SettingsPopover.tsx` L430-479: collapsible "your data" section with cloud vs local breakdown. OnboardingHints wired in App.tsx L129. |
| 5 | Destructive action confirmations state what will be lost and how to recover | VERIFIED | `DeleteTreeConfirmModal.tsx` L72-76: title shows quoted tree name, description shows node count with pluralization and "cannot be undone" warning. Delete button (L84-85) repeats tree name. |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `extension/src/apps/sidepanel/ui/hooks/useOverlayBehavior.ts` | Shared overlay behavior hook | VERIFIED | 86 lines, exports `useOverlayBehavior`, implements Esc/click-outside/focus-return/inert |
| `extension/src/apps/sidepanel/ui/components/SettingsPopover.tsx` | Settings using shared hook + privacy section | VERIFIED | Imports and uses `useOverlayBehavior` (L17, L169). "your data" section with cloud/local breakdown (L430-479) |
| `extension/src/apps/sidepanel/ui/components/TreeDropdown.tsx` | Trees using shared hook + metadata | VERIFIED | Uses `useOverlayBehavior` (L15, L113). Shows `lastSyncedAt`, archived label, stub status |
| `extension/src/apps/sidepanel/ui/components/tags/TagFilterDropdown.tsx` | Tags using shared hook + presets | VERIFIED | Uses `useOverlayBehavior` (L9, L32). Preset bar with All tagged/Untagged/Clear (L151-188) |
| `extension/src/apps/sidepanel/ui/components/FloatingSearch.tsx` | Keyboard hints bar in search | VERIFIED | Hint bar at L146-161 with kbd elements for Enter/arrows/Esc |
| `extension/src/apps/sidepanel/ui/components/OnboardingHints.tsx` | First-run coach marks component | VERIFIED | 131 lines, 3 hints with storage-backed dismissal |
| `extension/src/apps/sidepanel/ui/components/DeleteTreeConfirmModal.tsx` | Descriptive destructive confirmation | VERIFIED | Shows tree name, node count, irreversibility warning |
| `extension/src/apps/sidepanel/ui/components/SessionExpiredBanner.tsx` | Session-scoped persistent dismiss | VERIFIED | Uses `sessionBannerDismissedItem` for getValue/setValue/watch |
| `extension/src/apps/newtab/ui/DashboardView.tsx` | Empty state for dashboard | VERIFIED | EmptyState component with icon, text, and sidepanel CTA |
| `extension/src/shared/config/storage-items.ts` | Storage definitions for session banner + onboarding | VERIFIED | `sessionBannerDismissedItem` (L194, session-scoped) and `hasSeenOnboardingItem` (L201, local) |
| `extension/src/apps/sidepanel/ui/components/tags/tag-filter-utils.ts` | collectUntaggedNodes utility | VERIFIED | L37-45, uses tree.iter() matching existing pattern |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| useOverlayBehavior.ts | SettingsPopover.tsx | hook import + call | WIRED | Import L17, call L169 |
| useOverlayBehavior.ts | TreeDropdown.tsx | hook import + call | WIRED | Import L15, call L113 |
| useOverlayBehavior.ts | TagFilterDropdown.tsx | hook import + call | WIRED | Import L9, call L32 |
| OnboardingHints.tsx | storage-items.ts hasSeenOnboardingItem | getValue/setValue | WIRED | Import L2, getValue L26, setValue L58 |
| App.tsx | OnboardingHints.tsx | component render | WIRED | Import L20, render L129 |
| DashboardView.tsx | chrome.sidePanel.open | CTA click handler | WIRED | L180-184, guarded by availability check |
| SessionExpiredBanner.tsx | storage-items.ts sessionBannerDismissedItem | getValue/setValue/watch | WIRED | Import L4, getValue L13, watch L26, setValue L34 |
| App.tsx | sessionBannerDismissedItem | reset on auth restore | WIRED | Import L19, useEffect L103-107 clears flag when sessionExpired=false |
| TreeDropdown.tsx | store.account.lastSyncedAt | useStore selector | WIRED | L105 selector, L356 rendered in meta |
| TagFilterDropdown.tsx | tag-filter-utils collectUntaggedNodes | import + useMemo | WIRED | Import L14, useMemo L51 |
| DeleteTreeConfirmModal.tsx | store (treeLabel, nodeCount) | useStore selectors | WIRED | L16-17 selectors, L72 and L75 rendered |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| UXP-01 | 05-01 | Unified dropdown behavior (Esc, click-outside, focus return, inert) | SATISFIED | useOverlayBehavior hook + all 3 dropdowns retrofitted |
| UXP-02 | 05-01 | Search keyboard shortcuts inline | SATISFIED | FloatingSearch hint bar L146-161 |
| UXP-03 | 05-01 | FloatingSearch preserves draft on blur | SATISFIED | Pre-existing correct behavior verified: onBlurCapture only sets focused=false |
| UXP-04 | 05-02 | TreeDropdown shows sync time, node count, archived/stub status | SATISFIED | lastSyncedAt + formatRelativeTime + "archived" meta label |
| UXP-05 | 05-02 | Tag filter quick presets | SATISFIED | All tagged / Untagged / Clear preset buttons + collectUntaggedNodes utility |
| UXP-06 | 05-03 | New tab empty state with CTA | SATISFIED | EmptyState component in DashboardView with icon, text, Open sidepanel button |
| UXP-07 | 05-04 | Settings "Privacy & data" section | SATISFIED | Collapsible "your data" section in SettingsPopover L430-479 |
| UXP-08 | 05-04 | First-run micro-hints | SATISFIED | OnboardingHints with 3 coach marks, storage-backed dismissal |
| UXP-09 | 05-03 | SessionExpiredBanner persistent dismiss | SATISFIED | session-scoped storage, reset on auth restore in App.tsx |
| UXP-10 | 05-02 | Destructive confirmation shows what will be lost | SATISFIED | DeleteTreeConfirmModal shows tree name, page count, irreversibility warning |

No orphaned requirements found. All 10 UXP requirements are covered by plans and verified as implemented.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| TreeDropdown.tsx | 441, 445, 457 | CSS class "placeholder" | Info | Not a stub -- CSS class for favicon fallback icons. No issue. |
| TagFilterDropdown.tsx | 248 | CSS class "placeholder" | Info | Not a stub -- CSS class for favicon fallback icon. No issue. |

No TODO/FIXME/HACK/stub patterns found in any modified files. No empty implementations. No hardcoded empty data flowing to user-visible output.

### Human Verification Required

### 1. Overlay Esc/Click-Outside Behavior

**Test:** Open each dropdown (Settings, Trees, Tags). Press Esc. Click outside. Verify the dropdown closes and focus returns to the trigger button.
**Expected:** All three dropdowns close on Esc and click-outside. Focus visually returns to the gear/tree/tag button.
**Why human:** Focus return and inert sibling behavior require visual confirmation of correct DOM focus state.

### 2. Search Keyboard Hints Visibility

**Test:** Click the search orb to expand search. Verify hint bar appears below input. Click away (blur). Verify hint bar disappears.
**Expected:** Thin hint bar showing "Enter next / arrows navigate / Esc close" appears when search is expanded and focused, disappears on blur.
**Why human:** Visual positioning and typography cannot be verified programmatically.

### 3. Onboarding Coach Marks Positioning

**Test:** Clear `local:trail_has_seen_onboarding` from storage. Open sidepanel. Verify 3 tooltip-style hints appear pointing at search orb, tree button, tag button.
**Expected:** Coach marks are visually positioned below their target buttons with correct labels. Clicking "Got it" or anywhere dismisses all. Re-opening sidepanel shows no hints.
**Why human:** Hint positioning relies on getBoundingClientRect + 300ms delay; visual alignment needs human check.

### 4. New Tab Empty State

**Test:** Open a new tab with no bookmarks, no recent browsing history, and no recent searches. Verify centered empty state appears.
**Expected:** Layers icon, "Start browsing to grow your trail" text, and "Open sidepanel" CTA button centered on the page. CTA opens sidepanel.
**Why human:** Empty state layout and CTA functionality require browser context.

### 5. Delete Tree Confirmation Copy

**Test:** Open the delete tree confirmation (right-click tree root, delete). Verify it shows the tree name in quotes, page count, and "cannot be undone" warning.
**Expected:** Title: Delete "TreeName"? Body: "This removes all N pages in this tree. This cannot be undone." Button: Delete "TreeName".
**Why human:** Correct text rendering with smart quotes needs visual confirmation.

### Gaps Summary

No gaps found. All 5 success criteria from the ROADMAP are satisfied:

1. All dropdowns share `useOverlayBehavior` with Esc, click-outside, focus return, and inert management.
2. Search shows keyboard hints when expanded/focused; draft preserved on blur.
3. TreeDropdown shows sync time and "archived" label; node count was already present.
4. First-run hints with 3 coach marks + settings "your data" privacy section.
5. Delete confirmation is descriptive with tree name, count, and irreversibility warning.

TypeScript compiles cleanly. All 9 commits verified in git history. No stubs, no TODOs, no anti-patterns in modified files.

---

_Verified: 2026-03-21T17:00:00Z_
_Verifier: Claude (gsd-verifier)_
