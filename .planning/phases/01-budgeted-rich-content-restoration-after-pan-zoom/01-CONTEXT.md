# Phase 1: Budgeted Rich-Content Restoration After Pan/Zoom - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Optimize the moment of exiting low/dot LOD when the graph turns on text and favicons all at once. Replace synchronous burst rich-content restoration with frame-budgeted progressive hydration. Visual result must remain identical — only the pace of text/favicon/badge return changes.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion

All implementation choices are at Claude's discretion — pure infrastructure/performance phase. The user's spec provides all design direction:

- GraphArea: after gesture end, run a short "restore" phase instead of jumping to full immediately
- GraphPixiRenderer.deferContent: generalize to any expensive LOD upgrade (dot→low/full, low→full), not just new nodes in large trees
- Priority queue: current > hover > selected > search-focused > path nodes > viewport center > rest
- Favicon: batch invalidation instead of per-icon invalidate(); coalesce ready textures into restore queue
- textResolution: freeze/cap during active zoom/pinch, restore after idle + queue drain
- Budgeted hydration for ALL tree sizes (not just large); small trees get bigger batch size
- Tab-count badge: cache CanvasTextMetrics.measureText widths
- Favicon cache: explicit LRU with limit relative to visible node count (prevent thrash on long pans)
- BitmapText: only if profiler still shows bad p95 after staged restore (second phase, not this one)
- GraphRenderMetrics: add backlog size, batch time, restored node count
- Internal restore-policy helper in renderer; no Zustand store or settings changes
- Must work in both sidepanel and fullview (same shared renderer)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GraphPixiRenderer` (2148 lines) — already has `deferContent` boolean per NodeVisual, `hydrationQueue: NodeId[]`, `scheduleHydration()` via requestIdleCallback, `HYDRATION_BATCH_SIZE = 30`, `LARGE_TREE_THRESHOLD = 1500`
- `NodeVisual.hydrateContent()` — sets deferContent=false, clears keys to force re-render
- `resolveNodeLod()` — per-node LOD with forceDetail for current/selected/search/hover nodes
- `decideViewInvalidation()` in view-invalidation.ts — gesture-aware "transform-only"/"full" decisions with 600px overscan
- `quality-policy.ts` — EWMA + p95 hysteresis state machine, already computes adaptive detailMode
- Global `faviconTextureCache` — Map with FAVICON_CACHE_MAX=256, FIFO eviction (not LRU)
- `loadFaviconTexture()` — promise dedup per URL, calls `invalidate()` per loaded texture
- `syncTextResolution()` — recomputes from `view.scale * devicePixelRatio`, range 1-8

### Established Patterns
- Gesture state: `isGestureActive` boolean toggled in `setView(view, isGesture)`
- LOD transitions flow: GraphArea.gestureActive → detailMode prop → renderer.setDetailMode() → invalidateAll()
- Hydration: post-gesture `scheduleHydration()` via `requestIdleCallback`, batch of 30 per idle callback
- Metrics: `GraphRenderMetrics` object updated in updateVisible/render, reported via `metricsListener` callback to GraphArea
- Quality policy: GraphArea receives metrics → updateQualityPolicy() → sets qualityPolicyState → feeds back detailMode

### Integration Points
- `GraphArea.tsx:130-144` — detailMode computation (gestureActive → "low")
- `GraphPixiRenderer.setView()` — wasGesture/isGesture transition triggers scheduleHydration
- `GraphPixiRenderer.updateVisible()` — node creation, deferContent gating, hydration queue push
- `NodeVisual.update()` — reads detailMode, textResolution, applies text/favicon/tags per LOD
- `NodeVisual.requestFaviconLoad()` — per-icon invalidate() on load
- `NodeVisual.updateBadges()` — CanvasTextMetrics.measureText per badge render

### Key Files
- `extension/src/features/graph/components/graph/GraphArea.tsx` (178 lines)
- `extension/src/features/graph/components/graph/GraphCanvas.tsx` (~2150 lines)
- `extension/src/features/graph/graph/render/GraphPixiRenderer.ts` (2148 lines)
- `extension/src/features/graph/graph/render/quality-policy.ts`
- `extension/src/features/graph/graph/render/view-invalidation.ts`

</code_context>

<specifics>
## Specific Ideas

User-provided spec details:
- Leave backgrounds, outlines, positions, connections instant — only text/URL/tag dots/tab badges/favicon go through the queue
- Priority order: current, hover, selected, search-focused, path-nodes, then viewport center, then rest
- Remove the `small tree → immediate next-frame hydration` path; use budgeted for all, just with bigger batch for small trees
- Favicon cache: explicit LRU, raise limit relative to actual visible node count
- If p95 still bad after this work, second step: PIXI.Text → BitmapText/bitmap font (but NOT in this phase)
- Extend GraphRenderMetrics with: backlog size, batch time, restored node count

</specifics>

<deferred>
## Deferred Ideas

- BitmapText migration for title/url/badge — only if profiler still shows bad p95 after staged restore

</deferred>
