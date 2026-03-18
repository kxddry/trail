# Trail — Graph Visualization

## What This Is

Trail is a browser extension that visualizes navigation history as an interactive tree graph. Users explore, organize, and navigate their browsing sessions through a Pixi.js-powered WebGL canvas with tree/mindmap/radial layouts, spatial indexing, adaptive LOD, and animation systems.

## Core Value

The graph must feel instant and responsive at any tree size — pan, zoom, drag, expand/collapse should never drop below 60fps.

## Current Milestone: v1.0 Graph Performance Optimization

**Goal:** Eliminate per-frame full rebuild cascade during animations and interactions, enabling smooth 60fps on trees with 500-5000+ nodes.

**Target improvements:**
- Break the animateTick → React state → setData() rebuild cycle
- Cache connections by topology signature
- Replace linear drag hit-testing with spatial queries
- Separate static graph topology from ephemeral UI state

## Requirements

### Validated

- ✓ Pixi.js WebGL rendering with GPU acceleration
- ✓ Tidy-tree, mindmap, and radial layout algorithms
- ✓ Spatial index (grid-based) for view frustum culling
- ✓ LOD system (full/low/dot) with adaptive quality policy
- ✓ Offscreen layout pre-computation via Chrome offscreen document
- ✓ Key-based NodeVisual dirty checking
- ✓ View invalidation caching

### Active

- [ ] Decouple animation from React render cycle
- [ ] Split setData() into static/dynamic/particle APIs
- [ ] Cache connection geometry by topology signature
- [ ] Spatial hit-test for drag/reparent
- [ ] Pool particles and connection dirty flags
- [ ] Static/ephemeral graph state separation
- [ ] Offscreen cache signature with collapse + recency state

### Out of Scope

- WebGPU compute shaders — Chrome extension compat unclear
- ECS architecture — over-engineering for current scale
- Worker-based layout — hypothesis: serialization overhead may exceed benefit under 5k nodes (deferred to v2, needs profiling to validate)
- MSDF text rendering — separate effort, not in this milestone

## Context

**Renderer**: `GraphPixiRenderer` (1688 lines) — Pixi.js stage with manual render calls (ticker stopped), per-node `NodeVisual` containers with ~12 display objects each.

**Root cause identified**: `useGraphAnimation.ts:41` calls `setAnimationVersion(v+1)` on every RAF tick during animations. This triggers React re-render of `GraphCanvas.tsx`, which recomputes `renderNodes`, `connectionPositions`, `baseConnections` via useMemo chain, then calls `renderer.setData()` which fully rebuilds SpatialIndex and visible set.

**Key files**:
- `src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx` (~1700 lines)
- `src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts` (1688 lines)
- `src/entrypoints/sidepanel/ui/components/graph/useGraphAnimation.ts`
- `src/entrypoints/sidepanel/ui/graph/render/spatial-index.ts`
- `src/entrypoints/sidepanel/ui/graph/render/quality-policy.ts`
- `src/entrypoints/sidepanel/ui/graph/render/view-invalidation.ts`
- `src/entrypoints/sidepanel/ui/components/graph/graph-layout-compute.ts`

## Constraints

- **Runtime**: Chrome extension sidepanel — must work within extension APIs
- **Compatibility**: Existing UX must not change — no visual regressions
- **Dependencies**: Pixi.js is the renderer, cannot swap
- **Testing**: No formal test suite for graph — verification via profiling and visual inspection

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Break rebuild cycle before micro-optimizations | Per-frame setData() dominates profile; tuning inside the loop is wasted effort | — Pending |
| Imperative Pixi updates via ref, bypass React for animation | Canvas animations should not go through React reconciliation | — Pending |
| Keep layout in main thread (not Worker) | Hypothesis: serialization overhead may exceed benefit for <5k nodes — deferred to v2, needs profiling data | — Pending |

---
*Last updated: 2026-03-18 after Graph optimization analysis*
