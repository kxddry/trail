---
phase: 04-connection-caching
verified: 2026-03-19T12:00:00Z
status: passed
score: 7/7 must-haves verified
re_verification:
  previous_status: passed
  previous_score: 7/7
  gaps_closed: []
  gaps_remaining: []
  regressions: []
note: >
  User requested verification with goal "Graph surfaces render first static frame
  without waiting on non-critical bootstrap work" and requirements PERF-01 through PERF-06.
  These do NOT match the actual Phase 04 in this codebase. The actual Phase 04 is
  "Connection Caching" with requirements CONN-01, CONN-02, CONN-03. PERF-01 through
  PERF-06 do not exist in REQUIREMENTS.md. This report verifies the ACTUAL Phase 04
  as defined in ROADMAP.md.
---

# Phase 4: Connection Caching Verification Report

**Phase Goal:** Cache connection geometry by topology/layout signature. Path highlight and preview edge updated independently from base connections.
**Verified:** 2026-03-19T12:00:00Z
**Status:** passed
**Re-verification:** Yes -- re-verification of previously-passed phase (no gaps to close)

**IMPORTANT NOTE:** The verification request specified a different phase goal ("Graph surfaces render first static frame without waiting on non-critical bootstrap work") and requirement IDs (PERF-01 through PERF-06) that do not exist anywhere in this project's ROADMAP.md or REQUIREMENTS.md. This report verifies the actual Phase 04 ("Connection Caching", CONN-01/CONN-02/CONN-03) as defined in the project planning artifacts.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | baseConnections are only recalculated when topology/layout changes (staticVersion increments), not on every animation frame | VERIFIED | `baseConnections` useMemo at GraphCanvas.tsx:1415-1432 depends on `[staticVersion, effectiveShowConnections]` only. `buildConnections` appears only at line 1418 (inside this useMemo) and line 30 (import). No call in imperative tick path. |
| 2 | Path highlight (root->current) toggles onPath flag on cached segments without calling buildConnections | VERIFIED | `applyPathHighlight` at graph-utils.ts:49-61 takes cached base connections and returns new array with toggled `onPath` flags. Used in `connections` useMemo at GraphCanvas.tsx:1455 and imperative path at line 318. No `buildConnections` call in either path. |
| 3 | Preview edge (drag reparent) is layered on top of cached base connections without regenerating them | VERIFIED | `connections` useMemo at GraphCanvas.tsx:1454-1484+ applies `applyPathHighlight(baseConnections, pathNodeIds)` first, then conditionally appends preview edge via `dragReparentTarget` logic. `baseConnections` is not recalculated. |
| 4 | Imperative tick render path reuses cached base connections instead of calling buildConnections per tick | VERIFIED | `handleTickRenderRef.current` at GraphCanvas.tsx:266-336 reads `cachedBaseConnectionsRef.current` (line 318) and applies `applyPathHighlight`. No `buildConnections` call. `connPositions` Map construction completely absent from the file (grep confirms zero occurrences). |
| 5 | updateConnections skips clear+redraw when connections array reference has not changed since last call | VERIFIED | GraphPixiRenderer.ts:1554 checks `!this.connectionsDirty && viewUnchanged` and returns early. `connectionsDirty` only set true when `this.connections !== state.connections` in `setDynamicState` (line 1288-1290), or on topology/quality/theme/invalidateAll changes. |
| 6 | updateConnections still redraws when view changes cause different connections to enter/exit viewport | VERIFIED | `lastConnectionViewRect` at GraphPixiRenderer.ts:1548-1552 does strict equality comparison on minX/minY/maxX/maxY. When viewport changes, `viewUnchanged` is false, triggering full redraw at lines 1560-1563. |
| 7 | Connection rendering time drops by >80% during animation (no clear+redraw on every updateVisible) | VERIFIED (structural) | During animation: connections array reference is stable (cached base + same pathNodeIds), viewport is stable (no pan during animation), so `updateConnections` hits the early return at line 1554-1556 every tick. Only particle update runs (lines 1523-1524). The clear+draw loop (lines 1560+) is entirely skipped. |

**Score:** 7/7 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx` | Connection cache keyed to staticVersion, path overlay, preview overlay | VERIFIED | `cachedBaseConnectionsRef` at line 207, `baseConnections` useMemo at line 1415 keyed to `staticVersion`, `connections` useMemo at line 1454 applies path + preview overlay |
| `src/entrypoints/sidepanel/ui/components/graph/graph-utils.ts` | applyPathHighlight helper function | VERIFIED | Exported at line 49. Takes `baseConnections` and `pathNodeIds`, returns new array with toggled `onPath` flags. Reuses unchanged segment objects (line 57-59). |
| `src/entrypoints/sidepanel/ui/graph/render/GraphPixiRenderer.ts` | Dirty flag for connection rendering, view-rect-aware skip logic | VERIFIED | `connectionsDirty` field at line 806, `lastConnectionViewRect` at line 807. Skip logic in `updateConnections` at lines 1547-1556. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| GraphCanvas.tsx baseConnections useMemo | staticVersion | dependency array uses staticVersion instead of connectionPositions | WIRED | Line 1431: `[staticVersion, effectiveShowConnections]` |
| GraphCanvas.tsx connections useMemo | cachedBaseConnectionsRef | path toggle + preview append on cached segments | WIRED | Line 1455: `applyPathHighlight(baseConnections, pathNodeIds)` then preview edge logic |
| handleTickRenderRef (imperative path) | cachedBaseConnectionsRef | reads cached connections instead of calling buildConnections | WIRED | Line 318: `applyPathHighlight(cachedBaseConnectionsRef.current, s.pathNodeIds)` |
| setDynamicState | connectionsDirty | compares incoming connections reference with stored reference | WIRED | Line 1288: `if (this.connections !== state.connections)` then sets dirty at 1290 |
| setStaticGraph | connectionsDirty | always marks dirty on topology change | WIRED | Line 1173: `this.connectionsDirty = true` |
| updateConnections | connectionsDirty | skips clear+redraw when not dirty and viewport unchanged | WIRED | Line 1554: `if (!this.connectionsDirty && viewUnchanged)` returns early |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|----------|
| CONN-01 | 04-01 | ConnectionSegment[] cached by topology/layout signature, not rebuilt per frame | SATISFIED | `baseConnections` useMemo keyed to `staticVersion`, `cachedBaseConnectionsRef` stores result |
| CONN-02 | 04-01 | Path highlight and preview edge updated separately from base connections | SATISFIED | `applyPathHighlight` for path toggle, preview edge layered in separate `connections` useMemo |
| CONN-03 | 04-02 | Connection layer uses dirty flags instead of full clear+redraw on every updateVisible | SATISFIED | `connectionsDirty` + `lastConnectionViewRect` in GraphPixiRenderer, skip logic in `updateConnections` |

No orphaned requirements. REQUIREMENTS.md maps CONN-01, CONN-02, CONN-03 to Phase 4 (lines 69-71). All three are claimed in plan frontmatters (04-01 claims CONN-01/CONN-02, 04-02 claims CONN-03) and verified above.

**Note on PERF-01 through PERF-06:** The verification request referenced these requirement IDs, but they do not exist in REQUIREMENTS.md. No phase in the roadmap claims them. They appear to belong to a different project or a planned-but-not-yet-created phase.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| (none) | - | - | - | - |

No TODOs, FIXMEs, placeholders, empty implementations, or stub patterns found in any modified file. TypeScript compiles cleanly (exit code 0, zero errors).

### Commit Verification

| Commit | Message | Status |
|--------|---------|--------|
| e9ce0d2d | feat(04-01): cache base connections by staticVersion with path/preview overlays | VERIFIED |
| b4b62434 | perf(04-02): add dirty flag to skip redundant connection redraws | VERIFIED |

### Human Verification Required

### 1. Visual Connection Correctness During Animation

**Test:** Open sidepanel with a 20+ node tree. Expand and collapse nodes.
**Expected:** Connections animate correctly, no visual glitches, no missing or stale connections.
**Why human:** Visual animation correctness cannot be verified programmatically.

### 2. Path Highlight Updates on Navigation

**Test:** Navigate between different nodes in the tree.
**Expected:** Path highlight (root to current node) updates immediately to reflect the new path.
**Why human:** Requires observing visual path highlighting behavior in real-time.

### 3. Drag Reparent Preview Edge

**Test:** Drag a node to reparent it. Hover over potential parent nodes.
**Expected:** Preview edge appears/disappears cleanly, original connection is hidden during drag.
**Why human:** Drag interaction + visual preview requires manual interaction.

### 4. Layout Switch Full Redraw

**Test:** Switch between tree, mindmap, and radial layouts.
**Expected:** All connections fully redraw with correct geometry for the new layout mode.
**Why human:** Layout-dependent connection geometry is visual.

### 5. Connection Performance During Animation

**Test:** Run `window.__graphMetrics()` in console during expand/collapse animation on a 500-node tree.
**Expected:** `updateConnections` p50 time < 1ms (was ~5-10ms pre-optimization).
**Why human:** Requires runtime profiling in browser.

### Gaps Summary

No gaps found. All seven observable truths are verified through code analysis. All three requirement IDs (CONN-01, CONN-02, CONN-03) are satisfied. Both commits exist in the repository. TypeScript compiles cleanly with no errors. No anti-patterns detected.

The phase goal -- "Cache connection geometry by topology/layout signature. Path highlight and preview edge updated independently from base connections" -- is fully achieved in the codebase.

---

_Verified: 2026-03-19T12:00:00Z_
_Verifier: Claude (gsd-verifier)_
