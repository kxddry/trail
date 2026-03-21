# Phase 3: Bypass React for Animation - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Make `animateTick` update the renderer imperatively via ref, bypassing React state entirely during animation. `setAnimationVersion()` removed from animation RAF loop. React state updated only once when animation completes. Eliminates ~9 React re-renders per animation cycle.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase with approach prescribed by roadmap.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `useGraphAnimation.ts` — animation hook with `animateTick` RAF loop, currently calls `invalidateAnimation()` → `setAnimationVersion(v+1)` every tick
- `GraphPixiRenderer.ts` — now has `setDynamicState()` from Phase 2, can be called directly via ref
- `GraphCanvas.tsx` — has `rendererRef` to the PixiRenderer, `setDynamicState` useEffect
- `graph-profiler.ts` — Phase 1 profiler for measuring frame times

### Established Patterns
- `animatedPositionsRef` holds interpolated positions per-tick
- `renderNodes` useMemo depends on `animationVersion` to pick up animated positions
- `setDynamicState` effect depends on `renderNodes` — fires every time renderNodes changes
- Phase 2 split ensures `setStaticGraph` only fires on topology change

### Integration Points
- `animateTick` must call `renderer.setDynamicState()` directly via ref instead of triggering React
- `renderNodes` computation must be extractable to a non-React function for imperative use
- `animationVersion` state update moved to animation completion only
- Exit animation cleanup (nodeData reconciliation) must still work with imperative updates

</code_context>

<specifics>
## Specific Ideas

No specific requirements — infrastructure phase with prescribed approach.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
