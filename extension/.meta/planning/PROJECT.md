# Trail — Graph Visualization

## What This Is

Trail is a browser extension that visualizes navigation history as an interactive tree graph. Users explore, organize, and navigate their browsing sessions through a Pixi.js-powered WebGL canvas with tree/mindmap/radial layouts, spatial indexing, adaptive LOD, and animation systems.

## Core Value

The graph must feel instant and responsive at any tree size — pan, zoom, drag, expand/collapse should never drop below 60fps.

## Requirements

### Validated

- ✓ Pixi.js WebGL rendering with GPU acceleration
- ✓ Tidy-tree, mindmap, and radial layout algorithms
- ✓ Spatial index (grid-based) for view frustum culling
- ✓ LOD system (full/low/dot) with adaptive quality policy
- ✓ Offscreen layout pre-computation via Chrome offscreen document
- ✓ Key-based NodeVisual dirty checking
- ✓ View invalidation caching
- ✓ Decouple animation from React render cycle — v1.0
- ✓ Split setData() into static/dynamic/particle APIs — v1.0
- ✓ Cache connection geometry by topology signature — v1.0
- ✓ Spatial hit-test for drag/reparent — v1.0
- ✓ Pool particles and tag dot Graphics objects — v1.0
- ✓ Static/ephemeral graph state separation (GraphSnapshot) — v1.0
- ✓ Offscreen cache signature with collapse + recency state — v1.0
- ✓ Profiling instrumentation with p50/p95 per phase — v1.0

### Active

- [ ] BitmapText/MSDF text for node labels — reduce Text object cost
- [ ] Instanced rendering for dot-LOD nodes — single draw call
- [ ] Custom WebGL shader for node backgrounds — GPU instancing
- [ ] GraphSceneController — React sends commands, scene lives imperatively
- [ ] Semantic LOD with cluster/supernode mode on far zoom

### Out of Scope

- WebGPU compute shaders — Chrome extension compat unclear
- ECS architecture — over-engineering for current scale
- Worker-based layout — hypothesis: serialization overhead may exceed benefit under 5k nodes (deferred to v2, needs profiling to validate)
- MSDF text rendering — separate effort, not in this milestone

## Context

**v1.0 shipped (2026-03-19):** Eliminated per-frame full rebuild cascade during animations. Animation ticks bypass React entirely via imperative onTickRender callback. SpatialIndex only rebuilds on topology change. Connections cached by staticVersion with dirty flag skipping redundant redraws. Drag uses spatial queryNearest instead of O(n) scan. Hover patches 2 nodes instead of rebuilding all N. Graphics objects pooled (particles: 32, tag dots: 4/node). GraphSnapshot type formalizes static/ephemeral separation with incremental patching on collapse/expand. Offscreen cache keys enriched with collapse signature + recency ordering. Phase 8 added big-tree optimizations: flags on bootstrap critical path for exact cache hits, gesture-aware three-tier view invalidation (transform-only/translate-only/full) with 600px overscan, batched requestIdleCallback hydration for trees >=1500 nodes, and connection spatial index for visible-only drawing.

**Key files**:
- `src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx`
- `src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts`
- `src/entrypoints/sidepanel/ui/graph/render/graph-snapshot.ts`
- `src/entrypoints/sidepanel/ui/graph/render/graph-profiler.ts`
- `src/entrypoints/sidepanel/ui/graph/render/spatial-index.ts`
- `src/entrypoints/sidepanel/ui/components/graph/useGraphAnimation.ts`

## Constraints

- **Runtime**: Chrome extension sidepanel — must work within extension APIs
- **Compatibility**: Existing UX must not change — no visual regressions
- **Dependencies**: Pixi.js is the renderer, cannot swap
- **Testing**: No formal test suite for graph — verification via profiling and visual inspection

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Break rebuild cycle before micro-optimizations | Per-frame setData() dominates profile; tuning inside the loop is wasted effort | ✓ Good — setData split + React bypass eliminated the cascade |
| Imperative Pixi updates via ref, bypass React for animation | Canvas animations should not go through React reconciliation | ✓ Good — onTickRender callback reduces re-renders from ~9 to 1 per animation |
| Keep layout in main thread (not Worker) | Hypothesis: serialization overhead may exceed benefit for <5k nodes — deferred to v2, needs profiling data | — Pending (deferred) |
| Connection caching by staticVersion ref counter | Reuse existing version counter instead of computing topology hash | ✓ Good — zero hash overhead, dirty flag skips >80% of redraws |
| Incremental snapshot patching via diffSnapshots | Avoid full SpatialIndex rebuild on collapse/expand | ✓ Good — patchStaticGraph only touches affected nodes |
| Object pooling over object destruction | Eliminate GC pressure from Graphics churn during animation | ✓ Good — healthy GC profile confirmed via Chrome trace |
| Gesture-aware view invalidation | Skip updateVisible during active pan/zoom to prevent per-tick reculling | ✓ Good — transform-only path with 600px overscan eliminates zoom jank |
| Batched idle hydration | Large trees render shells first, hydrate text/favicon in idle batches | ✓ Good — first paint instant, detail fills in progressively |
| Connection spatial index | Query only visible connections instead of scanning entire list | ✓ Good — O(visible) vs O(n) for connection drawing |

---
*Last updated: 2026-03-19 after v1.0 Graph Performance Optimization milestone (complete)*
