# Phase 2: Split Renderer API - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace monolithic `setData()` in GraphPixiRenderer with granular API: `setStaticGraph()` for topology + basePositions (rebuilds SpatialIndex), `setDynamicState()` for ephemeral updates (positionOverrides, openProgress, hover, search), `setParticles()` for animations. GraphCanvas updated to call the correct method based on what changed.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase with API design prescribed by roadmap.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GraphPixiRenderer.ts` (1688 lines) — contains current monolithic `setData()` method that rebuilds everything
- `GraphCanvas.tsx` (~1700 lines) — React component that calls `renderer.setData()` on every state change
- `graph-profiler.ts` — Phase 1 profiler, instrumentation points will need updating after API split
- `spatial-index.ts` — SpatialIndex class, currently rebuilt on every `setData()` call

### Established Patterns
- `RenderData` type defines current `setData()` input shape (nodes, connections, layoutMode, etc.)
- Manual Pixi.js render calls (ticker stopped)
- React useMemo chain computes renderNodes → connectionPositions → baseConnections

### Integration Points
- `GraphCanvas.tsx` must be updated to call `setStaticGraph()` only on layout/topology change
- `setDynamicState()` for animation ticks, hover, selection changes
- `setParticles()` for particle animations
- Profiler instrumentation needs updating for new methods

</code_context>

<specifics>
## Specific Ideas

No specific requirements — infrastructure phase with prescribed API.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
