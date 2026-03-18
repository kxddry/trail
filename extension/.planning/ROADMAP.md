# Roadmap: Trail Graph Performance v1.0

**Created:** 2026-03-18
**Milestone:** v1.0 — Graph Performance Optimization
**Phases:** 3

## Phase 1: Break the Rebuild Cycle

**Goal:** Eliminate per-frame full setData() rebuild during animations by decoupling animation ticks from React state and splitting the renderer API.

**Requirements:** RCYC-01, RCYC-02, RCYC-03, RCYC-04

**Success Criteria:**
1. Animation frames do NOT trigger React re-render of GraphCanvas
2. `setData()` replaced with `setStaticGraph()` / `setDynamicState()` / `setParticles()`
3. SpatialIndex rebuild only occurs on topology change (add/remove/reparent), never on animation tick
4. Profiling instrumentation added: per-phase p50/p95 timing logged to console
5. Pan/zoom during animation maintains <16ms frame time on 500-node tree

## Phase 2: Cache Connections & Optimize Interactions

**Goal:** Cache connection geometry by topology signature, replace linear drag hit-testing with spatial queries, and pool frequently created/destroyed graphics objects.

**Requirements:** CONN-01, CONN-02, CONN-03, INTR-01, INTR-02, INTR-03, POOL-01, POOL-02

**Success Criteria:**
1. Connections only rebuilt when layout/topology changes, not on animation or hover
2. Path highlight updates without regenerating all ConnectionSegment[]
3. Drag nearest-parent detection uses SpatialIndex.query() — O(nearby) not O(n)
4. Particle and tag dot Graphics objects are pooled (no GC spikes during animations)
5. Selection/hover changes update only affected NodeVisuals, not full renderNodes array
6. Drag reparent preview maintains <16ms frame time with 2000-node tree

## Phase 3: Static/Ephemeral State Split

**Goal:** Formally separate static graph topology from ephemeral UI state, introduce GraphSnapshot type, and improve offscreen cache hit rate.

**Requirements:** ARCH-01, ARCH-02, ARCH-03

**Success Criteria:**
1. GraphSnapshot type encapsulates: node rects, connection geometry, layoutMode, version
2. Ephemeral state (view, selection, hover, search, animation offsets) updates without touching static snapshot
3. Offscreen layout cache key includes collapse state + recency ordering signature
4. Cache hit rate measurable — warm opens reuse cached layout without recomputation
5. Expand/collapse triggers incremental snapshot update, not full rebuild

---

## Progress

| Phase | Status | Requirements | Coverage |
|-------|--------|-------------|----------|
| 1 | Not Started | RCYC-01..04 | 4/4 |
| 2 | Not Started | CONN-01..03, INTR-01..03, POOL-01..02 | 8/8 |
| 3 | Not Started | ARCH-01..03 | 3/3 |

**Total:** 15 requirements across 3 phases — 100% coverage ✓

---
*Roadmap created: 2026-03-18*
*Last updated: 2026-03-18*
