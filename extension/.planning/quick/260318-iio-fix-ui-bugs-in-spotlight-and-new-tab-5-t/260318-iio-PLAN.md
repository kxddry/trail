---
phase: quick
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/spotlight/SpotlightRoot.tsx
  - src/entrypoints/spotlight.content/style.css
  - src/entrypoints/newtab/ui/NewTabApp.tsx
  - src/entrypoints/newtab/ui/DashboardView.tsx
  - src/entrypoints/newtab/ui/newtab.css
  - src/spotlight/useSpotlightActions.ts
autonomous: true
requirements: [BUG-1, BUG-2, BUG-3, BUG-4, BUG-5]

must_haves:
  truths:
    - "Spotlight shows a thin animated progress bar at top instead of 'Loading...' flash when search results are loading"
    - "New Tab search results panel has a fixed height matching the bento idle height, no layout shift"
    - "New Tab search results have uniform spacing between items (no random extra padding)"
    - "New Tab bento bookmarks stretch to fill full height when continue/recent-searches are loading, then smoothly animate to shrink"
    - "New Tab bento continue card bottom padding matches bookmarks card padding"
    - "Clicking a result from an old tree in New Tab opens just the page URL, not the whole tree"
  artifacts:
    - path: "src/spotlight/SpotlightRoot.tsx"
      provides: "Progress bar loading state instead of Loading... text"
    - path: "src/entrypoints/spotlight.content/style.css"
      provides: "Spotlight loading bar animation styles"
    - path: "src/entrypoints/newtab/ui/NewTabApp.tsx"
      provides: "Fixed-height results panel, open-url-only for old-tree results"
    - path: "src/entrypoints/newtab/ui/DashboardView.tsx"
      provides: "Smooth loading animation for bento sections"
    - path: "src/entrypoints/newtab/ui/newtab.css"
      provides: "Fixed panel height, uniform spacing, bento stretch animation styles"
  key_links:
    - from: "src/spotlight/SpotlightRoot.tsx"
      to: "src/entrypoints/spotlight.content/style.css"
      via: "CSS class spotlight-loading-bar"
      pattern: "spotlight-loading-bar"
    - from: "src/entrypoints/newtab/ui/NewTabApp.tsx"
      to: "src/spotlight/useSpotlightActions.ts"
      via: "handleActivate override for old-tree results"
      pattern: "open-url-only"
---

<objective>
Fix 5 UI bugs across Spotlight and New Tab: replace Spotlight loading flash with a thin progress bar, make New Tab search results panel a fixed height matching bento, fix inconsistent result spacing, add smooth bento loading animation with bookmarks stretch, and change old-tree result clicks to open URL only (not the whole tree).

Purpose: Polish UX -- eliminate layout shifts, loading flashes, and unexpected navigation behavior.
Output: Clean, consistent UI behavior in both Spotlight overlay and New Tab page.
</objective>

<execution_context>
@/Users/iv/.claude/get-shit-done/workflows/execute-plan.md
@/Users/iv/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@src/spotlight/SpotlightRoot.tsx
@src/spotlight/SpotlightResults.tsx
@src/spotlight/useSpotlightSearch.ts
@src/spotlight/useSpotlightActions.ts
@src/spotlight/rpc.ts
@src/spotlight/types.ts
@src/entrypoints/spotlight.content/style.css
@src/entrypoints/newtab/ui/NewTabApp.tsx
@src/entrypoints/newtab/ui/DashboardView.tsx
@src/entrypoints/newtab/ui/newtab.css
@src/background/messaging/handlers/spotlight-handlers.ts (lines 60-90 for action handling reference)

<interfaces>
<!-- Key types and contracts the executor needs -->

From src/spotlight/useSpotlightSearch.ts:
```typescript
type UseSpotlightSearchReturn = {
  sessionId: SpotlightSearchSessionId | null;
  bootstrapData: SpotlightBootstrapData | null;
  sections: SpotlightSection[];
  loading: boolean;          // <-- This is the loading state that causes the flash
  sessionError: string | null;
  query: string;
  setQuery: (q: string) => void;
  previewCache: LRUMap<string, SpotlightGraphPreviewData>;
  recentQueries: string[];
  retryBootstrap: () => void;
};
```

From src/spotlight/useSpotlightActions.ts (handleActivate node logic, lines 266-272):
```typescript
// Current behavior: opens whole tree for foreign nodes
const actionId: SpotlightActionId =
  activeTreeId && item.treeId !== activeTreeId ? 'open-node-in-tree' : 'open';
await handleExecuteAction(
  actionId,
  { kind: 'node', nodeId: item.nodeId, treeId: item.treeId },
  actionId === 'open-node-in-tree' ? 'Opened in tree' : 'Opened',
);
```

From src/background/messaging/handlers/spotlight-handlers.ts:
```typescript
// 'open' -- navigates to the node (just opens URL)
// 'open-node-in-tree' -- opens the full tree and focuses the node
// 'open-url-only' -- opens URL in new tab (exists, line 83-84)
```

From src/entrypoints/newtab/ui/DashboardView.tsx:
```typescript
type DashboardViewProps = {
  readonly bookmarks: readonly BookmarkItem[];
  readonly recentQueries: readonly string[];
  readonly continueItems: SpotlightSearchResult[];
  readonly onQueryChange: (q: string) => void;
  readonly onActivate: (item: SpotlightSearchResult) => Promise<void>;
};
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Spotlight progress bar + New Tab fixed-height panel + uniform spacing</name>
  <files>
    src/spotlight/SpotlightRoot.tsx,
    src/entrypoints/spotlight.content/style.css,
    src/entrypoints/newtab/ui/NewTabApp.tsx,
    src/entrypoints/newtab/ui/newtab.css
  </files>
  <action>
**Bug 1 -- Spotlight loading progress bar:**

In `SpotlightRoot.tsx`, replace the loading flash (line 256-257):
```tsx
) : search.loading ? (
  <div className="spotlight-empty">Loading...</div>
```
with a pattern that shows results (or empty state) WHILE loading, plus a thin progress bar at the top of the left panel. The key insight: when `search.loading` is true but `search.sections` already has data (from a previous search), show those sections with a progress bar on top. Only show the empty "Loading..." state when both `search.loading` is true AND `search.sections` is empty AND there is no query.

Restructure the left panel content in SpotlightRoot.tsx (around lines 251-291):
1. Add a `{search.loading && <div className="spotlight-loading-bar" />}` as the first child inside `.spotlight-left`, BEFORE the conditional content. This shows a thin animated bar at the top whenever loading, regardless of what content is below.
2. Remove the `search.loading` branch from the conditional chain entirely. The conditional should go: sessionError -> helpOpen -> (sections.length === 0 && query) -> (sections.length === 0 && !query && recentQueries) -> (sections.length === 0) -> SpotlightResults.
   This way, existing results stay visible while new results load, and the progress bar signals activity.

In `style.css` (spotlight), add styles for `.spotlight-loading-bar` matching the New Tab's pattern (from newtab.css lines 469-494):
```css
.spotlight-loading-bar {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  z-index: 10;
  overflow: hidden;
  pointer-events: none;
}

.spotlight-loading-bar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 50%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.15), transparent);
  animation: spotlight-loading-slide 1.2s ease-in-out infinite;
}

@keyframes spotlight-loading-slide {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}
```
Also add light theme variant:
```css
[data-theme="light"] .spotlight-loading-bar::after {
  background: linear-gradient(90deg, transparent, rgba(0, 0, 0, 0.08), transparent);
}
```
Make sure `.spotlight-left` has `position: relative` (it already uses flex layout, just ensure `position: relative` is set so the absolute progress bar anchors correctly).

**Bug 2 -- New Tab fixed-height results panel:**

In `newtab.css`, the `.newtab-list` currently has `max-height: 420px; min-height: 280px`. Change this to a FIXED height that matches the bento idle height. The bento grid with its cards is roughly the same visual area. Set `.newtab-list` to use a fixed height instead of max-height:
```css
.newtab-list {
  height: 340px;    /* Fixed: matches approximate bento height in idle */
  max-height: none; /* Remove the old max-height constraint */
  min-height: unset;
}
```
Also ensure `.spotlight-sections` inside `.newtab-list` gets `overflow-y: auto; height: 100%` so results scroll within the fixed container. The SpotlightResults component already sets `overflowY: auto, maxHeight: 100%` inline -- change the inline style in SpotlightResults or override via CSS:
```css
.newtab-list .spotlight-sections {
  height: 100%;
  overflow-y: auto;
}
```

**Bug 3 -- Uniform search result spacing:**

The random padding between search results comes from the virtual list items in SpotlightResults.tsx. Each item has inline `paddingLeft: 8` and `paddingRight: 8` (line 191-193), but section headers and items have different sizing via `HEADER_HEIGHT = 28` and `ROW_HEIGHT = 42`. The virtualizer uses `paddingStart: 8` and `paddingEnd: 8` as overall list padding. The issue is that the gap between results is already uniform via the virtualizer's absolute positioning -- the "random padding" likely comes from the bento/dashboard view items or from the `.newtab-search-defaults` items.

In `newtab.css`, ensure `.newtab-search-defaults` items have consistent spacing:
```css
.newtab-search-defaults {
  padding: 6px;
  gap: 0;  /* Remove any implicit gap */
}
```
And for the spotlight sections within newtab, ensure no extra margin/padding leaks:
```css
.newtab-list .spotlight-section-heading {
  margin: 0;
  padding: 0;
}
```
Also check if `.spotlight-sections` has any gap or margin between children that could cause inconsistency -- it should not since it uses the virtualizer's absolute positioning.
  </action>
  <verify>
    Build succeeds: `cd /Users/iv/dev/trail/extension && npm run build 2>&1 | tail -5`
    TypeScript check: `npx tsc --noEmit 2>&1 | tail -10`
  </verify>
  <done>
    - Spotlight shows a thin animated progress bar at top of left panel during loading, never flashes "Loading..." text when results exist
    - New Tab results panel has fixed height that does not change between idle and search states
    - Search result spacing is uniform with no random gaps
  </done>
</task>

<task type="auto">
  <name>Task 2: Bento smooth loading animation + old-tree click behavior</name>
  <files>
    src/entrypoints/newtab/ui/DashboardView.tsx,
    src/entrypoints/newtab/ui/NewTabApp.tsx,
    src/entrypoints/newtab/ui/newtab.css
  </files>
  <action>
**Bug 4 -- Smooth bento loading animation:**

The bento grid (in DashboardView.tsx) renders BookmarksCard, ContinueCard, and RecentSearchesCard. Each card returns `null` when empty (e.g., `continueItems.length === 0`). This means while data loads, only BookmarksCard might show (bookmarks load locally/fast), and the other cards pop in when data arrives, causing layout shift.

Fix approach -- make BookmarksCard stretch to fill the full bento when it is the only visible card, then smoothly animate when other cards appear:

1. In `DashboardView.tsx`, add a prop or derive loading state. The `continueItems` come from `search.sections[0]`, which is empty until bootstrap completes. Bookmarks load independently via `useBookmarks`. So we can detect "still loading" as: `continueItems.length === 0 && recentQueries.length === 0`.

2. Pass a `loading` prop from NewTabApp to DashboardView. In NewTabApp.tsx, the `search.loading` state from `useSpotlightSearch` indicates bootstrap is in progress. Add `loading={search.loading}` to the DashboardView props.

3. In DashboardView.tsx:
   - Add `loading: boolean` to `DashboardViewProps`.
   - When `loading` is true, only render BookmarksCard and give the bento grid a class like `newtab-bento--loading` that makes BookmarksCard expand to fill the full grid height.
   - When `loading` becomes false (data arrives), render all cards normally. Use CSS transitions on grid-template-rows or height for smooth animation.

4. In DashboardView.tsx, change BookmarksCard to accept a `stretch` prop:
   ```tsx
   <BookmarksCard bookmarks={bookmarks} stretch={loading} />
   ```
   When `stretch` is true, apply class `newtab-bento-card--stretch` which removes max-height on the bookmarks grid and takes full bento height.

5. In `newtab.css`, add smooth transition for the bento layout:
   ```css
   .newtab-bento {
     transition: grid-template-rows 0.3s ease;
   }

   .newtab-bento-card {
     transition: all 0.3s ease;
     overflow: hidden;
   }

   .newtab-bento-card--stretch {
     grid-column: 1 / -1;
   }

   .newtab-bento-card--stretch .newtab-bento-bookmarks-grid {
     max-height: 400px;  /* Full bento height when stretched */
   }
   ```

6. Fix ContinueCard bottom padding: The ContinueCard currently has `padding: 14px` from `.newtab-bento-card`. The `.newtab-bento-continue-list` inside it has no bottom padding, but the items themselves have `padding: 8px 12px`. This should be visually consistent with BookmarksCard. Ensure both cards use the same padding structure. If there is extra padding at the bottom of "Pick Up Where You Left Off", it is from the gap between items or from the card padding. Add:
   ```css
   .newtab-bento-continue-list {
     margin-bottom: -4px;  /* Compensate for last item's bottom padding to match bookmarks visual balance */
   }
   ```
   Or alternatively, just ensure `.newtab-bento-card` uses the same padding for all card types (it already does via the shared class). The issue might be that the continue list items have subtitle text adding extra height. Check that `.newtab-bento-item-subtitle` in continue cards is not adding unneeded padding. If the padding mismatch is from the card itself, reduce the bottom padding of the continue card:
   ```css
   .newtab-bento-continue-list + :empty,
   .newtab-bento-card:has(.newtab-bento-continue-list) {
     padding-bottom: 10px;  /* Match visual weight of bookmarks card */
   }
   ```
   Use your judgment on exact values to make both cards look balanced.

**Bug 5 -- Old-tree result click opens URL only (not whole tree):**

In `NewTabApp.tsx`, the `handleActivate` from `useSpotlightActions` uses this logic for node items (in useSpotlightActions.ts lines 266-272):
```typescript
const actionId: SpotlightActionId =
  activeTreeId && item.treeId !== activeTreeId ? 'open-node-in-tree' : 'open';
```

This means clicking a result from a different tree opens that tree. In New Tab, the desired behavior is: ALWAYS just open the URL, never open the whole tree. Opening in tree context should only happen via explicit action (context menu / action buttons).

Fix: In NewTabApp.tsx, create a wrapper around `act.handleActivate` that overrides the behavior for node items from non-active trees:

```tsx
const handleActivateNewTab = useCallback(async (item: SpotlightSearchResult) => {
  // In New Tab, clicking a result from an old tree should just open the URL,
  // not open the whole tree. Tree context is only via explicit actions.
  if (item.kind === 'node' && activeTreeId && item.treeId !== activeTreeId) {
    await act.handleExecuteAction(
      'open',
      { kind: 'node', nodeId: item.nodeId, treeId: item.treeId },
      'Opened',
    );
    return;
  }
  await act.handleActivate(item);
}, [activeTreeId, act]);
```

Then replace all references to `act.handleActivate` with `handleActivateNewTab` in NewTabApp.tsx:
- Line ~288: `onActivate={handleActivateNewTab}` (in DashboardView)
- Line ~487: `onActivate={handleActivateNewTab}` (in SpotlightResults)
- Line ~345: `handleActivate: handleActivateNewTab` in the useSpotlightKeyboard options -- BUT be careful here. The keyboard hook's `handleActivate` is used for Enter key activation. This should also use the new tab behavior. So pass `handleActivateNewTab` instead of `act.handleActivate` to useSpotlightKeyboard.

Also update the graph `onNavigate` callback (line ~371) to use `'open'` instead of `'open-node-in-tree'` for foreign tree nodes:
```tsx
onNavigate={(treeId, nodeId) => {
  // In New Tab, always just open the URL -- don't open the whole tree
  void act.handleExecuteAction('open', { kind: 'node', nodeId, treeId }, 'Opened');
}}
```
  </action>
  <verify>
    Build succeeds: `cd /Users/iv/dev/trail/extension && npm run build 2>&1 | tail -5`
    TypeScript check: `npx tsc --noEmit 2>&1 | tail -10`
  </verify>
  <done>
    - Bento bookmarks card stretches to fill full height when continue/recent sections are loading, then smoothly shrinks when data arrives
    - Continue card bottom padding matches bookmarks card padding visually
    - Clicking any search result in New Tab opens just the URL, never opens the whole tree
    - Explicit tree opening only available through context menu / action buttons (existing inline actions still use open-node-in-tree, which is correct)
  </done>
</task>

</tasks>

<verification>
After both tasks:
1. `npm run build` succeeds with no errors
2. `npx tsc --noEmit` passes with no type errors
3. Manual check: Open Spotlight, type a search -- should see thin progress bar at top, no "Loading..." flash
4. Manual check: Open New Tab, search something -- results panel height should not change, spacing should be uniform
5. Manual check: New Tab idle -- bookmarks fill the bento area, then smoothly make room when continue/recent data loads
6. Manual check: Click a result from a non-active tree in New Tab -- should open the URL directly, not open the tree
</verification>

<success_criteria>
- Zero "Loading..." text flash in Spotlight when searching (progress bar shown instead)
- New Tab search results panel is fixed height (no layout jump between idle and search)
- Uniform vertical spacing between all search result rows
- Smooth bento loading transition: bookmarks stretch then animate to share space
- Continue card and bookmarks card have matching visual padding
- Old-tree results in New Tab open URL only on click, not the full tree
</success_criteria>

<output>
After completion, create `.planning/quick/260318-iio-fix-ui-bugs-in-spotlight-and-new-tab-5-t/260318-iio-SUMMARY.md`
</output>
