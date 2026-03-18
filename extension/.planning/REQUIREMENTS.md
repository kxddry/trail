# Requirements: Trail Graph Performance

**Defined:** 2026-03-18
**Core Value:** Graph must feel instant and responsive at any tree size

## v1 Requirements

### Render Cycle

- [ ] **RCYC-01**: Animation ticks update renderer imperatively without triggering React re-render
- [ ] **RCYC-02**: `setData()` split into `setStaticGraph()` (topology), `setDynamicState()` (positions/hover/search), `setParticles()`
- [ ] **RCYC-03**: SpatialIndex is only rebuilt on topology change, not on every animation frame
- [ ] **RCYC-04**: Profiling instrumentation reports p50/p95 per phase: layout, renderNodes, buildConnections, setData, updateVisible

### Connection Caching

- [ ] **CONN-01**: ConnectionSegment[] cached by topology/layout signature, not rebuilt per frame
- [ ] **CONN-02**: Path highlight and preview edge updated separately from base connections
- [ ] **CONN-03**: Connection layer uses dirty flags instead of full clear+redraw on every updateVisible

### Interaction Performance

- [ ] **INTR-01**: Drag/reparent nearest-parent lookup uses SpatialIndex query instead of linear positionsRef scan
- [ ] **INTR-02**: `computeOffsetPositions()` only recalculates dragged subtree and affected ancestors during drag
- [ ] **INTR-03**: Selection preview and hover updates bypass full renderNodes rebuild

### State Architecture

- [ ] **ARCH-01**: Static graph snapshot (topology, base positions, base connections) separated from ephemeral UI state (view, selection, hover, search, animations)
- [ ] **ARCH-02**: GraphSnapshot type introduced: nodes/base rects, connections/base geometry, layoutMode, version
- [ ] **ARCH-03**: Offscreen layout cache key includes collapse state and recency ordering signature

### Object Lifecycle

- [ ] **POOL-01**: Particle Graphics objects pooled instead of created/destroyed per frame
- [ ] **POOL-02**: Tag dot Graphics objects pooled in NodeVisual instead of removeChildren+new per update

## v2 Requirements

### Deep Rendering

- **REND-01**: BitmapText or MSDF text instead of PIXI.Text for node labels
- **REND-02**: Instanced rendering for dot-LOD nodes (single draw call)
- **REND-03**: Custom WebGL shader for node backgrounds (instanced)

### Architecture

- **SCEN-01**: GraphSceneController — React sends commands, scene lives imperatively on PIXI
- **SCEN-02**: Worker pipeline for layout, edge generation, nearest-node queries
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
| RCYC-01 | Phase 1 | Pending |
| RCYC-02 | Phase 1 | Pending |
| RCYC-03 | Phase 1 | Pending |
| RCYC-04 | Phase 1 | Pending |
| CONN-01 | Phase 2 | Pending |
| CONN-02 | Phase 2 | Pending |
| CONN-03 | Phase 2 | Pending |
| INTR-01 | Phase 2 | Pending |
| INTR-02 | Phase 2 | Pending |
| INTR-03 | Phase 2 | Pending |
| ARCH-01 | Phase 3 | Pending |
| ARCH-02 | Phase 3 | Pending |
| ARCH-03 | Phase 3 | Pending |
| POOL-01 | Phase 2 | Pending |
| POOL-02 | Phase 2 | Pending |

**Coverage:**
- v1 requirements: 15 total
- Mapped to phases: 15
- Unmapped: 0 ✓

---
*Requirements defined: 2026-03-18*
*Last updated: 2026-03-18 after initial definition*
