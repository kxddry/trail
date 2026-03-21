# Phase 7: Performance Budgets - Context

**Gathered:** 2026-03-21
**Status:** Ready for planning

<domain>
## Phase Boundary

Extension has measurable, enforced performance targets and degrades gracefully on constrained devices. Covers: budget metrics, adaptive degradation, search caching, virtualization, skeleton loading.

</domain>

<decisions>
## Implementation Decisions

### Performance Budget Metrics (PERF-01)
- Add sidepanel bootstrap timing to GraphProfiler: `sidepanelBootstrapMs` (useBootstrap start → ready)
- Add spotlight query latency to existing profiler: `spotlightQueryMs` per search call
- Track 3 budget numbers: first sidepanel paint (<500ms target), first graph interactive (<1000ms), spotlight query (<100ms)
- Use `performance.mark()`/`performance.measure()` for browser devtools integration
- Budget breach: log warning via structured logger, no user-visible impact (metrics only for v1.2)

### Adaptive Degradation (PERF-02)
- Enable `adaptivePerformance` flag by default (currently false)
- Set `LOD_HIDE_PX = 4` and `LOD_CONN_HIDE_PX = 6` to enable hiding at extreme zoom-out
- Add node-count threshold: trees >500 nodes start at "low" quality, >2000 start at "dot"
- Existing EWMA quality-policy handles frame-time degradation — just needs the flag on

### Search Index Caching (PERF-03)
- Add `requestIdleCallback` pre-warming for spotlight index on sidepanel open
- Cap archive load in rebuild() — limit to most recent 10 archives, lazy-load rest on demand
- In-graph MiniSearch is already sync and always ready — no changes needed

### Virtualization (PERF-04)
- Add `@tanstack/react-virtual` to SearchResultsList (sidepanel search — unbounded results)
- Already installed as dependency (used by SpotlightResults)
- TreeDropdown archived list: low risk, skip virtualization (typically <50 items)
- TagFilterDropdown filteredNodes: skip for now — tag count is user-bounded

### Skeleton Loading (PERF-05)
- Add skeleton shimmer for bootstrap loading state in App.tsx — replace blank screen
- Skeleton layout: header bar + graph area placeholder (gray rectangle with pulse animation)
- Replace `<Suspense fallback={null}>` on GraphCanvas with skeleton placeholder
- Keep it simple: CSS-only pulse animation, no external skeleton library

### Claude's Discretion
- Exact skeleton visual design (pulse vs shimmer vs gradient)
- Precise LOD threshold values (can be tuned later)
- Whether to add `requestIdleCallback` polyfill for older browsers (probably not needed for Chrome extension)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `GraphProfiler` class with p50/p95 circular buffer, startup metrics, console API
- `quality-policy.ts` with EWMA frame-time scorer and transition thresholds
- `adaptivePerformance` flag in flags system
- `@tanstack/react-virtual` already installed (used by SpotlightResults)
- `STARTUP_T0 = performance.now()` at module load

### Key Files
- `graph-profiler.ts` — metrics collection
- `quality-policy.ts` — degradation policy
- `GraphPixiRenderer.ts` — LOD levels and thresholds
- `spotlight-live-index.ts` — search index build
- `SearchResultsList.tsx` — unvirtualized results list
- `App.tsx` — bootstrap loading state (currently blank)
- `GraphArea.tsx` — Suspense fallback={null}

</code_context>

<deferred>
## Deferred Ideas

None

</deferred>
