# Phase 4: Connection Caching - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Cache connection geometry by topology/layout signature. Path highlight (root→current) updated by toggling `onPath` flag on existing segments, not rebuilding all. Preview edge (drag reparent) added/removed without regenerating base connections. Dirty flag skips clear+redraw when connections unchanged. Target: >80% reduction in connection rendering time during animation.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase with approach prescribed by roadmap.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GraphPixiRenderer.ts` — has `updateConnections()` method that currently rebuilds all connection graphics every call
- `GraphCanvas.tsx` — computes `baseConnections` and `connectionPositions` via useMemo chain
- `graph-utils.ts` — `buildConnections()` function generates `ConnectionSegment[]`
- `graph-profiler.ts` — profiling for `updateConnections` already instrumented

### Established Patterns
- `ConnectionSegment` type with `fromId`, `toId`, `onPath`, `isPreview` fields
- `setStaticGraph` / `setDynamicState` split from Phase 2
- Imperative animation path from Phase 3

### Integration Points
- Connection cache should be invalidated by `setStaticGraph` (topology change)
- `setDynamicState` should only update path highlight and preview edge, not regenerate base connections
- `updateConnections` dirty flag prevents unnecessary clear+redraw during animation ticks
- Imperative tick render path needs to handle connections efficiently

</code_context>

<specifics>
## Specific Ideas

No specific requirements — infrastructure phase with prescribed approach.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
