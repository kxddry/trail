# Roadmap: Trail Graph Performance v1.0

**Created:** 2026-03-18
**Milestone:** v1.0 — Graph Performance Optimization
**Phases:** 8

## Phase 1: Profiling Infrastructure

**Goal:** Add per-phase timing instrumentation to establish baseline measurements before any optimization work.

**Requirements:** RCYC-04

**Plans:** 1 plan

Plans:
- [x] 01-01-PLAN.md — GraphProfiler utility + instrument 7 pipeline measurement points

**Success Criteria:**
1. Timing instrumentation added for: layout, renderNodes, buildConnections, computeOffsetPositions, setData, updateVisible, updateConnections
2. p50/p95 statistics tracked over sliding window (last 60 frames)
3. Baseline measurements captured on 500-node tree: idle, pan/zoom, expand/collapse, drag
4. Console-accessible API to dump current metrics (e.g. `window.__graphMetrics()`)

## Phase 2: Split Renderer API

**Goal:** Replace monolithic `setData()` with granular API: `setStaticGraph()` for topology + basePositions, `setDynamicState()` for ephemeral updates (positionOverrides, openProgress, hover, search), `setParticles()` for animations. SpatialIndex only rebuilt on topology change.

**Requirements:** RCYC-02, RCYC-03

**Plans:** 2/2 plans complete

Plans:
- [x] 02-01-PLAN.md — Implement setStaticGraph / setDynamicState / setParticles on GraphPixiRenderer
- [x] 02-02-PLAN.md — Migrate GraphCanvas to granular API, remove setData, visual verification

**Success Criteria:**
1. `setData()` replaced with `setStaticGraph(snapshot)` / `setDynamicState(state)` / `setParticles(particles)`
2. `setStaticGraph()` receives topology + basePositions, rebuilds SpatialIndex; `setDynamicState()` patches visible nodes without index rebuild
3. `setDynamicState()` accepts: positionOverrides (animation deltas, not base positions), openProgress, hover ID, search state
4. GraphCanvas calls `setStaticGraph()` only on layout/topology change, `setDynamicState()` on animation/interaction
5. No visual regressions: all existing interactions work identically

## Phase 3: Bypass React for Animation

**Goal:** Make `animateTick` update the renderer imperatively via ref, bypassing React state entirely during animation. React state updated only when animation completes.

**Requirements:** RCYC-01

**Plans:** 1/1 plans complete

Plans:
- [x] 03-01-PLAN.md — Wire imperative renderer updates from animateTick via onTickRender callback

**Success Criteria:**
1. `animateTick` calls `renderer.setDynamicState()` directly through ref — no `setAnimationVersion()` during animation
2. React re-render of GraphCanvas does NOT occur on animation RAF ticks
3. `animationVersion` state updated once at animation end (for final React reconciliation)
4. Pan/zoom during expand/collapse animation maintains <16ms frame time on 500-node tree
5. Profiling confirms: setData/updateVisible calls drop from ~9/animation to 1/animation

## Phase 4: Connection Caching

**Goal:** Cache connection geometry by topology/layout signature. Path highlight and preview edge updated independently from base connections.

**Requirements:** CONN-01, CONN-02, CONN-03

**Plans:** 2/2 plans complete

Plans:
- [x] 04-01-PLAN.md — Cache base connections by staticVersion, separate path highlight and preview edge overlays
- [x] 04-02-PLAN.md — Add dirty flag to updateConnections, visual verification

**Success Criteria:**
1. `ConnectionSegment[]` cached with signature derived from: layout positions hash + layout mode + hide-root flag
2. Cache invalidated only on layout change, not on animation/hover/selection
3. Path highlight (root->current) updated by toggling `onPath` flag on existing segments, not rebuilding all
4. Preview edge (drag reparent) added/removed without regenerating base connections
5. `updateConnections()` uses dirty flag — skips clear+redraw when connections unchanged
6. Connection rendering time drops by >80% during animation (measured via Phase 1 profiling)

## Phase 5: Interaction Optimization

**Goal:** Replace linear position scanning in drag/reparent with spatial queries. Selection and hover updates bypass full renderNodes rebuild.

**Requirements:** INTR-01, INTR-02, INTR-03

**Plans:** 2 plans

Plans:
- [x] 05-01-PLAN.md — SpatialIndex queryNearest + spatial drag snap + partial offset computation
- [x] 05-02-PLAN.md — Imperative hover patch bypassing renderNodes rebuild

**Success Criteria:**
1. Drag nearest-parent detection uses `SpatialIndex.queryNearest(worldX, worldY, radius)` — O(nearby) instead of O(n)
2. `queryNearest()` method added to SpatialIndex class
3. `computeOffsetPositions()` during drag only recalculates dragged node subtree + direct ancestors, not full Map
4. Hover and selection changes call `renderer.setDynamicState()` targeting only affected nodes
5. Drag reparent preview maintains <16ms frame time on 2000-node tree

## Phase 6: Object Pooling

**Goal:** Pool frequently created/destroyed PIXI Graphics objects to eliminate GC pressure during animations.

**Requirements:** POOL-01, POOL-02

**Plans:** 1 plan

Plans:
- [x] 06-01-PLAN.md — GraphicsPool for particles (32) + per-NodeVisual tag dot pooling (4)

**Success Criteria:**
1. Particle Graphics objects drawn from a pre-allocated pool (size 32), returned on animation end
2. `updateParticles()` no longer calls `removeChildren()` + `child.destroy()` per frame
3. Tag dot Graphics objects in NodeVisual pooled (max 4 per node), reused across `updateTags()` calls
4. `updateTags()` no longer calls `removeChildren()` + `new PIXI.Graphics()` per update
5. No GC spikes visible in Chrome DevTools during 5-minute expand/collapse interaction session

## Phase 7: State Architecture

**Goal:** Formalize static/ephemeral separation with GraphSnapshot type. Improve offscreen layout cache hit rate with richer cache keys.

**Requirements:** ARCH-01, ARCH-02, ARCH-03

**Plans:** 3 plans

Plans:
- [x] 07-01-PLAN.md — GraphSnapshot type + renderer/GraphCanvas integration (ARCH-01, ARCH-02)
- [x] 07-02-PLAN.md — Offscreen layout cache key enrichment with collapse state + recency signature (ARCH-03)
- [ ] 07-03-PLAN.md — Incremental snapshot patching for collapse/expand (gap closure)

**Success Criteria:**
1. `GraphSnapshot` type defined: node rects + basePositions, connection geometry, layoutMode, version number
2. Static snapshot created on layout change, immutable until next layout change
3. Ephemeral state (view, selection, hover, search, animation offsets) updates without touching snapshot
4. Offscreen layout cache key includes: layout mode + collapse state hash + recency ordering signature
5. Cache hit rate measurable — warm opens reuse cached layout in >90% of cases
6. Expand/collapse triggers incremental snapshot update (affected subtree only), not full rebuild

## Phase 8: Shared Graph Big-Tree Performance Pass

**Goal:** Optimize the shared graph pipeline for large trees (>=1500 nodes) across four areas: bootstrap cache accuracy, deferred node hydration, gesture-aware view invalidation, and connection spatial indexing.

**Requirements:** BOOT-01, BOOT-02, GSTR-01, GSTR-02, HYDR-01, CIDX-01, METR-01

**Depends on:** Phase 7

**Plans:** 3 plans

Plans:
- [ ] 08-01-PLAN.md — Bootstrap cache accuracy: flags on critical path + offscreen recencyOrdering fix
- [ ] 08-02-PLAN.md — Gesture-aware view invalidation with overscan and transform-only fast path
- [ ] 08-03-PLAN.md — Deferred node hydration + connection spatial indexing + profiler extension

**Success Criteria:**
1. Flags (including recencyOrdering) available before first GraphCanvas render — layout signature matches offscreen precomputer
2. Offscreen layout precomputer uses real recencyOrdering flag, not hardcoded false
3. During active gestures, renderer skips updateVisible (transform-only path) — `skippedFullInvalidationCount` > 0
4. Overscan padding (600px) absorbs pan/zoom during gestures without triggering reculling
5. Large trees (>=1500 nodes) show node shells on first paint, text/favicon hydrates in idle batches
6. Connection drawing iterates only spatially-visible connections, not the full array
7. `window.__graphMetrics()` shows connectionQuery and deferredHydration phases with recorded samples

---

## Progress

| Phase | Status | Requirements | Coverage |
|-------|--------|-------------|----------|
| 1 | Complete | RCYC-04 | 1/1 |
| 2 | Complete | RCYC-02, RCYC-03 | 2/2 |
| 3 | Complete | RCYC-01 | 1/1 |
| 4 | Complete | CONN-01..03 | 3/3 |
| 5 | Complete | INTR-01..03 | 3/3 |
| 6 | Complete | POOL-01..02 | 2/2 |
| 7 | In Progress | ARCH-01..03 | 3/3 |
| 8 | Planned | BOOT-01..02, GSTR-01..02, HYDR-01, CIDX-01, METR-01 | 7/7 |

**Total:** 22 requirements across 8 phases — 100% coverage

**Parallelization:** Phases 4, 5, 6 are independent and can execute in parallel after Phase 3. Phase 8 Plans 01 and 02 are parallel (Wave 1); Plan 03 depends on Plan 02.

---
*Roadmap created: 2026-03-18*
*Last updated: 2026-03-19*
