---
phase: 04-graph-startup-optimization-without-blocking-first-paint
verified: 2026-03-19T08:45:00Z
status: passed
score: 6/6 must-haves verified
re_verification: false
---

# Phase 4: Graph Startup Optimization Verification Report

**Phase Goal:** Graph surfaces (sidepanel, fullview, Spotlight iframe) render the first static frame without waiting on non-critical bootstrap work, using an exact layout cache that is strict enough to trust at startup
**Verified:** 2026-03-19T08:45:00Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | PERF-01: Graph rendering does not wait on tag definitions, tree lists, command state, or platform shortcut metadata before first paint | VERIFIED | `useBootstrap.ts` lines 26-34: critical path awaits only `getSettings()` + `getTreeState()`, calls `bootstrapGraph(settings, treeState)`. Lines 53-76: tags, flags, trees, platform meta, command state are all deferred via independent `.then()/.catch()` chains inside `Promise.allSettled`. `bootstrapGraph` store action (store.ts lines 333-350) sets only settings, tree, pins, tabStates, nodeRecency, openNodeIds -- no metaKey, no isMac, no tagDefs, no commandState. |
| 2 | PERF-02: Layout cache includes a layoutSignature and only serves cached positions when the signature matches current boot state | VERIFIED | `types.ts` line 32: `readonly layoutSignature: string` on CachedLayoutResult. `computeLayoutSignature()` (lines 77-88) produces deterministic pipe-delimited string from mode, density, gap scales, radial params, collapse state, recency. `cache.ts` lines 38-49: `readLayoutCache` with signature tries exact key first, then base key with `baseEntry.layoutSignature === layoutSignature` validation -- rejects on mismatch. 6 passing tests in `tests/layout-signature.test.ts`. |
| 3 | PERF-03: Changing layout settings and reopening the graph uses positions from a fresh cache, not stale ones | VERIFIED | `offscreen-graph/main.ts` lines 86-93: `SAVE_SETTINGS` handler refetches settings then immediately calls `computeAndCache(cachedTreeJSON)` with the new settings. `compute-layout.ts` lines 73-81: `computeLayoutSignature` is computed fresh from current settings and included in the result. `cache.ts` lines 25-28: `writeLayoutCache` writes to both exact signature key and base fallback key. On next open, `readLayoutCache` with current signature will match the newly-computed entry or reject the stale one. |
| 4 | PERF-04: Tag dots appear after first paint once tag definitions load, without causing a layout recompute or view reset | VERIFIED | `useBootstrap.ts` line 58: `getTagDefs()` is in the deferred section, called after `bootstrapGraph` completes. `store.ts` `setTagDefs` (lines 441-454) only updates `tagDefs` and `tagDefsList` state slices. `GraphCanvas.tsx` layout `useMemo` dependency array (lines 558-569) does NOT include `tagDefs` -- it depends on `baseLayoutConfig, getVisibleChildren, layoutOptions.mode, layoutOptions.mindmap, layoutOptions.radial, layoutOptions.tree, root, settings, sortChildrenForParentKey, subtreeScores`. tagDefs is used only in rendering (line 1521 in render model creation), not in layout computation. |
| 5 | PERF-05: Startup instrumentation records critical bootstrap duration, cache hit/miss type, and time to first PIXI render | VERIFIED | `graph-profiler.ts`: `STARTUP_T0` captured at module load (line 17). `StartupMetrics` type (lines 32-45) has `bootstrapMs`, `firstRenderMs`, `layoutMs`, `cacheHitType`, `nodeCount`, `layoutMode`. `recordStartup()` method (lines 121-124). `getStartupMetrics()` (lines 126-128). `window.__graphMetrics()` (lines 154-184) prints both per-phase stats table and startup metrics table. `GraphCanvas.tsx`: bootstrap timing recorded at line 442, cache hit type at lines 466/481/490/554, layout timing at lines 467/482/550, first render at line 577 via `requestAnimationFrame`. |
| 6 | PERF-06: If any critical pre-mount fetch fails, the surface falls back to mount-then-fetch behavior without blocking or crashing | VERIFIED | `useBootstrap.ts` lines 42-47: critical path wrapped in try/catch, logs error and returns early on failure. Comment confirms "Surface already mounted React tree -- it will show loading state until TREE_UPDATED arrives from background." Each deferred fetch has independent `.catch()` (lines 56-74) so one failure does not block others. Pre-mount cache fetch in all entrypoints (`main.tsx` files) uses `readLayoutCache('active')` which returns `null` on failure (cache.ts line 36: `if (!storage) return null`). |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `extension/src/shared/graph-layout-cache/types.ts` | layoutSignature field, computeLayoutSignature function | VERIFIED | 89 lines. `layoutSignature: string` on line 32. `LayoutSignatureParams` type lines 54-69. `computeLayoutSignature()` lines 77-88. `computeCollapseSignature()` lines 44-48. |
| `extension/src/shared/graph-layout-cache/cache.ts` | Signature-aware readLayoutCache/writeLayoutCache | VERIFIED | 63 lines. `storageKey()` lines 9-14 supports signature suffix. `writeLayoutCache` lines 20-29 writes to both exact+base keys. `readLayoutCache` lines 31-56 validates signature on fallback. |
| `extension/src/shared/graph-layout-cache/compute-layout.ts` | Produces layoutSignature from settings | VERIFIED | 96 lines. Imports `computeLayoutSignature` (line 14). Calls it at lines 73-81. Includes `layoutSignature` in returned `CachedLayoutResult` at line 93. |
| `extension/src/entrypoints/sidepanel/ui/state/store.ts` | bootstrapGraph + setPlatformMeta actions | VERIFIED | `bootstrapGraph` action lines 333-350 (settings+tree only, no metaKey/isMac). `setPlatformMeta` action line 352. Both declared in StoreActions type at lines 152-153. |
| `extension/src/entrypoints/sidepanel/ui/hooks/useBootstrap.ts` | Split critical + deferred phases | VERIFIED | 82 lines. Critical path lines 27-47 (settings+tree). Deferred path lines 53-76 (flags, tags, trees, platform, commands). Independent `.catch()` on each deferred fetch. |
| `extension/src/ui-core/panel/bootstrap.tsx` | Pre-mount cache fetch, __trailCachedLayout global | VERIFIED | 49 lines. `declare global { var __trailCachedLayout }` lines 11-14. `cachedLayout` option lines 18-19. Stashes on `globalThis.__trailCachedLayout` at line 31. |
| `extension/src/entrypoints/sidepanel/ui/main.tsx` | Pre-mount readLayoutCache | VERIFIED | 14 lines. `readLayoutCache('active')` at line 6 before mount. `await cachePromise` at line 9 before `mountPanelApp`. |
| `extension/src/entrypoints/fullview/ui/main.tsx` | Pre-mount readLayoutCache | VERIFIED | 14 lines. Same pattern as sidepanel. `readLayoutCache('active')` at line 6, awaited before `mountPanelApp`. |
| `extension/src/entrypoints/spotlight-graph/main.tsx` | Pre-mount readLayoutCache | VERIFIED | 28 lines. `readLayoutCache('active')` at line 11. `globalThis.__trailCachedLayout = cached` at line 15 before `createRoot`. |
| `extension/src/entrypoints/offscreen-graph/main.ts` | SAVE_SETTINGS recomputation handler | VERIFIED | 121 lines. `SAVE_SETTINGS` handler lines 86-93. Calls `fetchSettings()` then `computeAndCache(cachedTreeJSON)`. `cachedTreeJSON` stored at line 80 from `TREE_UPDATED`. |
| `extension/src/entrypoints/sidepanel/ui/graph/render/graph-profiler.ts` | recordStartup, getStartupMetrics, STARTUP_T0 | VERIFIED | 185 lines. `STARTUP_T0 = performance.now()` line 17. `StartupMetrics` type lines 32-45. `recordStartup()` line 121. `getStartupMetrics()` line 126. Console API at line 154. |
| `extension/src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx` | Signature-validated cache hydration, timing marks | VERIFIED | `consumePrefetchedLayout()` lines 65-69. Signature comparison at line 462: `cachedSig && cachedSig === currentSignature`. Fallback for old format lines 474-487. Bootstrap timing line 442. First render timing line 577. |
| `extension/tests/layout-signature.test.ts` | Tests for signature determinism | VERIFIED | 186 lines. 6 tests covering determinism, mode differentiation, density differentiation, collapse signature differentiation, recency ordering differentiation, and format validation. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| compute-layout.ts | types.ts | imports computeLayoutSignature | WIRED | Line 14: `import { computeCollapseSignature, computeLayoutSignature } from './types.js'` |
| cache.ts | types.ts | reads layoutSignature from CachedLayoutResult | WIRED | Line 1: `import type { CachedLayoutResult } from './types.js'`. Line 47: `baseEntry.layoutSignature === layoutSignature` |
| offscreen-graph/main.ts | compute-layout.ts | calls computeLayoutFromTree on settings change | WIRED | Line 10: `import { computeLayoutFromTree }`. Lines 87-91: `fetchSettings()` then `computeAndCache(cachedTreeJSON)` which calls `computeLayoutFromTree` at line 51 |
| useBootstrap.ts | store.ts | calls bootstrapGraph with settings+tree only | WIRED | Line 13: `useStore((state) => state.bootstrapGraph)`. Line 34: `bootstrapGraph(settings, treeState)` |
| bootstrap.tsx | cache.ts | accepts cachedLayout for global stash | WIRED | bootstrap.tsx does not import cache.ts directly (by design), but receives `cachedLayout` param (line 19) and stashes it (line 31). Entrypoints import readLayoutCache and pass result. |
| sidepanel/main.tsx | cache.ts | pre-mount cache read | WIRED | Line 3: `import { readLayoutCache }`. Line 6: `readLayoutCache('active')` |
| fullview/main.tsx | cache.ts | pre-mount cache read | WIRED | Line 3: `import { readLayoutCache }`. Line 6: `readLayoutCache('active')` |
| spotlight-graph/main.tsx | cache.ts | pre-mount cache read | WIRED | Line 7: `import { readLayoutCache }`. Line 11: `readLayoutCache('active')` |
| GraphCanvas.tsx | graph-profiler.ts | calls recordStartup with timing data | WIRED | Line 34: `import { graphProfiler, profileSync, STARTUP_T0 }`. Lines 442, 466-469, 481-484, 490, 550-554, 577: multiple `graphProfiler.recordStartup()` calls |
| GraphCanvas.tsx | types.ts | reads layoutSignature for validation | WIRED | Line 54: `import { computeCollapseSignature, computeLayoutSignature }`. Line 461: `_prefetchedLayout.layoutSignature`. Line 462: `cachedSig === currentSignature` |
| useBootstrap.ts | tags API | deferred fetch after first paint | WIRED | Line 5: `import { getTagDefs }`. Line 57: `getTagDefs()` in deferred section (after bootstrapGraph completes) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|-----------|-------------|--------|----------|
| PERF-01 | 04-02 | Graph rendering does not wait on tag definitions, tree lists, command state, or platform shortcut metadata before first paint | SATISFIED | useBootstrap critical path: settings+tree only. Tags/flags/trees/platform/commands deferred. |
| PERF-02 | 04-01 | Layout cache includes a layoutSignature and only serves cached positions when the signature matches current boot state | SATISFIED | layoutSignature field on CachedLayoutResult, computeLayoutSignature function, signature-validated readLayoutCache |
| PERF-03 | 04-01 | Changing layout settings and reopening the graph uses positions from a fresh cache, not stale ones | SATISFIED | Offscreen worker SAVE_SETTINGS recomputation, dual-key cache write, signature validation on read |
| PERF-04 | 04-02 | Tag dots appear after first paint once tag definitions load, without causing a layout recompute or view reset | SATISFIED | tagDefs deferred in useBootstrap, NOT in layout useMemo deps, only used in render model |
| PERF-05 | 04-03 | Startup instrumentation records critical bootstrap duration, cache hit/miss type, and time to first PIXI render | SATISFIED | STARTUP_T0, bootstrapMs, cacheHitType, firstRenderMs, layoutMs, nodeCount, layoutMode all recorded. window.__graphMetrics() console API. |
| PERF-06 | 04-02 | If any critical pre-mount fetch fails, the surface falls back to mount-then-fetch behavior without blocking or crashing | SATISFIED | try/catch around critical path in useBootstrap, early return on failure, independent .catch() on each deferred fetch |

**Note:** PERF-01 through PERF-06 are not yet tracked in REQUIREMENTS.md (the traceability table only covers phases 1-3). This is an informational gap in documentation, not a code gap.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| None | - | - | - | No anti-patterns found in phase 04 files |

No TODOs, FIXMEs, placeholders, or empty implementations found in any of the 13 files modified/created in this phase.

### Human Verification Required

### 1. Cache Hit/Miss Correctness at Runtime

**Test:** Open sidepanel, wait for graph to render. Run `window.__graphMetrics()` in DevTools console. Check that `Cache Hit` shows `exact` (not `stale` or `miss`). Close sidepanel, change layout settings (e.g., switch from tree to radial mode), reopen sidepanel, run `__graphMetrics()` again.
**Expected:** First open shows `exact` cache hit. After settings change, the offscreen worker should have recomputed, so the reopened sidepanel should also show `exact` (not `stale`). If opened before recomputation completes, `miss` is acceptable.
**Why human:** Requires runtime chrome.storage.session interaction and real-time timing that cannot be verified statically.

### 2. Tag Dots Appear Without Layout Jump

**Test:** Open sidepanel with tags assigned to nodes. Watch the graph during initial load.
**Expected:** Graph renders first with node positions, then tag dots fade in without any visible layout shift or view reset.
**Why human:** Visual behavior -- layout recompute avoidance can only be confirmed by observing no jump/shift.

### 3. Fallback on Network Failure

**Test:** Open Chrome DevTools Network tab, throttle to Offline, then open the sidepanel.
**Expected:** Sidepanel mounts without crashing. Shows loading state. When network resumes, TREE_UPDATED from background should populate the graph.
**Why human:** Requires simulating network failure conditions in a Chrome extension context.

### 4. All Three Surfaces Work

**Test:** Open sidepanel, fullview (via extension popup), and Spotlight iframe. Verify each renders the graph.
**Expected:** All three surfaces show the graph without delay from deferred fetches. Each should have pre-fetched the layout cache.
**Why human:** Requires opening multiple Chrome extension surfaces.

### Gaps Summary

No gaps found. All 6 success criteria are satisfied with complete implementations. Every artifact exists, is substantive (no stubs), and is properly wired into the call chain. The phase achieves its goal: graph surfaces render the first static frame without waiting on non-critical bootstrap work, using a signature-validated layout cache.

The only documentation gap is that PERF-01 through PERF-06 requirements are not yet added to the REQUIREMENTS.md traceability table, but this does not affect functionality.

---

_Verified: 2026-03-19T08:45:00Z_
_Verifier: Claude (gsd-verifier)_
