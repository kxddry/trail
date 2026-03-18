# Phase 5: Interaction Optimization - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Replace linear position scanning in drag/reparent with spatial queries. Selection and hover updates bypass full renderNodes rebuild. Add `queryNearest()` to SpatialIndex. Drag reparent preview maintains <16ms frame time on 2000-node tree.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase with approach prescribed by roadmap.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `spatial-index.ts` — SpatialIndex class with `query()`, `insert()`, `update()`, `remove()` methods (grid-based)
- `GraphPixiRenderer.ts` — has `hitTestWorld()` and `hitTestScreen()` using spatial index queries
- `GraphCanvas.tsx` — drag handler with linear position scanning for nearest parent
- Phase 2 `setDynamicState()` with incremental spatial index updates

### Established Patterns
- Grid-based spatial index with cell-based bucketing
- `hitTestWorld()` queries index then checks nodeData for precise AABB bounds
- Drag reparent uses `computeOffsetPositions()` for dragged subtree positioning

### Integration Points
- `queryNearest()` method needed on SpatialIndex for drag nearest-parent detection
- Drag handler should use `queryNearest()` instead of linear scan
- `computeOffsetPositions()` during drag should only recalculate dragged subtree + ancestors
- Hover/selection changes should call `setDynamicState()` targeting only affected nodes

</code_context>

<specifics>
## Specific Ideas

No specific requirements — infrastructure phase with prescribed approach.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
