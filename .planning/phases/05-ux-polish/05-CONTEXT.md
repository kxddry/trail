# Phase 5: UX Polish - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Extension interactions feel consistent and self-documenting: every dropdown, modal, search box, and onboarding surface behaves predictably. 10 UX requirements covering interaction consistency, information density, and onboarding.

</domain>

<decisions>
## Implementation Decisions

### Shared Overlay Hook (UXP-01)
- Extract `useOverlayBehavior(containerRef, onClose)` hook — handles Esc keydown, click-outside mousedown, focus return to trigger, and inert on background
- Apply to SettingsPopover, TreeDropdown, TagFilterDropdown — replacing their inline re-implementations
- Focus return: on close, call `triggerRef.current?.focus()` (currently missing in all 3)
- Inert: set `inert` attribute on sibling elements (currently only SettingsPopover does this)
- TreeDropdown Esc guard for rename input: keep existing guard, overlay hook fires only when no input/textarea is focused

### Search Keyboard Hints (UXP-02)
- Add thin hint bar below the expanded search input: `↑↓ navigate · Enter open · Esc close`
- Muted text, small font — disappears on scroll or when results are focused
- Only visible when search is expanded and focused

### FloatingSearch Blur (UXP-03)
- Current behavior is already correct: blur preserves draft, Esc wipes it
- No changes needed — mark as pre-existing

### TreeDropdown Metadata (UXP-04)
- Active tree: add "last synced" from `account.lastSyncedAt` store field
- Archived trees: show "archived" badge/label explicitly
- Stub trees already show cloud icon from Phase 3 work
- Node count and savedAt date already rendered

### Tag Filter Presets (UXP-05)
- 3 buttons above the tag list: "All tagged", "Untagged", "Clear"
- "All tagged" selects all tags, "Untagged" inverts to show only untagged items, "Clear" resets
- Keep existing individual tag toggle behavior below the presets

### New Tab Empty State (UXP-06)
- When all dashboard cards (bookmarks, continue, recents) return null: show centered empty state
- Content: Trail logo + "Start browsing to grow your trail" text + "Open sidepanel" CTA button
- CTA opens sidepanel via `chrome.sidePanel.open()`

### Settings Privacy Section (UXP-07)
- Add small accordion/expandable section in SettingsPopover: "Your data"
- Bullet list: "Synced to cloud: trees, tags, settings" / "Stays local: layout cache, theme, search history"
- Compact — 4-5 lines max, no sub-pages

### First-Run Hints (UXP-08)
- `hasSeenOnboarding` storage flag (`chrome.storage.local`)
- On first sidepanel open: 3 tooltip-style coach marks pointing at search orb, tree dropdown trigger, tag filter
- Each mark: short label + "Got it" dismiss button
- Single dismiss dismisses all + sets flag
- Click anywhere also dismisses

### SessionExpiredBanner Dismiss (UXP-09)
- Persist dismiss to `chrome.storage.session` — survives panel close/reopen within browser session
- Reappears on meaningful state change: new auth event, explicit sign-out, or fresh browser session
- Currently in-memory only — need `sessionBannerDismissedItem` storage definition

### Destructive Action Copy (UXP-10)
- DeleteTreeConfirmModal: "Delete '{treeName}'? This removes all {nodeCount} pages. This cannot be undone."
- Spotlight confirm: show action title + target name in message

### Claude's Discretion
- Exact styling of coach marks (tooltip vs popover vs overlay)
- Hint bar typography and positioning in FloatingSearch
- Whether empty state illustration is an icon or SVG

</decisions>

<code_context>
## Existing Code Insights

### Key Files
- `SettingsPopover.tsx` — has inert, inline Esc/click-outside
- `TreeDropdown.tsx` — inline Esc/click-outside, no inert, no focus return
- `TagFilterDropdown.tsx` — inline Esc/click-outside, no inert
- `FloatingSearch.tsx` — blur preserves draft (already correct)
- `NewTabApp.tsx` + `DashboardView.tsx` — empty bento grid when no data
- `SessionExpiredBanner.tsx` — in-memory dismiss only
- `DeleteTreeConfirmModal.tsx` — generic copy, no tree name

### Established Patterns
- `useAnchoredDropdown` for viewport repositioning (not overlay behavior)
- `data-tooltip` for hover hints
- `chrome.storage.session` for session-scoped persistence (layout cache, editor state)

</code_context>

<specifics>
## Specific Ideas

UXP-03 is already working — mark as pre-existing during execution. Focus effort on UXP-01 (shared hook) as the foundation that other dropdown-related items depend on.

</specifics>

<deferred>
## Deferred Ideas

None

</deferred>
