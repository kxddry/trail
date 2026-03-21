---
phase: quick
plan: 260319-3vm
subsystem: graph-perf
tags: [performance, gestures, pan, zoom, hover, prefetch, zustand, react]
dependency_graph:
  requires: []
  provides: [gesture-deferred-store-writes, hover-debounce, gesture-quality-degradation, graphcanvas-chunk-prefetch]
  affects: [useGraphView.ts, GraphCanvas.tsx, GraphArea.tsx, graph-canvas-types.ts]
tech_stack:
  added: []
  patterns: [wheel-idle-timer, gesture-idle-timer, debounced-store-write, module-level-prefetch]
key_files:
  created: []
  modified:
    - src/entrypoints/sidepanel/ui/components/graph/useGraphView.ts
    - src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx
    - src/entrypoints/sidepanel/ui/components/graph/GraphArea.tsx
    - src/entrypoints/sidepanel/ui/components/graph/graph-canvas-types.ts
decisions:
  - "Wheel-idle timer at 150ms for store commit rather than per-frame, preserving renderer/grid updates every frame"
  - "Gesture-idle timer at 200ms for quality restoration separate from store commit to avoid race"
  - "Hover debounce 80ms writes to store but renderer gets immediate update via setHoverNodeId ref path"
  - "pendingIsGestureRef tracks gesture batch across RAF boundary so batched calls don't accidentally flush to store"
  - "Module-level prefetch of GraphCanvas chunk leverages browser dedup of identical import() specifiers"
metrics:
  duration: "~25min"
  completed: "2026-03-19"
  tasks: 2
  files: 4
---

# Phase quick Plan 260319-3vm: Graph Gesture Responsiveness and Open Performance Summary

**One-liner:** Deferred Zustand view writes to gesture-end/wheel-idle, 80ms hover debounce, gesture-active quality degradation to low/simplified, and module-load GraphCanvas chunk prefetch.

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | Local camera state + hover debounce + gesture quality | f9d4aa01 | useGraphView.ts, GraphCanvas.tsx, GraphArea.tsx, graph-canvas-types.ts |
| 2 | Prefetch GraphCanvas chunk ahead of first graph open | f9d4aa01 | GraphArea.tsx |

## What Was Built

### Task 1A: Local camera state during pan/zoom (useGraphView.ts)

`scheduleGraphView` now accepts an `isGesture` parameter (default false). When true:
- The Zustand write (`onGraphViewChange`) is suppressed in the RAF callback
- A 150ms wheel-idle `setTimeout` is set; on expiry it calls `commitViewToStore()`
- On `pointerUp`, `commitViewOnGestureEnd()` is called from GraphCanvas, which cancels the wheel-idle timer and immediately commits
- A 200ms gesture-idle timer fires `setGestureActiveState(false)` to restore quality

The renderer and grid transform still update every RAF frame — only the Zustand write is deferred. `pendingIsGestureRef` tracks whether any call in the current pending RAF batch was a gesture, so batched non-gesture + gesture calls correctly suppress the store write.

On unmount, any uncommitted view delta (viewRef vs lastCommittedViewRef) is flushed to the store.

### Task 1B: Hover debounce (GraphCanvas.tsx)

In `handlePointerMove`, on hover node change:
- `rendererRef.current?.setHoverNodeId(hitNodeId)` is called immediately for zero-latency visual feedback
- `onSetHoverNodeId(hitNodeId)` (Zustand write) is deferred 80ms via `hoverDebounceRef`

On `onPointerLeave`, the debounce is cancelled and both renderer + store receive `null` immediately, ensuring cursor/hover visuals reset without delay.

Debounce timer is cleaned up on renderer destroy (component unmount).

### Task 1C: Gesture-aware quality degradation (GraphArea.tsx + graph-canvas-types.ts)

- `onGestureActiveChange?: (active: boolean) => void` prop added to `GraphCanvasProps`
- `GraphCanvas` manages local `gestureActive` state (driven by `useGraphView`), and propagates changes to parent via `onGestureActiveChange` in a `useEffect`
- `GraphArea` tracks `gestureActive` in `useState`, passed as `onGestureActiveChange={handleGestureActiveChange}`
- Quality derivation updated: `gestureActive` forces `detailMode='low'` and `connectionQuality='simplified'`, sitting between overlay LOD (highest priority) and adaptive performance

### Task 2: GraphCanvas chunk prefetch (GraphArea.tsx)

Added module-level `import('./GraphCanvas.js')` immediately after the `React.lazy` declaration. The browser module cache deduplicates this with the lazy import, meaning the chunk is fetched at sidepanel boot instead of on first Suspense render.

## Deviations from Plan

None — plan executed exactly as written.

## Success Criteria Verification

- Zero Zustand view writes during active pan/zoom gestures: confirmed (only on pointerUp via `commitViewOnGestureEnd` or 150ms wheel-idle)
- Hover store writes debounced to at most 1 per 80ms: confirmed (hoverDebounceRef with 80ms timeout)
- Detail mode degrades to 'low' during gestures, restores after 200ms idle: confirmed (gestureActive state + quality derivation in GraphArea)
- GraphCanvas chunk prefetched at module load time: confirmed (module-level import() in GraphArea.tsx)
- TypeScript compiles with no errors: confirmed (npx tsc --noEmit passes cleanly)

## Self-Check: PASSED

- `src/entrypoints/sidepanel/ui/components/graph/useGraphView.ts` — modified, verified
- `src/entrypoints/sidepanel/ui/components/graph/GraphCanvas.tsx` — modified, verified
- `src/entrypoints/sidepanel/ui/components/graph/GraphArea.tsx` — modified, verified
- `src/entrypoints/sidepanel/ui/components/graph/graph-canvas-types.ts` — modified, verified
- Commit f9d4aa01 — confirmed present
