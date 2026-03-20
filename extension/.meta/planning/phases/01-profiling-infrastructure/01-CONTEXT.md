# Phase 1: Profiling Infrastructure - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Add per-phase timing instrumentation to the graph rendering pipeline. Measure layout, renderNodes, buildConnections, computeOffsetPositions, setData, updateVisible, updateConnections with p50/p95 sliding window stats. Expose via console API.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GraphPixiRenderer.ts` (1688 lines) — main renderer with `setData()`, `updateVisible()`, `updateConnections()` methods
- `graph-layout-compute.ts` — layout computation functions
- `graph-utils.ts` — utility functions including `buildConnections`, `computeOffsetPositions`
- `quality-policy.ts` — LOD quality policy with existing render pipeline hooks

### Established Patterns
- Manual Pixi.js render calls (ticker stopped, explicit `app.renderer.render()`)
- React hooks + useMemo for data pipeline
- Per-node `NodeVisual` containers with ~12 display objects each

### Integration Points
- `GraphPixiRenderer.setData()` — monolithic entry point, primary instrumentation target
- `useGraphAnimation.ts` — RAF tick loop, high-frequency measurement point
- `GraphCanvas.tsx` — React component orchestrating layout → render pipeline
- `window.__graphMetrics()` — console API endpoint (to be created)

</code_context>

<specifics>
## Specific Ideas

No specific requirements — infrastructure phase.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
