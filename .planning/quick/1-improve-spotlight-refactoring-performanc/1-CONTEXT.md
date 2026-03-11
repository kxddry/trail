# Quick Task 1: Improve Spotlight — Refactoring, Performance, UX, Reliability - Context

**Gathered:** 2026-03-10
**Status:** Ready for planning

<domain>
## Task Boundary

Improve the Spotlight feature across 4 dimensions: code architecture (decompose SpotlightRoot.tsx), performance (echo indexing, RPC caching), UX/a11y (focus navigation, loading states, ARIA), and reliability (session recovery hardening).

</domain>

<decisions>
## Implementation Decisions

### Decomposition Strategy
- **Domain-based hooks**: Split SpotlightRoot.tsx (884 lines) into focused hooks by domain:
  - `useSpotlightSearch` — search pipeline, debounce, session recovery
  - `useSpotlightPreview` — graph preview, LRU cache, prefetch
  - `useSpotlightActions` — action execution, confirmations
  - `useSpotlightKeyboard` — keyboard navigation, focus management
- SpotlightRoot becomes ~200-line "glue" component composing hooks + rendering
- Extract sub-components where rendering is complex (ResultsList, GraphPreview panel)

### PostMessage Typing
- **Typed IPC wrapper** (`spotlight-ipc.ts`): Single module shared by both sides
- Discriminated union `SpotlightMessage` for all message types
- `sendToGraph()` and `onGraphMessage()` functions — fire-and-forget, NOT request/response RPC
- Ready-handshake logic encapsulated in the wrapper
- Eliminates scattered manual type guards in SpotlightGraphApp and SpotlightGraphFrame

### Scope
- **All 4 areas in one task**: refactoring → performance → UX/a11y → reliability
- Refactoring goes first (hooks + IPC) as foundation for other changes
- Performance/UX/reliability improvements land in the new decomposed structure
- ~3 tasks for executor: (1) decomposition + IPC, (2) perf optimizations, (3) UX/a11y + reliability

</decisions>

<specifics>
## Specific Ideas

- Echo effect optimization: Build `Record<string, ListItem>` index from flat results for O(1) lookup by node ID
- RPC caching: Lightweight in-memory cache with TTL for frequent calls (bootstrap, tree preview)
- Focus navigation: Arrow keys (left/right) for panel switching alongside Tab, visual indicator for active pane
- Loading states: Skeleton/shimmer for graph preview panel; empty state illustrations
- ARIA: Live regions for search result counts; aria-labels on icon buttons; focus trap verification in Shadow DOM
- Session recovery: Exponential backoff retry; health-check ping before search; graceful SW wake handling

</specifics>
