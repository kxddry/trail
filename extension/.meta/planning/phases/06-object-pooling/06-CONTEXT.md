# Phase 6: Object Pooling - Context

**Gathered:** 2026-03-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Pool frequently created/destroyed PIXI Graphics objects to eliminate GC pressure during animations. Particle Graphics from pre-allocated pool (size 32). Tag dot Graphics pooled per node (max 4). No GC spikes during 5-minute interaction session.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure phase with approach prescribed by roadmap.

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GraphPixiRenderer.ts` — `updateParticles()` method currently calls `removeChildren()` + `child.destroy()` per frame
- `NodeVisual` class — `updateTags()` calls `removeChildren()` + `new PIXI.Graphics()` per update
- Phase 1 profiler for measuring GC impact

### Established Patterns
- Pixi.js Graphics objects with manual render calls
- `particleLayer` container holds particle visuals
- NodeVisual has tag dot container with per-node Graphics

### Integration Points
- Particle pool integrated into `updateParticles()` — draw from pool, return on animation end
- Tag dot pool per NodeVisual — reuse Graphics across `updateTags()` calls
- Pool lifecycle tied to renderer lifecycle (create on init, clear on destroy)

</code_context>

<specifics>
## Specific Ideas

No specific requirements — infrastructure phase with prescribed approach.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>
