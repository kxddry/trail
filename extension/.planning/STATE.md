---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: unknown
last_updated: "2026-03-19T15:27:33.121Z"
progress:
  total_phases: 8
  completed_phases: 8
  total_plans: 15
  completed_plans: 15
---

# State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-18)

**Core value:** Graph must feel instant and responsive at any tree size
**Current focus:** Phase 08 — shared-graph-big-tree-performance-pass

## Current Position

Phase: 08 (shared-graph-big-tree-performance-pass) — COMPLETE
Plan: 3 of 3 (all complete)

## Accumulated Context

### Bootstrap Cache Accuracy (2026-03-19)

Flags (including recencyOrderingV2) are now fetched on the critical path in useBootstrap, alongside settings and tree state. The offscreen document also caches flags and derives recencyOrdering from `cachedFlags.recencyOrderingV2` instead of hardcoding `false`. This ensures layout signature parity between the offscreen precomputer and sidepanel consumer, eliminating cache misses caused by recencyOrdering mismatch.

### Root Cause Analysis (2026-03-18)

The primary performance bottleneck is the `animateTick` → `setAnimationVersion(v+1)` → React re-render → full rebuild cascade:

```
animateTick (RAF, ~60fps during animation)
  → setAnimationVersion(v+1)         [useGraphAnimation.ts:41]
    → React re-render GraphCanvas
      → displayNodes useMemo         [GraphCanvas.tsx:593]
        → visibleDisplayNodes         [GraphCanvas.tsx:605]
          → renderNodes .map()        [GraphCanvas.tsx:1076]
      → connectionPositions new Map() [GraphCanvas.tsx:1135]
        → baseConnections build       [GraphCanvas.tsx:1150]
      → useEffect fires              [GraphCanvas.tsx:1238]
        → renderer.setData()          [full rebuild]
          → new SpatialIndex          [GraphPixiRenderer.ts:1027]
          → updateVisible all         [GraphPixiRenderer.ts:1201]
          → updateConnections clear   [GraphPixiRenderer.ts:1263]
```

Every animation frame (9+ frames per 150ms animation) traverses this entire path. For 500 nodes, this means ~500 object spreads + ~500 Map entries + ~500 SpatialIndex inserts per frame.

### Positions Architecture Decision (2026-03-18)

**basePositions** = output of layout algorithm, part of static snapshot. Changed only on topology/layout change.
**positionOverrides** (animatedTransforms) = animation deltas applied on top of basePositions, part of ephemeral/dynamic state. Changed per-frame during animation.

This distinction is critical for the `setStaticGraph()` / `setDynamicState()` API split in Phase 2.

### Priority Order (7 phases)

1. Profiling infrastructure (Phase 1) — baseline before any changes
2. Split renderer API (Phase 2) — `setStaticGraph` / `setDynamicState` / `setParticles`
3. Bypass React for animation (Phase 3) — imperative via ref
4. Connection caching (Phase 4) — topology signature cache
5. Interaction optimization (Phase 5) — spatial drag, partial offset
6. Object pooling (Phase 6) — particles, tag dots
7. State architecture (Phase 7) — GraphSnapshot type, cache keys

Phases 4-6 are parallelizable after Phase 3.

Micro-optimizations (bitmask keys, numeric SpatialIndex keys) become relevant AFTER Phase 3 removes the rebuild loop.

### Profiling Infrastructure (2026-03-18)

GraphProfiler uses Float64Array circular buffers (window size 60) for zero-allocation recording at hot paths. The `profileSync(phase, fn)` wrapper is used for React useMemo callbacks; `graphProfiler.record(phase, duration)` is used for imperative methods in GraphPixiRenderer. Prefetched layout cache-hit path is kept outside profiling to avoid skewing baselines. Console API: `window.__graphMetrics()`.

### Granular Renderer API (2026-03-18)

GraphPixiRenderer now has three entry points replacing the monolithic setData():

- `setStaticGraph(GraphSnapshot)` — rebuilds SpatialIndex, used on topology/layout changes only
- `setDynamicState(DynamicGraphState)` — patches nodeData map and invalidates visible nodes without index rebuild, used for animation/hover/search
- `setParticles(ParticleRenderModel[])` — updates particle layer independently

Old `setData()` and `RenderData` type removed — GraphCanvas fully migrated to granular API in Plan 02-02.

### GraphCanvas API Migration (2026-03-18)

GraphCanvas now uses three separate useEffects instead of the old monolithic setData call:

- Static useEffect: depends on `staticVersion` counter (tracks basePositions/layoutMode/dimensions changes), calls `setStaticGraph()`
- Dynamic useEffect: depends on renderNodes/connections/showConnections, calls `setDynamicState()`
- Particle useEffect: depends on particleRenderModels, calls `setParticles()`

setDynamicState was hardened post-migration to handle:

- Spatial index position updates during drag (without full rebuild)
- Exit animation node insertion into spatial index
- nodeData map reconciliation to clean up stale exit nodes

### Imperative Animation Path (2026-03-18)

animateTick now bypasses React entirely during animation via `onTickRender` callback pattern:

- `useGraphAnimation` accepts `onTickRender?: () => void` param, stored in `onTickRenderRef`
- During active animation ticks, `animateTick` calls `onTickRenderRef.current()` instead of `invalidateAnimation()`
- `handleTickRender` in GraphCanvas builds NodeRenderModel[] and ConnectionSegment[] imperatively from `latestRenderStateRef` snapshot, pushes directly to renderer via `setDynamicState()` / `setParticles()`
- React reconciliation deferred to animation end: `invalidateAnimation()` + `invalidateParticles()` called only in `!needsLoop` branch
- Result: ~9 React re-renders per 150ms expand/collapse animation reduced to 1 final reconciliation render

Key pattern: `latestRenderStateRef` is assigned after all useMemos in GraphCanvas, so the RAF callback always reads the latest computed state (visibleDisplayNodes, positions, search state, etc.).

Drag reparent preview is skipped in the imperative path — drag and animation are mutually exclusive interactions.

### Connection Caching (2026-03-18)

Base connections are now cached by `staticVersion` via `cachedBaseConnectionsRef`. `buildConnections()` no longer accepts `pathNodeIds` -- all segments are produced with `onPath: false`, making the output purely topology-dependent and cacheable.

Two overlay operations are applied on top of cached base connections:

1. `applyPathHighlight(baseConnections, pathNodeIds)` — toggles `onPath` flag for segments on the root-to-current path. Reuses segment objects when `onPath` is already correct (no allocation).
2. Preview edge (drag reparent) — filters out old parent connection, appends preview segment using `connectionPositions` for geometry.

The imperative tick render path (`handleTickRenderRef.current`) reads `cachedBaseConnectionsRef.current` + `applyPathHighlight` instead of calling `buildConnections` per frame. The `connPositions` Map construction was also removed from the imperative path since drag and animation are mutually exclusive.

Static useEffect passes `baseConnections` (without path overlay) to `setStaticGraph`. Path highlight is ephemeral and handled by the dynamic useEffect via `connections`.

### Connection Dirty Flag (2026-03-18)

`updateConnections()` in GraphPixiRenderer now uses a dirty flag (`connectionsDirty`) and viewport snapshot (`lastConnectionViewRect`) to skip redundant clear+redraw cycles. During animation, when the connections array reference is stable (via Plan 01 caching) and the viewport hasn't changed, the entire connection drawing loop is skipped.

Dirty triggers: `setStaticGraph` (topology change), `setDynamicState` (reference change via `!==`), `refreshTheme`, `setConnectionQuality`, `invalidateAll`. Particles are decoupled from the dirty check and always update every frame (moved to top of `updateConnections`).

### Spatial Drag Optimization (2026-03-18)

SpatialIndex now has `queryNearest(cx, cy, radius, excludeIds?)` returning `{ id, dist } | null` — uses the same grid-cell approach as `query()` with center-distance comparison and a `seen` Set for dedup across cells.

Drag snap detection in GraphCanvas now uses `renderer.queryNearestNode()` (spatial query) instead of `positionsRef.current.forEach()` (linear scan). This is O(nearby) instead of O(n).

During drag, `computeDragOffsetPositions` recomputes only affected nodes (dragged subtree + ancestors to root). `affectedIds` is pre-computed once at drag start via `dragAffectedIdsRef`. `prevDragPositionsRef` stores the previous frame's positions to enable incremental Map updates (shallow copy + selective overwrite).

### Hover Optimization (2026-03-18)

Hover state removed from React render pipeline. `hoverNodeId` no longer appears in the `renderNodes` useMemo dependency array -- `isHoverFocused` is hardcoded to `false` in both the useMemo and the imperative tick render path. Instead, a dedicated `useEffect([hoverNodeId])` calls `renderer.setHoverNodeId()`, which triggers `patchHoverVisual()` -- a targeted 2-node patch (previous hover + next hover) following the same pattern as `patchSelectionVisuals`. `setDynamicState` reconciles the hover flag via `adjustedNode` so React-produced models (which always have `isHoverFocused: false`) get corrected to match the renderer's hover state.

### Object Pooling (2026-03-18)

GraphicsPool class provides acquire/releaseAll/destroyAll for zero-allocation PIXI.Graphics reuse. Takes a parent Container in constructor and auto-adds children, avoiding addChild/removeChild churn.

Particle pool: 32 pre-allocated Graphics in `particlePool` field on GraphPixiRenderer. `releaseAll()` clears and hides each frame, `acquire()` returns visible Graphics for drawing. Overflow creates new Graphics automatically.

Tag dot pool: 4 pre-allocated Graphics per NodeVisual in `tagDotPool` array. `updateTags()` reuses via `clear()`/redraw with `visible` toggle instead of removeChildren+new. Cleaned up by existing `container.destroy({ children: true })`.

### Layout Cache Enrichment (2026-03-18)

CachedLayoutResult now includes `collapseSignature` (sorted comma-joined collapsed node IDs) and `recencyOrdering` (boolean flag). Storage key format: `graph-layout:active:tree:_:0` (treeId:layoutMode:collapseSignature:recencyFlag).

Dual-write strategy: `writeLayoutCache` writes to both the enriched key (exact match) and the base key (`graph-layout:active`) for backward compatibility. `readLayoutCache` tries enriched key first when state params provided, falls back to base key.

Offscreen document accepts optional `collapsedNodeIds` from TREE_UPDATED messages, passes them to `computeLayoutFromTree` which filters via `getVisibleChildren` wrapper. `recencyOrdering` always `false` in offscreen doc (no access to live tab recency data).

GraphCanvas validates `collapseSignature` + `recencyOrdering` match before cache hydration. Uses `??` defaults for backward compat with old cached results. State mismatch discards stale cache and forces fresh layout computation.

### GraphSnapshot Type (2026-03-18)

GraphSnapshot formalizes the static/ephemeral state separation. Defined in `graph-snapshot.ts` with readonly fields: version, nodes, basePositions (ReadonlyMap), connections, layoutMode, nodeWidth, nodeHeight, showConnections.

`createGraphSnapshot()` factory returns `Object.freeze`'d objects for runtime immutability. GraphCanvas constructs snapshot in useMemo (gated by staticVersion), passes to renderer via static useEffect. `snapshotRef` stores current snapshot for imperative animation path access.

`setStaticGraph` now accepts `GraphSnapshot` instead of ad-hoc `StaticGraphData`. `DynamicGraphState` remains a local type in GraphPixiRenderer -- ephemeral state is transient and does not need formalization.

### Incremental Snapshot Patching (2026-03-18)

Collapse/expand now routes through `patchStaticGraph` instead of `setStaticGraph`, avoiding full SpatialIndex rebuild. `diffSnapshots(prev, next)` computes `{ added, removed, moved }` node sets. `patchStaticGraph` applies the diff incrementally: `index.remove` for removed nodes, `index.insert` for added, `index.update` for moved. No `nodeData.clear()`, no `new SpatialIndex()`, no `invalidateAll()`.

GraphCanvas static useEffect uses `prevSnapshotVersionRef` to detect first render (must use `setStaticGraph`) vs subsequent changes. Layout mode and dimension changes also force `setStaticGraph` (SpatialIndex cell size depends on dimensions). All other static changes (collapse/expand, minor topology updates) use the incremental path.

`currentSnapshot` getter on GraphPixiRenderer exposes the current snapshot for comparison without making `data` public.

## Blockers/Concerns

None.

### Roadmap Evolution

- Phase 8 added: Shared Graph Big-Tree Performance Pass

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 260319-3vm | Graph Responsiveness and Open Performance - Quick Wins | 2026-03-18 | e737cabc | [260319-3vm-graph-responsiveness-and-open-performanc](./quick/260319-3vm-graph-responsiveness-and-open-performanc/) |

---
*Last updated: 2026-03-19 (Phase 08 complete, all 15/15 plans executed)*
