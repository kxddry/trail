---
gsd_state_version: 1.0
milestone: v1.0
milestone_name: milestone
status: in-progress
last_updated: "2026-03-18T17:02:45.000Z"
last_activity: 2026-03-18 — Completed 04-01-PLAN.md (Connection caching by staticVersion)
progress:
  total_phases: 7
  completed_phases: 3
  total_plans: 6
  completed_plans: 5
---

# State

## Project Reference

See: .planning/PROJECT.md (updated 2026-03-18)

**Core value:** Graph must feel instant and responsive at any tree size
**Current focus:** Phase 4 in progress, Plan 01 complete (connection caching by staticVersion)

## Current Position

Phase: 4 (in-progress)
Plan: 1 of 2 complete
Status: In progress
Last activity: 2026-03-18 — Completed 04-01-PLAN.md (Connection caching by staticVersion)

## Accumulated Context

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
- `setStaticGraph(StaticGraphData)` — rebuilds SpatialIndex, used on topology/layout changes only
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

## Blockers/Concerns

None.

---
*Last updated: 2026-03-18*
