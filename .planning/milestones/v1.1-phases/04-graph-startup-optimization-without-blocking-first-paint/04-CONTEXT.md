# Phase 4: Graph Startup Optimization Without Blocking First Paint - Context

**Gathered:** 2026-03-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Optimize graph startup across sidepanel, fullview, and Spotlight iframe surfaces so the first static frame renders without waiting on non-critical bootstrap work. Make the layout cache strict enough (via layoutSignature) to trust at startup. Add startup instrumentation. No changes to graph fidelity, LOD, or interaction — only the bootstrap/render critical path.

</domain>

<decisions>
## Implementation Decisions

### Claude's Discretion
All implementation choices are at Claude's discretion — pure infrastructure/performance phase. The user provided a detailed spec covering:

- Bootstrap split (critical vs deferred)
- Pre-mount store priming
- Store API changes (bootstrap → bootstrapGraph + setPlatformMeta)
- Layout cache signature derivation and validation
- Settings-change cache recomputation in offscreen worker
- Renderer startup fast-path (skip redundant setDynamicState)
- Deferred tag definitions handling
- Startup instrumentation metrics

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `bootstrap()` action in `sidepanel/ui/state/store.ts` — current single bootstrap action to split
- `useBootstrap()` hook in `sidepanel/ui/hooks/useBootstrap.ts` — current all-in-one hook to replace with deferred variant
- `readLayoutCache()` / `writeLayoutCache()` in `shared/graph-layout-cache/cache.ts` — session storage cache helpers to extend with signature
- `CachedLayoutResult` type in `shared/graph-layout-cache/types.ts` — to extend with layoutSignature
- `computeLayoutFromTree()` in `shared/graph-layout-cache/compute-layout.ts` — offscreen layout computation
- `deriveLayoutOptions()` in `sidepanel/ui/graph/layout/options.ts` — layout config derivation from Settings (source of signature inputs)
- `graphProfiler` in `sidepanel/ui/graph/render/graph-profiler.ts` — existing instrumentation to extend with startup metrics
- `computeCollapseSignature()` in `shared/graph-layout-cache/types.ts` — already computes collapse state hash

### Established Patterns
- Zustand store with action methods for state management
- `globalThis.__trailCachedLayout` pattern already used by Spotlight graph entrypoint for pre-mount cache stash
- Offscreen document pattern for background layout computation via message passing
- `mountPanelApp()` in `ui-core/panel/bootstrap.tsx` for shared panel mounting across sidepanel/fullview
- Chrome session storage for layout cache persistence

### Integration Points
- `sidepanel/main.tsx` and `fullview/ui/main.tsx` — entrypoints that call `mountPanelApp()`
- `spotlight-graph/main.tsx` — already does pre-mount cache prefetch
- `offscreen-graph/main.ts` — listens for TREE_UPDATED, computes layout, writes cache
- `GraphCanvas.tsx` (71KB) — consumes `globalThis.__trailCachedLayout` for hydration
- `GraphPixiRenderer.ts` — main renderer, target for startup fast-path
- `graph-snapshot.ts` — immutable state snapshot for diffing (relevant to skip-redundant-update logic)

</code_context>

<specifics>
## Specific Ideas

User provided a complete implementation spec including:
- Exact list of critical vs deferred fetches
- Store API contract changes
- layoutSignature composition (layout mode, node dims, gaps, radial params, density, recencyOrdering, collapseSignature)
- Cache key strategy (exact-key first, fallback with field matching)
- Offscreen worker settings-change recomputation trigger
- GraphCanvas/GraphPixiRenderer startup fast-path criteria
- Tag defs deferred rendering behavior (empty → patch, no relayout)
- Instrumentation metrics list (6 timing points)

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>
