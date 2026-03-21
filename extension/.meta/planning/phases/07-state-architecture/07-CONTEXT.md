# Phase 7: State Architecture - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Formalize static/ephemeral separation with GraphSnapshot type (node rects + basePositions, connection geometry, layoutMode, version number). Static snapshot created on layout change, immutable until next layout change. Ephemeral state (view, selection, hover, search, animation offsets) updates without touching snapshot. Offscreen layout cache key includes layout mode + collapse state hash + recency ordering signature. Cache hit rate measurable — warm opens reuse cached layout in >90% of cases. Expand/collapse triggers incremental snapshot update (affected subtree only), not full rebuild.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase with approach prescribed by roadmap.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GraphPixiRenderer.ts` — already has `StaticGraphData` and `DynamicGraphState` types from Phase 2
- `GraphCanvas.tsx` — `staticVersion` ref counter from Phase 2 tracks topology changes
- `graph-layout-compute.ts` — offscreen layout computation via Chrome offscreen document
- Phase 2 split API (`setStaticGraph` / `setDynamicState` / `setParticles`)

### Established Patterns
- `StaticGraphData` type: nodes, connections, layoutMode, nodeWidth, nodeHeight, showConnections
- `staticVersion` useMemo increments on basePositions/layoutMode/nodeWidth/nodeHeight change
- Offscreen layout uses `calculateLayout()` via message passing to offscreen document
- `cachedBaseConnectionsRef` from Phase 4 caches connection geometry by staticVersion

### Integration Points
- `GraphSnapshot` type formalizes what Phase 2 already partially captures in `StaticGraphData`
- Offscreen layout cache key needs enriching with collapse state + recency signature
- Incremental snapshot update on expand/collapse aligns with existing `setStaticGraph` call pattern
- Phase 1 profiler can measure cache hit rates

</code_context>

<specifics>
## Specific Ideas

No specific requirements — infrastructure phase with prescribed approach.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
