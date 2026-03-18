# Requirements: Trail Graph Performance

**Defined:** 2026-03-18
**Core Value:** Graph must feel instant and responsive at any tree size

## v1 Requirements

### Render Cycle

- [x] **RCYC-01**: Animation ticks update renderer imperatively without triggering React re-render
- [x] **RCYC-02**: `setData()` split into `setStaticGraph()` (topology + basePositions), `setDynamicState()` (positionOverrides/openProgress/hover/search), `setParticles()`
- [x] **RCYC-03**: SpatialIndex is only rebuilt on topology change, not on every animation frame
- [x] **RCYC-04**: Profiling instrumentation reports p50/p95 per phase: layout, renderNodes, buildConnections, computeOffsetPositions, setData, updateVisible

### Connection Caching

- [x] **CONN-01**: ConnectionSegment[] cached by topology/layout signature, not rebuilt per frame
- [x] **CONN-02**: Path highlight and preview edge updated separately from base connections
- [x] **CONN-03**: Connection layer uses dirty flags instead of full clear+redraw on every updateVisible

### Interaction Performance

- [x] **INTR-01**: Drag/reparent nearest-parent lookup uses SpatialIndex query instead of linear positionsRef scan
- [x] **INTR-02**: `computeOffsetPositions()` only recalculates dragged subtree and affected ancestors during drag
- [x] **INTR-03**: Selection preview and hover updates bypass full renderNodes rebuild

### State Architecture

- [ ] **ARCH-01**: Static graph snapshot (topology, basePositions, base connections) separated from ephemeral UI state (view, selection, hover, search, positionOverrides/animatedTransforms)
- [ ] **ARCH-02**: GraphSnapshot type introduced: nodes/base rects, connections/base geometry, layoutMode, version
- [ ] **ARCH-03**: Offscreen layout cache key includes collapse state and recency ordering signature

### Object Lifecycle

- [x] **POOL-01**: Particle Graphics objects pooled instead of created/destroyed per frame
- [x] **POOL-02**: Tag dot Graphics objects pooled in NodeVisual instead of removeChildren+new per update

## v2 Requirements

### Deep Rendering

- **REND-01**: BitmapText or MSDF text instead of PIXI.Text for node labels
- **REND-02**: Instanced rendering for dot-LOD nodes (single draw call)
- **REND-03**: Custom WebGL shader for node backgrounds (instanced)

### Architecture

- **SCEN-01**: GraphSceneController — React sends commands, scene lives imperatively on PIXI
- **SCEN-02**: Worker pipeline for layout, edge generation, nearest-node queries (hypothesis — serialization overhead may exceed benefit under 5k nodes; needs profiling to validate)
- **SCEN-03**: Semantic LOD with cluster/supernode mode on far zoom

## Out of Scope

| Feature | Reason |
|---------|--------|
| WebGPU compute | Chrome extension compatibility unclear |
| ECS architecture | Over-engineering for current node counts |
| Canvas framework swap | Pixi.js is deeply integrated, swap is not cost-effective |
| Alternative layout algorithms | Current tidy-tree is O(n) and sufficient |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| RCYC-04 | Phase 1 | Complete |
| RCYC-02 | Phase 2 | Complete |
| RCYC-03 | Phase 2 | Complete |
| RCYC-01 | Phase 3 | Complete |
| CONN-01 | Phase 4 | Complete |
| CONN-02 | Phase 4 | Complete |
| CONN-03 | Phase 4 | Complete |
| INTR-01 | Phase 5 | Complete |
| INTR-02 | Phase 5 | Complete |
| INTR-03 | Phase 5 | Complete |
| POOL-01 | Phase 6 | Complete |
| POOL-02 | Phase 6 | Complete |
| ARCH-01 | Phase 7 | Pending |
| ARCH-02 | Phase 7 | Pending |
| ARCH-03 | Phase 7 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-18*
*Last updated: 2026-03-18 after roadmap expansion to 7 phases*
