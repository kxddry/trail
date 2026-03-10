---
phase: quick-1
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - extension/src/spotlight/spotlight-ipc.ts
  - extension/src/spotlight/useSpotlightSearch.ts
  - extension/src/spotlight/useSpotlightPreview.ts
  - extension/src/spotlight/useSpotlightActions.ts
  - extension/src/spotlight/useSpotlightKeyboard.ts
  - extension/src/spotlight/SpotlightRoot.tsx
  - extension/src/spotlight/SpotlightGraphFrame.tsx
  - extension/src/entrypoints/spotlight-graph/SpotlightGraphApp.tsx
  - extension/src/spotlight/rpc.ts
autonomous: true
requirements: [SPOTLIGHT-REFACTOR, SPOTLIGHT-PERF, SPOTLIGHT-UX, SPOTLIGHT-RELIABILITY]

must_haves:
  truths:
    - "SpotlightRoot.tsx is under 250 lines, composing domain hooks"
    - "All postMessage communication uses typed IPC — no manual type guards in Frame/GraphApp"
    - "Echo effect lookup is O(1) via nodeId-indexed map instead of linear scan"
    - "Session recovery retries with exponential backoff before giving up"
    - "Search result count announced to screen readers via aria-live region"
    - "Keyboard focus pane indicator visually distinguishable"
    - "Typecheck passes with zero errors after refactoring"
  artifacts:
    - path: "extension/src/spotlight/spotlight-ipc.ts"
      provides: "Typed IPC layer — discriminated union messages, send/subscribe helpers"
      exports: ["SpotlightIPCMessage", "sendToGraph", "onGraphMessage", "sendToParent", "onParentMessage"]
    - path: "extension/src/spotlight/useSpotlightSearch.ts"
      provides: "Search pipeline hook — debounce, session bootstrap/recovery, query state"
      exports: ["useSpotlightSearch"]
    - path: "extension/src/spotlight/useSpotlightPreview.ts"
      provides: "Graph preview hook — LRU cache, prefetch, preview resolution"
      exports: ["useSpotlightPreview"]
    - path: "extension/src/spotlight/useSpotlightActions.ts"
      provides: "Action execution hook — inline actions, destructive confirmation, drilldown"
      exports: ["useSpotlightActions"]
    - path: "extension/src/spotlight/useSpotlightKeyboard.ts"
      provides: "Keyboard navigation hook — key dispatch, focus pane, hint application"
      exports: ["useSpotlightKeyboard"]
    - path: "extension/src/spotlight/SpotlightRoot.tsx"
      provides: "Slim glue component composing hooks + JSX"
      min_lines: 100
    - path: "extension/src/spotlight/SpotlightGraphFrame.tsx"
      provides: "Iframe bridge using typed IPC (no manual type guards)"
    - path: "extension/src/entrypoints/spotlight-graph/SpotlightGraphApp.tsx"
      provides: "Graph renderer using typed IPC (no manual type guards)"
  key_links:
    - from: "extension/src/spotlight/useSpotlightSearch.ts"
      to: "extension/src/spotlight/rpc.ts"
      via: "bootstrapSpotlight, searchSpotlight, disposeSpotlightSession"
      pattern: "import.*from.*rpc"
    - from: "extension/src/spotlight/useSpotlightPreview.ts"
      to: "extension/src/spotlight/rpc.ts"
      via: "getSpotlightTreePreview"
      pattern: "import.*getSpotlightTreePreview.*from.*rpc"
    - from: "extension/src/spotlight/SpotlightGraphFrame.tsx"
      to: "extension/src/spotlight/spotlight-ipc.ts"
      via: "sendToGraph, onGraphMessage"
      pattern: "import.*from.*spotlight-ipc"
    - from: "extension/src/entrypoints/spotlight-graph/SpotlightGraphApp.tsx"
      to: "extension/src/spotlight/spotlight-ipc.ts"
      via: "sendToParent, onParentMessage"
      pattern: "import.*from.*spotlight-ipc"
    - from: "extension/src/spotlight/SpotlightRoot.tsx"
      to: "extension/src/spotlight/useSpotlightSearch.ts"
      via: "hook composition"
      pattern: "useSpotlightSearch"
---

<objective>
Decompose SpotlightRoot.tsx (884 lines, 60+ state variables) into domain-focused hooks, introduce a typed IPC layer for postMessage communication, optimize echo effect performance with indexed lookups, add session recovery hardening with backoff, and improve UX/a11y with ARIA live regions and focus indicators.

Purpose: SpotlightRoot is a monolith that mixes search pipeline, graph preview, action execution, keyboard handling, and session management. This makes it hard to reason about, test, and extend. The postMessage layer uses unsafe manual type guards duplicated across files.

Output: 5 new files (1 IPC module + 4 hooks), 3 refactored files (SpotlightRoot, SpotlightGraphFrame, SpotlightGraphApp), all typechecking clean.
</objective>

<execution_context>
@/Users/iv/.claude/get-shit-done/workflows/execute-plan.md
@/Users/iv/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@extension/src/spotlight/SpotlightRoot.tsx
@extension/src/spotlight/SpotlightGraphFrame.tsx
@extension/src/entrypoints/spotlight-graph/SpotlightGraphApp.tsx
@extension/src/spotlight/rpc.ts
@extension/src/spotlight/types.ts
@extension/src/spotlight/lru-map.ts
@extension/src/spotlight/SpotlightHintRow.tsx
@extension/src/spotlight/SpotlightFooter.tsx
@extension/src/spotlight/SpotlightActionMenu.tsx
@extension/src/spotlight/SpotlightRowActions.tsx
@extension/src/spotlight/SpotlightQuickLook.tsx

<interfaces>
<!-- Key types consumed by all hooks and IPC layer -->

From extension/src/spotlight/types.ts (re-exports from @shared/rpc/contracts.js):
```typescript
export type {
  SpotlightBootstrapData,
  SpotlightExecuteActionResponse,
  SpotlightActionId,
  SpotlightActionResult,
  SpotlightActionTarget,
  SpotlightSearchResponse,
  SpotlightSearchResult,
  SpotlightSearchSessionId,
  SpotlightSection,
  SpotlightGraphPreviewData,
} from '@shared/rpc/contracts.js';
```

From extension/src/spotlight/rpc.ts:
```typescript
export async function bootstrapSpotlight(limit?: number): Promise<SpotlightBootstrapData>;
export async function searchSpotlight(sessionId, query, limit, requestSeq, scopeTreeId?): Promise<SpotlightSearchResponse>;
export async function disposeSpotlightSession(sessionId): Promise<void>;
export async function getSpotlightTreePreview(treeId: string): Promise<SpotlightGraphPreviewData | null>;
export async function executeSpotlightAction(actionId, target?, query?): Promise<SpotlightExecuteActionResponse>;
export async function exportTree(treeId?: string): Promise<TrailExportBundle>;
```

From extension/src/spotlight/lru-map.ts:
```typescript
export class LRUMap<K, V> {
  constructor(maxSize: number);
  get(key: K): V | undefined;
  set(key: K, value: V): void;
  has(key: K): boolean;
  clear(): void;
}
```

From extension/src/spotlight/SpotlightHintRow.tsx:
```typescript
export function applySpotlightHint(currentQuery: string, hint: string): string;
export function buildSpotlightHints(query: string): string[];
export function computeGhostSuffix(query: string, activeHint: string | null): string | null;
export function shouldApplyHintOnTab(query: string, candidates: string[]): boolean;
```

From extension/src/spotlight/SpotlightFooter.tsx:
```typescript
export function isDestructiveAction(item: SpotlightSearchResult): boolean;
```

From extension/src/spotlight/SpotlightActionMenu.tsx:
```typescript
export function buildClientContextActions(item: SpotlightSearchResult, activeTreeId: string | null): SpotlightActionResult[];
```
</interfaces>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Create typed IPC layer and extract domain hooks from SpotlightRoot</name>
  <files>
    extension/src/spotlight/spotlight-ipc.ts,
    extension/src/spotlight/useSpotlightSearch.ts,
    extension/src/spotlight/useSpotlightPreview.ts,
    extension/src/spotlight/useSpotlightActions.ts,
    extension/src/spotlight/useSpotlightKeyboard.ts,
    extension/src/spotlight/SpotlightRoot.tsx,
    extension/src/spotlight/SpotlightGraphFrame.tsx,
    extension/src/entrypoints/spotlight-graph/SpotlightGraphApp.tsx
  </files>
  <action>
**Step 1: Create `spotlight-ipc.ts` — typed postMessage IPC**

Define a discriminated union for ALL messages crossing the iframe boundary:

```typescript
import type { NodeId, Url } from '@shared/types/ids.js';
import type { SpotlightGraphPreviewData } from './types.js';

// Parent -> Graph iframe messages
type SetGraphContextMsg = {
  type: 'SET_GRAPH_CONTEXT';
  activeTreeId: string;
  previewData: SpotlightGraphPreviewData | null;
  selectedNodeId: NodeId | null;
  highlightNodeId: NodeId | null;
  selectionIntentId: number;
};

// Graph iframe -> Parent messages
type GraphReadyMsg = { type: 'GRAPH_READY' };
type NavigateMsg = { type: 'NAVIGATE'; treeId: string; nodeId: NodeId; url: Url };
type HoverNodeMsg = { type: 'HOVER_NODE'; treeId: string; nodeId: NodeId | null };

export type ParentToGraphMsg = SetGraphContextMsg;
export type GraphToParentMsg = GraphReadyMsg | NavigateMsg | HoverNodeMsg;
export type SpotlightIPCMessage = ParentToGraphMsg | GraphToParentMsg;
```

Provide typed helpers:
- `sendToGraph(iframe: HTMLIFrameElement, msg: ParentToGraphMsg)` — posts to iframe.contentWindow
- `sendToParent(msg: GraphToParentMsg)` — posts to window.parent
- `onGraphMessage(source: Window | null, handler: (msg: GraphToParentMsg) => void)` — returns cleanup fn; validates `event.source === source`, uses discriminated union `type` field for dispatch (NO manual type guards)
- `onParentMessage(handler: (msg: ParentToGraphMsg) => void)` — returns cleanup fn; uses `type` field validation
- Internal `isSpotlightIPC(data: unknown): data is SpotlightIPCMessage` guard that validates the `type` field exists and is one of the known literals. This is the SINGLE type guard — consumers never write their own.

**Step 2: Extract `useSpotlightSearch.ts`**

Move from SpotlightRoot: bootstrap effect, search-with-debounce effect, session recovery, dispose-on-close effect, dispose-on-unmount effect.

Hook signature:
```typescript
export function useSpotlightSearch(options: {
  isOpen: boolean;
  searchLimit: number;
  debounceMs: number;
  drilldownScopeTreeId: string | null;
}): {
  sessionId: SpotlightSearchSessionId | null;
  bootstrapData: SpotlightBootstrapData | null;
  sections: SpotlightSection[];
  loading: boolean;
  query: string;
  setQuery: (q: string) => void;
  previewCache: LRUMap<string, SpotlightGraphPreviewData>;
};
```

Session recovery hardening: Instead of a single retry on SESSION_EXPIRED, implement exponential backoff — retry up to 3 times with delays [200ms, 800ms, 2000ms]. If all retries fail, set a `sessionError` state. Also add: before the first search after re-opening (when `isOpen` transitions true), do a lightweight bootstrap (not just rely on cache) — this handles 15min TTL expiry while spotlight was closed.

The `previewCache` is exposed so the preview hook can share it (it's already a ref in SpotlightRoot). Internally use `useRef(new LRUMap(...))`.

**Step 3: Extract `useSpotlightPreview.ts`**

Move from SpotlightRoot: previewTreeId computation, preview data fetching effect, prefetchPreviews function.

Hook signature:
```typescript
export function useSpotlightPreview(options: {
  activeTreeId: string | null;
  drilldownScope: { treeId: string; treeName: string } | null;
  effectiveItem: SpotlightSearchResult | null;
  hoveredGraphTarget: SpotlightNodeTarget | null;
  sections: SpotlightSection[];
  previewCache: LRUMap<string, SpotlightGraphPreviewData>;
}): {
  previewTreeId: string | null;
  graphPreviewData: SpotlightGraphPreviewData | null;
  graphPreviewLoading: boolean;
  setGraphPreviewData: (data: SpotlightGraphPreviewData | null) => void;
  setGraphPreviewLoading: (loading: boolean) => void;
};
```

Expose setters because the drilldown action (in useSpotlightActions) needs to directly set preview data when entering a drilldown tree.

Build echo index optimization inside this hook: create `Record<string, SpotlightSearchResult>` (keyed by `${treeId}:${nodeId}`) from `sections.flatMap(s => s.items)` for O(1) lookup. Replace the `flatItems.find(...)` linear scan in `hoveredGraphKey` computation. Export the echo index via return value so SpotlightRoot can use it for hoveredGraphItem resolution:
```typescript
echoIndex: Map<string, SpotlightSearchResult>;  // key: `${treeId}:${nodeId}`
```

**Step 4: Extract `useSpotlightActions.ts`**

Move from SpotlightRoot: handleActivate, handleExecuteAction, handleInlineAction, handleConfirmDestructive, handleActionMenuSelect, exitDrilldown, toggleSection, plus all the state these depend on (actionMenuActions, confirmingAction, quickLookItem, drilldownScope, drilldownTransition, collapsedSections, statusText, etc.).

Hook signature:
```typescript
export function useSpotlightActions(options: {
  activeTreeId: string | null;
  query: string;
  close: () => void;
  flatItems: SpotlightSearchResult[];
  previewCache: LRUMap<string, SpotlightGraphPreviewData>;
  setGraphPreviewData: (data: SpotlightGraphPreviewData | null) => void;
  setGraphPreviewLoading: (loading: boolean) => void;
  setQuery: (q: string) => void;
}): {
  actionMenuActions: SpotlightActionResult[] | null;
  setActionMenuActions: (actions: SpotlightActionResult[] | null) => void;
  confirmingAction: SpotlightSearchResult | null;
  setConfirmingAction: (action: SpotlightSearchResult | null) => void;
  quickLookItem: SpotlightSearchResult | null;
  setQuickLookItem: (item: SpotlightSearchResult | null) => void;
  drilldownScope: { treeId: string; treeName: string } | null;
  drilldownTransition: 'idle' | 'entering' | 'exiting';
  predrilldownQuery: string;
  collapsedSections: Set<string>;
  statusText: string | null;
  setStatusText: (text: string | null) => void;
  handleActivate: (item: SpotlightSearchResult) => Promise<void>;
  handleInlineAction: (actionId: SpotlightActionId, target: SpotlightActionTarget | undefined, statusText: string) => Promise<void>;
  handleActionMenuSelect: (action: SpotlightActionResult) => void;
  handleConfirmDestructive: () => Promise<void>;
  exitDrilldown: () => void;
  toggleSection: (sectionId: string) => void;
};
```

Keep the `downloadBundle` and `sanitizeFilename` helpers as module-level functions in this file (they are only used by handleActivate for export-tree).

**Step 5: Extract `useSpotlightKeyboard.ts`**

Move from SpotlightRoot: the entire `handleKeyDownCapture` callback.

Hook signature:
```typescript
export function useSpotlightKeyboard(options: {
  query: string;
  selectedItem: SpotlightSearchResult | null;
  hoveredGraphItem: SpotlightSearchResult | null;
  activeTreeId: string | null;
  hintCandidates: string[];
  activeHint: string | null;
  actionMenuActions: SpotlightActionResult[] | null;
  setActionMenuActions: (actions: SpotlightActionResult[] | null) => void;
  confirmingAction: SpotlightSearchResult | null;
  quickLookItem: SpotlightSearchResult | null;
  setQuickLookItem: (item: SpotlightSearchResult | null) => void;
  helpOpen: boolean;
  setHelpOpen: (open: boolean) => void;
  drilldownScope: { treeId: string; treeName: string } | null;
  selectedFocusPane: 'list' | 'graph';
  setSelectedFocusPane: (pane: 'list' | 'graph') => void;
  setQuery: (q: string) => void;
  close: () => void;
  exitDrilldown: () => void;
  handleActivate: (item: SpotlightSearchResult) => Promise<void>;
  handleApplyHint: (hint: string) => void;
  handleConfirmDestructive: () => Promise<void>;
  setConfirmingAction: (action: SpotlightSearchResult | null) => void;
}): {
  handleKeyDownCapture: (event: React.KeyboardEvent) => void;
};
```

**Step 6: Refactor `SpotlightRoot.tsx` to ~200 lines**

Compose all 4 hooks + remaining UI state (`isOpen`, `hasBeenOpened`, `helpOpen`, `selectedKey`, `selectedFocusPane`, `hoveredGraphTarget`). Keep `itemByKey`, `flatItems`, hint computations, and the JSX render.

Move `resolveNodeTarget`, `resolvePreviewTreeId`, `resolveCopyUrlItem`, `renderItemTitle`, `renderItemSubtitle`, `getItemMeta` to a new section at the bottom of SpotlightRoot (they are pure rendering helpers) OR into their respective hooks where appropriate (resolveNodeTarget and resolvePreviewTreeId into useSpotlightPreview since they serve preview resolution).

Replace `hoveredGraphKey` linear scan with the O(1) echo index from useSpotlightPreview:
```typescript
const hoveredGraphKey = useMemo(() => {
  if (!hoveredGraphTarget) return null;
  const key = `${hoveredGraphTarget.treeId}:${hoveredGraphTarget.nodeId}`;
  return echoIndex.get(key)?.key ?? null;
}, [hoveredGraphTarget, echoIndex]);
```

**Step 7: Refactor `SpotlightGraphFrame.tsx` to use typed IPC**

- Remove all 3 manual type guard functions (`isNavigateMessage`, `isGraphReadyMessage`, `isHoverNodeMessage`)
- Import `sendToGraph`, `onGraphMessage` from `spotlight-ipc.ts`
- Replace `sendContext` with `sendToGraph(iframeRef.current!, msg)`
- Replace `window.addEventListener('message', handleMessage)` with `onGraphMessage(iframeRef.current?.contentWindow, handler)` which returns a cleanup function
- The handler receives already-typed messages; switch on `msg.type`

**Step 8: Refactor `SpotlightGraphApp.tsx` to use typed IPC**

- Remove `isSetGraphContextMessage` and `isValidNodeId` manual type guards
- Import `sendToParent`, `onParentMessage` from `../../spotlight/spotlight-ipc.ts`
- Replace all `window.parent.postMessage(...)` calls with `sendToParent(...)` — typed, no raw `*` origin strings scattered everywhere
- Replace `window.addEventListener('message', handleMessage)` with `onParentMessage(handler)` returning cleanup

**IMPORTANT constraints:**
- Do NOT change rpc.ts — it stays as-is (the RPC caching idea from CONTEXT was for frequent calls but the current fire-and-forget pattern is fine; actual caching is in the LRU preview cache which stays)
- Do NOT change CSS — no visual regressions
- Every hook must use immutable state update patterns (new objects, not mutations)
- All files must be under 400 lines each
  </action>
  <verify>
    <automated>cd /Users/iv/dev/trail/extension && pnpm typecheck:ui 2>&1 | tail -20</automated>
  </verify>
  <done>
    - SpotlightRoot.tsx is under 250 lines (was 884)
    - 4 domain hooks exist (useSpotlightSearch, useSpotlightPreview, useSpotlightActions, useSpotlightKeyboard)
    - spotlight-ipc.ts exists with discriminated union types and typed send/subscribe helpers
    - SpotlightGraphFrame.tsx and SpotlightGraphApp.tsx have zero manual type guard functions
    - All imports resolve, typecheck passes with zero errors
  </done>
</task>

<task type="auto">
  <name>Task 2: Performance optimizations and session recovery hardening</name>
  <files>
    extension/src/spotlight/useSpotlightSearch.ts,
    extension/src/spotlight/useSpotlightPreview.ts
  </files>
  <action>
**Performance: Echo index (if not already done in Task 1)**

Verify the echo index is implemented in useSpotlightPreview. The `hoveredGraphKey` computation in SpotlightRoot must use the O(1) indexed lookup instead of `flatItems.find(...)`. The index shape is `Map<string, SpotlightSearchResult>` keyed by `"${treeId}:${nodeId}"` — built from `flatItems` filtering only items with a resolvable nodeTarget.

**Performance: Prefetch deduplication**

In `useSpotlightPreview`, ensure `prefetchPreviews` does not fire concurrent fetches for the same treeId. Track in-flight prefetch promises via a `Set<string>` ref. Before fetching, check both the LRU cache AND the in-flight set. Remove from in-flight set in `.finally()`.

**Session recovery: Exponential backoff**

In `useSpotlightSearch`, verify the search error handler for `SESSION_EXPIRED` implements:
1. Retry bootstrap up to 3 times with delays [200, 800, 2000] ms
2. Between retries, keep `loading: true`
3. If all retries fail, set `sessionError: string` state (exposed in hook return)
4. Clear `sessionError` when spotlight opens fresh (isOpen transitions true)

Also add a health-check before first search: when `isOpen` becomes true AND there was a previous sessionId, call `bootstrapSpotlight` fresh (don't rely on potentially expired session). The current code already does this (bootstrap effect runs on `isOpen` change), so verify it clears the old session properly.

**Session recovery: Graceful SW wake handling**

In the RPC layer or in useSpotlightSearch, if `browser.runtime.sendMessage` throws with "Could not establish connection" or "Extension context invalidated", treat it like SESSION_EXPIRED — trigger re-bootstrap. This handles the case where the service worker died and needs to be re-woken.

Implementation: In `useSpotlightSearch`, wrap the search RPC call to catch connection errors and map them to SESSION_EXPIRED recovery flow. Do NOT modify rpc.ts directly — instead wrap at the hook level:

```typescript
function isConnectionError(error: unknown): boolean {
  const msg = (error as Error)?.message ?? '';
  return msg.includes('Could not establish connection')
    || msg.includes('Extension context invalidated')
    || msg.includes('Receiving end does not exist');
}
```

When caught, funnel into the same SESSION_EXPIRED retry logic.
  </action>
  <verify>
    <automated>cd /Users/iv/dev/trail/extension && pnpm typecheck:ui 2>&1 | tail -20</automated>
  </verify>
  <done>
    - Echo index provides O(1) lookup for hoveredGraphKey (no .find() on flatItems)
    - Prefetch deduplication prevents duplicate in-flight requests for same treeId
    - Session recovery retries with exponential backoff [200, 800, 2000]ms
    - Connection errors (SW death) handled as session recovery triggers
    - Typecheck passes
  </done>
</task>

<task type="auto">
  <name>Task 3: UX/a11y improvements — ARIA live regions, focus indicators, loading states</name>
  <files>
    extension/src/spotlight/SpotlightRoot.tsx,
    extension/src/spotlight/useSpotlightSearch.ts
  </files>
  <action>
**ARIA live region for search result counts**

In SpotlightRoot's JSX, add an `aria-live="polite"` region that announces the result count when search completes. Use a visually hidden element (sr-only pattern via inline styles: `position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap;`):

```tsx
<div aria-live="polite" aria-atomic="true" style={srOnlyStyle}>
  {!loading && sections.length > 0
    ? `${flatItems.length} result${flatItems.length === 1 ? '' : 's'} found`
    : !loading && query && sections.length === 0
    ? 'No results found'
    : ''}
</div>
```

Place this inside the `<Command>` component, before the panels div.

**ARIA labels on icon buttons**

Add `aria-label` attributes to:
- Breadcrumb back button: `aria-label="Exit drilldown"` (currently just shows arrow character)
- Section collapse/expand buttons: `aria-label={collapsed ? 'Expand section' : 'Collapse section'}` plus `aria-expanded={!collapsed}`
- Confirm dialog buttons already have text content, so they are fine.

**Focus pane visual indicator**

The `data-focus` attribute is already set on `.spotlight-right` — verify that `selectedFocusPane` is toggled on Tab key. The CSS likely already handles this, but if the left panel doesn't have a `data-focus` indicator, add `data-focus={selectedFocusPane}` to `.spotlight-left` div as well, so CSS can style the active pane (e.g., subtle border highlight). Do NOT write new CSS — just add the data attribute for CSS to hook into.

**Loading state for graph preview**

The current loading state shows "Loading tree preview..." text. Enhance it minimally: add `role="status"` and `aria-label="Loading tree preview"` so screen readers announce it.

**Session error state**

If `sessionError` is set from the search hook (all recovery retries failed), show a user-friendly message in the left panel instead of an empty state:

```tsx
{sessionError ? (
  <div className="spotlight-empty" role="alert">
    Connection lost. Close and reopen spotlight to retry.
  </div>
) : loading ? (
  ...existing loading...
```

**IMPORTANT:**
- Do NOT add any new CSS files or modify existing CSS
- Do NOT change keyboard behavior — only add ARIA attributes
- Use inline styles ONLY for the sr-only pattern (no other inline styles)
- The sr-only element must be inside the component tree, not portaled
  </action>
  <verify>
    <automated>cd /Users/iv/dev/trail/extension && pnpm typecheck:ui 2>&1 | tail -20</automated>
  </verify>
  <done>
    - aria-live region announces search result counts
    - Breadcrumb back button has aria-label
    - Section toggle buttons have aria-label and aria-expanded
    - Graph loading indicator has role="status"
    - Session error state shows user-friendly message with role="alert"
    - data-focus attribute on left panel for CSS hookability
    - Typecheck passes
  </done>
</task>

</tasks>

<verification>
1. `cd /Users/iv/dev/trail/extension && pnpm typecheck:ui` — zero errors
2. `wc -l extension/src/spotlight/SpotlightRoot.tsx` — under 250 lines
3. `wc -l extension/src/spotlight/useSpotlight*.ts` — each under 400 lines
4. `grep -c "type guard" extension/src/spotlight/SpotlightGraphFrame.tsx extension/src/entrypoints/spotlight-graph/SpotlightGraphApp.tsx` — zero manual type guards
5. `grep "aria-live\|aria-label\|aria-expanded\|role=" extension/src/spotlight/SpotlightRoot.tsx` — ARIA attributes present
6. Open extension, activate spotlight, verify: search works, graph preview loads, keyboard navigation works, echo hover sync works
</verification>

<success_criteria>
- SpotlightRoot.tsx reduced from 884 to ~200 lines
- 4 domain hooks + 1 IPC module created
- All postMessage type guards centralized in spotlight-ipc.ts
- Echo hover lookup is O(1) (indexed map, not linear find)
- Session recovery handles exponential backoff and SW connection loss
- ARIA live regions, labels, and roles added for screen reader support
- Zero TypeScript errors across all modified files
</success_criteria>

<output>
After completion, create `.planning/quick/1-improve-spotlight-refactoring-performanc/1-SUMMARY.md`
</output>
