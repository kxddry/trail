# Phase 8: Shared Graph Big-Tree Performance Pass - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Optimize the shared graph pipeline (sidepanel, spotlight, fullview) for large trees (>=1500 nodes). Four focus areas: bootstrap cache accuracy, deferred node hydration, gesture-aware pan/zoom invalidation, and connection spatial indexing. No user-facing API or settings changes — all work is internal, gated by the existing adaptivePerformance flag.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure/performance phase. Key constraints from the spec:
- 1500-node threshold for large-tree mode (adjustable by later profiling)
- Preserve routed edge shapes: orthogonal stays orthogonal, radial keeps curves
- Simplified mode reduces cost via thinner strokes/lower alpha/deterministic thinning, NOT straight-line fallback
- Reuse existing adaptivePerformance flag — no new user-facing controls
- Pause hydration during gestures, resume on idle

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `SpatialIndex<T>` in `spatial-index.ts` — grid-based spatial hash with insert/update/remove/query/queryNearest. Currently nodes-only, needs connection support
- `GraphProfiler` in `graph-profiler.ts` — Float64Array circular buffers, `profileSync()` wrapper, `window.__graphMetrics()` console API
- `GraphicsPool` in `GraphPixiRenderer.ts` — acquire/releaseAll for zero-allocation PIXI.Graphics reuse (particles, tag dots)
- `NodeVisual.deferContent` flag — already exists for skipping text/favicon on first update; basis for batched hydration
- `updateQualityPolicy()` in `quality-policy.ts` — EWMA scoring with hysteresis, maps to detail/connection quality modes
- `cachedBaseConnectionsRef` — connection caching by staticVersion (from Phase 4)
- `patchStaticGraph()` / `diffSnapshots()` — incremental SpatialIndex patching (from Phase 7)
- `consumePrefetchedLayout()` / `globalThis.__trailCachedLayout` — existing cache hydration path in GraphCanvas

### Established Patterns
- **Static/dynamic split**: `setStaticGraph(GraphSnapshot)` vs `setDynamicState(DynamicGraphState)` vs `setParticles()`
- **Imperative animation**: `onTickRender` callback bypasses React during animation frames
- **Spatial drag**: `queryNearestNode()` spatial query replaces linear scan
- **Connection dirty flag**: `connectionsDirty` + `lastConnectionViewRect` skip redundant redraw
- **Layout signature**: deterministic hash of mode/density/gaps/radial/collapse/recency in `computeLayoutSignature()`
- **Dual-write cache**: exact key + fallback base key in `writeLayoutCache()`

### Integration Points
- `useBootstrap()` — critical path fetches settings+treeState, deferred fetches flags. Flags need to join critical path for layout signature
- `offscreen-graph/main.ts` — hardcodes `recencyOrdering: false`, needs real flag from settings/flags
- `decideViewInvalidation()` — pure function, input struct needs gesture fields
- `GraphPixiRenderer.updateConnections()` — scans full connection list, needs spatial query
- `GraphCanvas.tsx` — static useEffect consumes snapshot, needs gesture-aware view handling
- `quality-policy.ts` — frame-time thresholds only, no node-count awareness

</code_context>

<specifics>
## Specific Ideas

From the detailed spec:
- Bootstrap: compute exact layout signature from settings+treeState+flags BEFORE bootstrapGraph(), write to globalThis.__trailCachedLayout for synchronous hydration
- Large-tree first paint: two-stage rendering — cheap shell (background rect + dot) first, then text/favicon/tag hydration in requestIdleCallback batches
- Pan/zoom: interaction overscan rect (larger than current 200px padding), transform-only path during active wheel/pinch, full recull only on gesture idle or overscan exit
- Connections: add ConnectionSpatialIndex in renderer, query visible-only on redraw. Radial edges keep bezier curves in simplified mode with thinner strokes + lower alpha + deterministic thinning of non-path edges
- Metrics: add connectionQueryMs, deferredHydrationMs, skippedFullInvalidationCount to GraphRenderMetrics

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>
